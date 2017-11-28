#!/usr/bin/env python
from flask import render_template, request, flash, session, url_for, redirect, \
                  Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from functools import wraps
#from app import db, app, gmaps
from app import db, app

from forms import SignupForm, SigninForm, ContactForm, SellerForm, UpdateProfileForm, \
                  UpdateParkingSpotForm, MessageForm, ApprovalForm, BuyerForm
from models import User, Parking_Spot, Message
import googlemaps
import json

gmaps = googlemaps.Client(key='AIzaSyA3puSdjsWawVHB0LxKU7dk9s9bzHHteGU')
# define the blueprint: 'parq', set url prefix: app.url/parq
#app = Blueprint('parq', __name__, url_prefix='/parq')

###################
# Helper Functions
###################

def validate_address(val_address, gmaps):
  """ Uses google maps api to see if inserted address is valid or not """ 
  response = gmaps.geocode(val_address)
  
  if len(response) == 0 or ('partial_match' in response[0].keys() and response[0]['partial_match'] == True):
    return False
  else:
    coordinates = [response[0]['geometry']['location']['lat'], response[0]['geometry']['location']['lng']]
    full_place_name = str(response[0]['formatted_address'])

    return (full_place_name, coordinates)

def parse_valid_data(val_add):
    """ Processes the validated address and returns its parsed parts""" 
    val_add1 = val_add[0]
    val_add2 = val_add1.split(",")
    valid_address = val_add2[0]
    valid_city = val_add2[1]
    val_add3 = val_add2[2].split(" ")
    valid_state = val_add3[1]
    valid_zipcode = int(val_add3[2])
    val_location = val_add[1]
    valid_latitude = float(val_location[0])
    valid_longitude = float(val_location[1]) 

    return (valid_address, valid_city, valid_state, valid_zipcode, valid_latitude, valid_longitude)

def parse_search_query(query):
  query = query.split('%')
  lat_lon = (float(query[0]), float(query[1]))
  zipcode = int(query[2])
  search_add = str(query[3])
 
  return (lat_lon, zipcode, search_add)


def get_mapbox_features(parking_spots, lat_long, val_add):
  feat_dict  = {}  
  features =[]
  center = [lat_long[1], lat_long[0]]

  for spot in parking_spots:
    if spot.address not in feat_dict.keys():
      feat_dict[spot.address] = []
      feature = {}
      feature['type'] = 'Feature'
      
      feature['geometry'] = {}
      feature['geometry']['type'] = 'Point'

      feature['properties'] = {}
      feature['properties']['icon'] = 'circle'
      feature['geometry']['coordinates'] = [float(spot.lon), float(spot.lat)]
      feature['properties']['description'] = "<strong><li style=\"color:black\">"+ "Parking Spot : "+ str(spot.psid) +"</li></strong><p><a href=\"message/"+str(spot.psid)+"\" target=\"_blank\" title=\"Opens in a new window\">"+ spot.address + ", " + spot.city + ", " + spot.state + " " + str(spot.zipcode)+ "  :  " + spot.ps_size+  "</a></p>"

      feat_dict[spot.address].append(feature)
    else :
      feature = {}
      feature['type'] = 'Feature'
      
      feature['geometry'] = {}
      feature['geometry']['type'] = 'Point'

      feature['properties'] = {}
      feature['properties']['icon'] = 'circle'
      feature['geometry']['coordinates'] = [float(spot.lon), float(spot.lat)]
      feature['properties']['description'] = "<strong><li style=\"color:black\">"+ "Parking Spot : "+ str(spot.psid) +"</li></strong><p><a href=\"message/"+str(spot.psid)+"\" target=\"_blank\" title=\"Opens in a new window\">"+ spot.address + ", " + spot.city + ", " + spot.state + " " + str(spot.zipcode)+ "  :  " + spot.ps_size+  "</a></p>"

      feat_dict[spot.address].append(feature)

  feature = {}
  feature['type'] = 'Feature'
  
  feature['geometry'] = {}
  feature['geometry']['type'] = 'Point'

  feature['properties'] = {}
  feature['properties']['icon'] = 'harbor'
  feature['geometry']['coordinates'] = [lat_long[1], lat_long[0]]
  feature['properties']['description'] = "<strong><li style=\"color:black\">Requested Position</li></strong><p><a>"+ val_add[0] +  "</a></p>"

  if val_add[0].split(",")[0] in feat_dict.keys():
    feat_dict[val_add[0].split(",")[0]] = [feature] + feat_dict[val_add[0].split(",")[0]]

  for spot in feat_dict.keys():
    desc = ""
    for sub_spot in feat_dict[spot]:
      desc = desc + sub_spot['properties']['description']

    feat_dict[spot][0]['properties']['description'] = desc

    features.append(feat_dict[spot][0])

  return center, features

###################
# Routes
###################

@app.route('/')
def home():
  if current_user.is_authenticated:
    user = current_user
    return render_template('profile.html',name=user.firstname + " " + user.lastname)
  return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm(request.form)
     
  if request.method == 'POST':

    if form.validate() == False:	
      return render_template('signup.html', form=form)

    else:
      newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)

      db.session.commit()
      flash('Registration successful')
      return redirect(url_for('login'))
   
  elif request.method == 'GET':
    return render_template('signup.html', form=form)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
  user = current_user
  return render_template('profile.html', name=user.firstname + " " + user.lastname)


@app.route('/messagepage')
@login_required
def message_page():
  user = current_user
  #my_messages = user.get_all_messages()
  my_messages = user.get_my_messages_by_expiry_status(expired = 0)
  return render_template('messagepage.html', my_messages=my_messages, get_user=User.get_user_name)

# Check to see if user can see other people's messages...
@app.route('/view_message/<message_id>', methods =['GET', 'POST'])
@login_required
def view_message(message_id):
    form = ApprovalForm()
    message = Message.get_message_by_id(message_id)

    if request.method == 'POST':
      message.approved = 1

      # Mark the parking spot as taken
      parking_spot = Parking_Spot.get_parking_spot_by_id(message.psid)
      parking_spot.availible = 0

      db.session.commit()
      return redirect(url_for('profile')) 

    # Messages that are already approved should not have the approved field
    if message.approved: 
      return render_template('view_message.html', form=None, message=message, get_user=User.get_user_name)
    
    return render_template('view_message.html', form=form, message=message, get_user=User.get_user_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = SigninForm()
     
  if request.method == 'POST':
    # if this doesn't work change back to just validate()
    if form.validate_on_submit(): 
      user = User.get_user(form.email.data)

      # Check if user exists and the password is correct
      if user is not None and user.is_correct_password(form.password.data):
        # Logs the user in authenticates him/her
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('profile'))
      else: 
        flash('Error! Incorrect login credentials.', 'error')
  return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
  user = current_user
  user.authenticated = False
  db.session.add(user)
  db.session.commit()
  logout_user()
  return redirect(url_for('home'))


# TODO Alter this to show the results of the search.
@app.route('/buyer_search_results/<query>')
@login_required
def buyer_search_results(query):
  user = current_user
  uid = user.uid

  # Parse the query
  lat_lon, zipcode, search_add = parse_search_query(query)

  search_results = Parking_Spot.vicinity_search(lat_lon, zipcode, uid)
  if search_results:
    center, features = get_mapbox_features(search_results, lat_lon, search_add)
    features = json.dumps(features)
    center = json.dumps(center)


    return render_template('buyer_search_map.html', mapbox_features = features, map_center = center )

  # When none are found
  return render_template('buyer_search_results.html', spots=None)


@app.route('/buyer_search', methods=['GET', 'POST'])
@login_required
def buyer_search():
  form = BuyerForm(request.form)
     
  if request.method == 'POST':
    if form.validate() == False:  
      return render_template('buyer_search.html', form=form)

    val_address = form.address.data+","+form.city.data+","+form.state.data+" "+str(form.zipcode.data)
    val_add = validate_address(val_address, gmaps)

    if val_add:
      # Query is unicode. Need to format it in a parseable way
      lat_lon = tuple(val_add[1])
      query = str(lat_lon[0])+'%'+str(lat_lon[1])+'%'+str(form.zipcode.data)+'%'+str(val_add[0])
      


      #displaying results. 
      user = current_user
      uid = user.uid

      lat_lon, zipcode, search_add = parse_search_query(query)

      search_results = Parking_Spot.vicinity_search(lat_lon, zipcode, uid)
      if search_results:
        center, features = get_mapbox_features(search_results, lat_lon, search_add)
        features = json.dumps(features)
        center = json.dumps(center)

        return render_template('buyer_search_map.html', mapbox_features = features, map_center = center )

      # When none are found
      return render_template('buyer_search_results.html', spots=None)


      #return redirect(url_for('buyer_search_results', query=query))

    else:
      flash('Invalid Address')
      return render_template('buyer_search.html', form=form)    
    # print("Print here")
    # print(search_results)

  # GET request
  return render_template('buyer_search.html', form=form)

@app.route('/buyer_profile')
@login_required
def buyer_profile():
  user = current_user
  return render_template('buyer_profile.html')

@app.route('/requests')
@login_required
def requests():
  user = current_user
  unapproved_messages = user.get_my_messages_by_status(approved=0, expired = 0)

  if not unapproved_messages:
    flash('You have no pending requests!')
    return redirect(url_for('buyer_profile'))

  return render_template('requests.html', my_messages=unapproved_messages, get_user=User.get_user_name)

@app.route('/view_requests/<message_id>')
@login_required
def view_requests(message_id):
  # TODO: Check to see if a user can see other user's messages because of this query?
  message = Message.get_message_by_id_status(message_id, 0, 0)
  return render_template('view_requests.html', message=message, get_user=User.get_user_name)

@app.route('/approved_requests')
@login_required
def approved_requests():
  #form = ReleaseForm()
  user = current_user
  approved_messages = user.get_my_messages_by_status(approved=1, expired = 0)

  if not approved_messages:
    flash('You have no approved requests!')
    return redirect(url_for('buyer_profile'))

  # Get a list of the approved parking spots (psid)
  approved_spots = [a.psid for a in approved_messages]
  for i, psid in enumerate(approved_spots):
    approved_spots[i] = Parking_Spot.get_parking_spot_by_id(psid)

  return render_template('approved_requests.html', approved_spots=approved_spots, get_user=User.get_user_name)

@app.route('/view_approved_requests/<message_id>')
@login_required
def view_approved_requests(message_id):
  message = Message.get_message_by_id_status(message_id, 1, 0)
  return render_template('view_approved_requests.html', message=message, get_user=User.get_user_name)

@app.route('/release_spot/<parking_id>')
@login_required
def release_spot(parking_id):
  user = current_user
  parking_spot = Parking_Spot.get_parking_spot_by_id(parking_id)
  parking_spot.availible = 1
  db.session.commit()

  approved_messages = user.get_my_messages_by_status(approved=1, expired = 0)
  approved_message = [a for a in approved_messages if a.psid == parking_id]
  a.expired = True
  db.session.commit()
  return redirect(url_for('approved_requests'))



@app.route('/seller')
@login_required
def seller():
  return render_template('seller.html')

@app.route('/viewspots')
@login_required
def viewspots():
  user = current_user
  # A user's garage is a list containing his parking spots
  garage = user.get_all_parking_spots()
  return render_template('viewspots.html', garage=garage)

@app.route('/addspots',methods=['GET', 'POST'])
@login_required
def addspots():
  form = SellerForm(request.form)
     
  if request.method == 'POST':
    user = current_user
    uid = user.uid

    if form.validate(uid) == False:  
      return render_template('addspots.html', form=form)
    
    val_address = form.address.data+","+form.city.data+","+form.state.data+" "+str(form.zipcode.data)
    val_add = validate_address(val_address, gmaps)

    if val_add:
      valid_address, valid_city, valid_state, valid_zipcode, valid_latitude, \
      valid_longitude = parse_valid_data(val_add)

      parking_spot = Parking_Spot(uid, valid_address, valid_city, valid_state, valid_zipcode, form.ps_size.data, valid_latitude, valid_longitude)
    else:
      flash('Invalid Address')
      return render_template('addspots.html', form=form)    
  
    db.session.add(parking_spot)
    db.session.commit()

    return redirect(url_for('seller'))

  return render_template('addspots.html', form=form)


@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():
  form = UpdateProfileForm(request.form)

  if request.method == 'POST':
    user = current_user

    user.firstname = form.firstname.data.title()
    user.lastname = form.lastname.data.title()
    db.session.commit()
    return redirect(url_for('profile'))

  # GET Method
  return render_template('updateprofile.html', form=form)

@app.route('/parking/<parking_id>')
@login_required
def parking(parking_id):
  user = current_user
  parking_spot = Parking_Spot.get_user_parking_spot_by_id(parking_id, user.uid)
  return render_template('parking.html', parking_spot=parking_spot)

@app.route('/message/<parking_id>', methods=['GET', 'POST'])
@login_required
def message(parking_id):
  form = MessageForm(request.form) 
  user = current_user

  # Get the information related to this parking spot
  parking_spot = Parking_Spot.get_parking_spot_by_id(parking_id)

  if request.method == 'POST':
    message = Message(user.uid, parking_spot.ownerid, parking_spot.psid, form.message.data)
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('profile'))

  return render_template('message.html', parking_spot=parking_spot, form=form)

@app.route('/delete_spot/<parking_id>')
@login_required
def delete_spot(parking_id):
  user = current_user
  parking_spot = Parking_Spot.get_user_parking_spot_by_id(parking_id, user.uid)

  # Deletes by simply setting the validity to zero
  parking_spot.validity = 0
  db.session.commit()
  return render_template('delete_spot.html', parking_spot=parking_spot)

@app.route('/update_spot/<parking_id>', methods=['GET', 'POST'])
@login_required
def update_spot(parking_id):
  form = UpdateParkingSpotForm(request.form)  

  user = current_user
  parking_spot = Parking_Spot.get_user_parking_spot_by_id(parking_id, user.uid)

  if request.method == 'POST':
    val_address = form.address.data+","+form.city.data+","+form.state.data+" "+str(form.zipcode.data)
    val_add = validate_address(val_address, gmaps)
    if val_add:
      valid_address, valid_city, valid_state, valid_zipcode, valid_latitude, \
      valid_longitude = parse_valid_data(val_add)
    else:
      flash('Invalid Address')
      return render_template('update_spot.html', parking_spot=parking_spot, form=form)

    parking_spot.address = valid_address
    parking_spot.city = valid_city
    parking_spot.state = valid_state
    parking_spot.zipcode = valid_zipcode
    parking_spot.size = form.ps_size.data
    parking_spot.lat = valid_latitude
    parking_spot.lon = valid_longitude
    db.session.commit()

    return redirect(url_for('profile'))

  if parking_spot:
    return render_template('update_spot.html', parking_spot=parking_spot, form=form)
  return render_template('notallowed.html')
