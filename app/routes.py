#!/usr/bin/env python
import googlemaps
from haversine import haversine
import os
import jellyfish as jf
from flask import render_template, request, flash, session, url_for, redirect, \
                  Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from functools import wraps
from app import db, app
from forms import SignupForm, SigninForm, ContactForm, SellerForm, UpdateProfileForm, \
                  UpdateParkingSpotForm, MessageForm, ApprovalForm, BuyerForm
from models import User, Parking_Spot, Message
import json 
gmaps = googlemaps.Client(key='AIzaSyA3puSdjsWawVHB0LxKU7dk9s9bzHHteGU')

# define the blueprint: 'parq', set url prefix: app.url/parq
#app = Blueprint('parq', __name__, url_prefix='/parq')

@app.route('/')
def home():
  if current_user.is_authenticated:
    user = current_user
    return render_template('profile.html',name=user.firstname + " " + user.lastname)
  return render_template('index.html')

# TODO signup method not allowed
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
  my_messages = user.get_messages()
  return render_template('messagepage.html', my_messages=my_messages, get_user=User.get_user_name)

@app.route('/view_message/<message_id>', methods =['GET', 'POST'])
@login_required
def view_message(message_id):
    form = ApprovalForm()
    message = Message.query.filter_by(message_id=message_id).first()
    
    if request.method == 'POST':
      message.approved = 1
      db.session.commit()
      return redirect(url_for('profile')) 

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


@app.route('/buyer')
@login_required
def buyer():
  user = current_user
  uid = user.uid
  #allspots = Parking_Spot.query.filter(Parking_Spot.ownerid != uid, Parking_Spot.validity == 1).all()
  allspots = Parking_Spot.query.filter(Parking_Spot.validity == 1).all()
  new_spots = get_closest(lat_long, allspots)
  allspots = new_spots

  return render_template('buyer.html', allspots=allspots)

def get_mapbox_features(parking_spots):
  features =[]

  for spot in parking_spots:
    feature = {}
    feature['type'] = 'Feature'
    
    feature['geometry'] = {}
    feature['geometry']['type'] = 'Point'

    feature['properties'] = {}
    feature['properties']['icon'] = 'circle'
    feature['geometry']['coordinates'] = [float(spot.lon), float(spot.lat)]
    feature['properties']['description'] = "<strong>"+ "Parking Spot : "+ str(spot.psid) +"</strong><p><a href=\"message/"+str(spot.psid)+"\" target=\"_blank\" title=\"Opens in a new window\">"+ spot.address + ", " + spot.city + ", " + spot.state + " " + str(spot.zipcode)+ "  :  " + spot.ps_size+  "</a></p>"

    features.append(feature)

  return features


@app.route('/buyer_search',methods=['GET', 'POST'])
@login_required
def buyer_search():
  form = BuyerForm(request.form)
     
  if request.method == 'POST':
    user = current_user
    uid = user.uid

    if form.validate(uid) == False:  
      return render_template('buyer_search.html', form=form)
    
    val_address = form.address.data+","+form.city.data+","+form.state.data+" "+str(form.zipcode.data)
    if validate_address(val_address, gmaps):
      val_add = validate_address(val_address, gmaps)
      lat_long = tuple(val_add[1])
    else:
      flash('Invalid Address')
      return render_template('buyer_search.html', form=form)    

    allspots = Parking_Spot.query.filter(Parking_Spot.validity == 1, Parking_Spot.ownerid != uid).all()
    new_spots = get_closest(lat_long, allspots)
    allspots = new_spots
    
    features = get_mapbox_features(allspots)

    feature = {}
    feature['type'] = 'Feature'
    
    feature['geometry'] = {}
    feature['geometry']['type'] = 'Point'

    feature['properties'] = {}
    feature['properties']['icon'] = 'harbor'
    feature['geometry']['coordinates'] = [lat_long[1], lat_long[0]]
    feature['properties']['description'] = "<strong>Requested Position</strong><p><a>"+ val_add[0] +  "</a></p>"

    features = [feature] + features

    center = features[0]['geometry']['coordinates']
    features = json.dumps(features)
    center = json.dumps(center)


    return render_template('buyer.html',  mapbox_features = features, map_center = center )

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
  #my_messages = user.get_messages()
  unapproved_messages = Message.query.filter_by(sender_uid=user.uid, approved=0).all()
  if not unapproved_messages:
    flash('You have no pending requests!')
    return redirect(url_for('buyer_profile'))

  return render_template('requests.html', my_messages=unapproved_messages, get_user=User.get_user_name)

@app.route('/view_requests/<message_id>')
@login_required
def view_requests(message_id):
  message = Message.query.filter_by(message_id=message_id, approved=0).first()
  return render_template('view_requests.html', message=message, get_user=User.get_user_name)



@app.route('/approved_requests')
@login_required
def approved_requests():

  user = current_user
  #my_messages = user.get_messages()
  approved_messages = Message.query.filter_by(sender_uid=user.uid, approved=1).all()
  if not approved_messages:
    flash('You have no approved requests!')
    return redirect(url_for('buyer_profile'))

  return render_template('approved_requests.html', my_messages=approved_messages, get_user=User.get_user_name)

@app.route('/view_approved_requests/<message_id>')
@login_required
def view_approved_requests(message_id):
  message = Message.query.filter_by(message_id=message_id, approved=1).first()
  return render_template('view_approved_requests.html', message=message, get_user=User.get_user_name)




@app.route('/seller')
@login_required
def seller():
  return render_template('seller.html')


@app.route('/viewspots')
@login_required
def viewspots():
  user = current_user
  uid = user.uid
  # A user's garage is a list containing his parking spots
  garage = Parking_Spot.query.filter_by(ownerid = uid, validity=1).all()
  return render_template('viewspots.html', garage=garage)

def validate_address(val_address, gmaps):
  response = gmaps.geocode(val_address)
  #print response
  if len(response) == 0 or ('partial_match' in response[0].keys() and response[0]['partial_match'] == True) :
    return False
  else:
    coordinates = [response[0]['geometry']['location']['lat'], response[0]['geometry']['location']['lng']]
    full_place_name = str(response[0]['formatted_address'])

    return (full_place_name, coordinates)


def get_closest(coordinates, parking_spots, radius = 1.0):
  new_spots = []

  for spot in parking_spots:

    if haversine(coordinates,(float(spot.lat),float(spot.lon))) <= radius:
      new_spots.append(spot)

  
  return new_spots




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
    if validate_address(val_address, gmaps):
      val_add = validate_address(val_address, gmaps)
      val_add1 = val_add[0]
      val_add2 = val_add1.split(",")
      valid_address = val_add2[0]
      valid_city = val_add2[1]
      val_add3 = val_add2[2].split(" ")
      valid_state = val_add3[1]
      valid_zipcode = int(val_add3[2])
      val_location = val_add[1]
      valid_latitude = val_location[0]
      valid_longitude = val_location[1] 
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
  parking_spot = Parking_Spot.query.filter_by(psid=parking_id, ownerid=user.uid).first()
  return render_template('parking.html', parking_spot=parking_spot)

@app.route('/message/<parking_id>', methods=['GET', 'POST'])
@login_required
def message(parking_id):
  form = MessageForm(request.form) 
  user = current_user
  parking_spot = Parking_Spot.query.filter_by(psid=parking_id).first()
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
  parking_spot = Parking_Spot.query.filter_by(psid=parking_id, ownerid=user.uid).first()
  parking_spot.validity = 0
  db.session.commit()
  return render_template('delete_spot.html', parking_spot=parking_spot)

@app.route('/update_spot/<parking_id>', methods=['GET', 'POST'])
@login_required
def update_spot(parking_id):
  form = UpdateParkingSpotForm(request.form)  

  user = current_user
  parking_spot = Parking_Spot.query.filter_by(psid=parking_id, ownerid=user.uid).first()

  if request.method == 'POST':
    val_address = form.address.data+","+form.city.data+","+form.state.data+" "+str(form.zipcode.data)
    if validate_address(val_address, gmaps):
      val_add = validate_address(val_address, gmaps)
      val_add1 = val_add[0]
      val_add2 = val_add1.split(",")
      valid_address = val_add2[0]
      valid_city = val_add2[1]
      val_add3 = val_add2[2].split(" ")
      valid_state = val_add3[1]
      valid_zipcode = int(val_add3[2])
      val_location = val_add[1]
      valid_latitude = val_location[0]
      valid_longitude = val_location[1] 
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


