#!/usr/bin/env python

from flask import render_template, request, flash, session, url_for, redirect, \
                  Blueprint

from functools import wraps
from app import db, app
from forms import SignupForm, SigninForm, ContactForm, SellerForm, UpdateProfileForm
from models import User, Parking_Spot

# define the blueprint: 'parq', set url prefix: app.url/parq
#app = Blueprint('parq', __name__, url_prefix='/parq')

# Login required
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Login required.')
			return redirect(url_for('signin'))
	return wrap

@app.route('/')
@login_required
def home():
  return render_template('index.html')

@app.route('/welcome')
@login_required
def welcome():
  return render_template('welcome.html')

# TODO signup method not allowed
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm(request.form)
   
  if 'email' in session:
    return redirect(url_for('profile')) 
     
  if request.method == 'POST':

    if form.validate() == False:	
      return render_template('signup.html', form=form)

    else:
      newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)

      db.session.commit()

      session['email'] = newuser.email
      return redirect(url_for('profile'))
   
  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
 
  user = User.query.filter_by(email = session['email']).first()
 
  if user is None:
    return redirect(url_for('signin'))

  return render_template('profile.html', name=user.firstname + " " + user.lastname)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  
  if request.method == 'POST':
    return 'Form posted.'
  
  elif request.method == 'GET':
    return render_template('contact.html', form=form)



@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()
  
  if 'email' in session:
    return redirect(url_for('profile'))
     
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))
                 
  elif request.method == 'GET':
    return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
     
  session.pop('email', None)
  return redirect(url_for('home'))


@app.route('/buyer')
def buyer():
  if 'email' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(email = session['email']).first()
  uid = user.uid

  allspots = Parking_Spot.query.order_by(Parking_Spot.city).all()
  
  return render_template('buyer.html', allspots=allspots)


@app.route('/seller')
def seller():
  if 'email' not in session:
    return redirect(url_for('signin'))
  return render_template('seller.html')


@app.route('/viewspots')
def viewspots():
  if 'email' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(email = session['email']).first()
  uid = user.uid

  # A user's garage is a list containing his parking spots
  garage = Parking_Spot.query.filter_by(ownerid = uid).all()

  return render_template('viewspots.html', garage=garage)


@app.route('/addspots',methods=['GET', 'POST'])
def addspots():
  form = SellerForm(request.form)
   
  if 'email' not in session:
    return redirect(url_for('signin')) 
     
  if request.method == 'POST':
    user = User.query.filter_by(email = session['email']).first()
    uid = user.uid

    if form.validate(uid) == False:  
      return render_template('addspots.html', form=form)
    
    parking_spot = Parking_Spot(uid, form.address.data, form.city.data, form.state.data, form.zipcode.data, form.ps_size.data)
    
    db.session.add(parking_spot)

    db.session.commit()
    return redirect(url_for('seller'))

  return render_template('addspots.html', form=form)


@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
  form = UpdateProfileForm(request.form)

  if 'email' not in session:
    return redirect(url_for('signin'))

  if request.method == 'POST':
    user = User.query.filter_by(email=session['email']).first()

    user.firstname = form.firstname.data.title()
    user.lastname = form.lastname.data.title()
    db.session.commit()

    return redirect(url_for('profile'))

  # GET Method
  return render_template('updateprofile.html', form = form)

# if __name__ == '__main__':
#     app.run(debug=False)

