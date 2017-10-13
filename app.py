#!/usr/bin/env python

from flask import Flask, render_template, request, flash, session, url_for, redirect
from functools import wraps
from flaskext.mysql import MySQL
from models import db, User
from forms import SignupForm, SigninForm
from flask_wtf.csrf import CSRFProtect

# Create application object

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)


# VERY BAD. FIX THIS LATER, need random key generator. Also separate config file...
app.secret_key = "secret key"	# need secret key for sessions to work properly


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
   
  if request.method == 'POST':
    if form.validate() == False:	
      print form.lastname.data
      print form.firstname.data
      print form.email.data
      print form.password.data
      print form.data
      return render_template('signup.html', form=form)

    else:

      print "here!"
      newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)

      db.session.commit()
      print "comiited to database"
      session['email'] = newuser.email
      return redirect(url_for('profile'))
   
  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/profile')
def profile():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
 
  user = User.query.filter_by(email = session['email']).first()
 
  if user is None:
    return redirect(url_for('signin'))
  else:
    return render_template('profile.html')


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
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))
                 
  elif request.method == 'GET':
    return render_template('signin.html', form=form)

# TODO link the logout to the logout button?
@app.route('/signout')
def signout():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
     
  session.pop('email', None)
  return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=False)
