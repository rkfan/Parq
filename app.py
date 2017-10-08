#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flaskext.mysql import MySQL

# Create application object

mysql = MySQL()

app = Flask(__name__)

# This configuration can change....local database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''	
app.config['MYSQL_DATABASE_DB'] = 'UserData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
 

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
			return redirect(url_for('login'))
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
@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		# admin, admin for now....
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from USER where Username='" + username + "' and Password='" + password + "'")
		data = cursor.fetchone()
		if data is None:
			error = 'Invalid credentials. Please try again.'
		else:
			session['logged_in'] = True
			flash('Logged in')
			return redirect(url_for('welcome'))	# Redirect to home

	return render_template('login.html', error=error)

# TODO link the logout to the logout button?
@app.route('/logout')
def logout():
	session.pop('logged_in', None)	# Pops the value of true for logged in
	flash('Logged out')
	return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
