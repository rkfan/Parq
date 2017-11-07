#!/usr/bin/env python

from flask import render_template, request, flash, session, url_for, redirect, \
                  Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from functools import wraps
from app import db, app
from forms import SignupForm, SigninForm, ContactForm, SellerForm, UpdateProfileForm, \
                  UpdateParkingSpotForm
from models import User, Parking_Spot

# define the blueprint: 'parq', set url prefix: app.url/parq
#app = Blueprint('parq', __name__, url_prefix='/parq')

@app.route('/')
def home():
  if current_user.is_authenticated:
    return render_template('profile.html',name=current_user.firstname + " " + current_user.lastname)
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
  return render_template('profile.html', name=current_user.firstname + " " + current_user.lastname)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  
  if request.method == 'POST':
    return 'Form posted.'
  
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = SigninForm()
     
  if request.method == 'POST':
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
  allspots = Parking_Spot.get_all_spots()
  
  return render_template('buyer.html', allspots=allspots)

@app.route('/seller')
@login_required
def seller():
  return render_template('seller.html', name=current_user.firstname + " " + current_user.lastname)

@app.route('/viewspots')
@login_required
def viewspots():
  # A user's garage is a list containing his parking spots
  garage = current_user.get_all_parking_spots()
  return render_template('viewspots.html', garage=garage)


@app.route('/addspots',methods=['GET', 'POST'])
@login_required
def addspots():
  form = SellerForm(request.form)
     
  if request.method == 'POST':
    uid = current_user.uid

    if form.validate(uid) == False:  
      return render_template('addspots.html', form=form)
    
    parking_spot = Parking_Spot(uid, form.address.data, form.city.data, form.state.data, form.zipcode.data, form.ps_size.data)   
    db.session.add(parking_spot)
    db.session.commit()

    return redirect(url_for('seller'))

  return render_template('addspots.html', form=form)


@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():
  form = UpdateProfileForm(request.form)

  if request.method == 'POST':
    #user = current_user

    current_user.firstname = form.firstname.data.title()
    current_user.lastname = form.lastname.data.title()
    db.session.commit()

    return redirect(url_for('profile'))

  # GET Method
  return render_template('updateprofile.html', form=form)

@app.route('/parking/<parking_id>')
@login_required
def parking(parking_id):
  parking_spot = Parking_Spot.get_parking_spot_by_id(parking_id, current_user.uid)
  return render_template('parking.html', parking_spot=parking_spot)

@app.route('/delete_spot/<parking_id>')
#@login_required
def delete_spot(parking_id):
  parking_spot = Parking_Spot.get_parking_spot_by_id(parking_id, current_user.uid)
  parking_spot.validity = 0
  db.session.commit()

  return render_template('delete_spot.html', parking_spot=parking_spot)

@app.route('/update_spot/<parking_id>', methods=['GET', 'POST'])
@login_required
def update_spot(parking_id):
  form = UpdateParkingSpotForm(request.form)  

  # GET Method
  # Query for this parking spot
  parking_spot = Parking_Spot.get_parking_spot_by_id(parking_id, current_user.uid)

  if request.method == 'POST':
    parking_spot.address = form.address.data
    parking_spot.city = form.city.data
    parking_spot.state = form.state.data
    parking_spot.zipcode = form.zipcode.data
    parking_spot.size = form.ps_size.data
    db.session.commit()

    return redirect(url_for('profile'))

  if parking_spot:
    return render_template('update_spot.html', parking_spot=parking_spot, form=form)
  return render_template('notallowed.html')
