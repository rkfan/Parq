# tests/test_user.py
 
import unittest
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User
from werkzeug import generate_password_hash, check_password_hash

""" Tests User functionality"""
class ParqTestUserFunctionality(BaseTestCase):
	########################
	#### Tests          ####
	########################

	def test_valid_user_registration(self):
		""" Tests that user can register """ 
		with self.client:
			response = self.register('patrick', 'kennedy', 'patkennedy79@gmail.com', 'FlaskIsAwesome')
			self.assertIn(b'/login', request.url)
			self.assertIn(b'Registration successful', response.data)

			# See if user stored in database
			user = User.query.filter_by(email='patkennedy79@gmail.com').first()
			self.assertTrue(str(user) == 'User {0} {1} with email: {2}'.format(user.firstname, user.lastname, user.email))

	def test_incorrect_user_registration(self):
		""" Tests that user cannot register with existing email """ 
		with self.client:
			response = self.register('testurrr', 'teetee', 'test@tester.com', 'duplicate')
			self.assertIn(b'That email is already taken', response.data)
			self.assertIn(b'/signup', request.url)
			self.assertTrue(User.user_email_taken('test@tester.com') == True)

	def test_get_by_id(self):
		""" Tests that id is correct for currently logged in user """
		with self.client:
			self.login('test@tester.com', 'test')
			test_user = self.get_test_acc()
			self.assertTrue(current_user.uid == test_user.get_id())
			self.assertFalse(current_user.uid == test_user.get_id() + 1)

	def test_get_user_by_email(self):
		""" Tests the get_user method of User model """ 
		# Non existing email
		self.assertEqual(User.get_user('nonexisting@gmail.com'), None)
		
		with self.client:
			# Existing email of logged in user
			self.login('test@tester.com', 'test')
			self.assertEqual(current_user, User.get_user(current_user.email))

	def test_check_password(self):
		""" Tests password is correct after hashing """ 
		test_user = self.get_test_acc()
		pass_hash = test_user.pwdhash
		self.assertTrue(check_password_hash(pass_hash, 'test'))
		self.assertFalse(check_password_hash(pass_hash, 'TeSt'))

	def test_update_profile(self):
		""" Tests to see that the user can update their profile """ 
		self.assertLoginReq('/updateprofile')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.post('/updateprofile', data=dict(firstname='Adam', lastname='Admin'), 
				follow_redirects=True)
			self.assertIn(b'/profile', request.url)
			self.assertIn(b'This is Adam Admin\'s profile page', response.data)
			self.assertIn(b'buyer', response.data)
			self.assertIn(b'seller', response.data)
			self.assertIn(b'Update Profile', response.data)
	    

class UserViewsTests(BaseTestCase):
	########################
	#### Tests 			####
	########################

	def test_profile_view(self):
		""" Tests to see if the user can see his/her respective profile """ 
		self.assertLoginReq('/profile')

		with self.client:
			response = self.login('test@tester.com', 'test')
			self.assertIn(b'Profile', response.data)
			self.assertIn(b'This is Test Tester\'s profile page', response.data)
			self.assertIn(b'buyer', response.data)
			self.assertIn(b'seller', response.data)
			self.assertIn(b'Update Profile', response.data)

	def test_seller_view(self):
		""" Tests to see that the user can see the seller page if logged in """
		self.assertLoginReq('/seller')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/seller')
			self.assertTrue(response.status_code, 200)
			self.assertIn(b'This is Test Tester\'s seller page', response.data)
			self.assertIn(b'My Garage', response.data)
			self.assertIn(b'Add Parking Space', response.data)

class UserLoginLogoutTests(BaseTestCase):
	########################
	#### helper methods ####
	########################

	def logout(self):
		""" Logs out the user """ 
		return self.client.get('/logout', follow_redirects=True)

	########################
	#### Tests 			####
	########################

	def test_login_page_loads(self):
		""" Tests to see that the login page can load """ 
		response = self.client.get('/login')
		self.assertTrue(response.status_code, 200)
		self.assertIn(b'Sign In', response.data)

	def test_correct_login(self):
		""" Tests to see if a user can log in correctly """ 
		with self.client:
			response = self.login('test@tester.com', 'test')
			self.assertIn(b'/profile', request.url)
			self.assertTrue(current_user.is_active)
			self.assertTrue(current_user.is_authenticated)

			# Test to see that authenticated index brings you to profile page
			response = self.client.get('/', content_type='html/text', follow_redirects=True)
			self.assertEqual(response.status_code, 200)
			self.assertIn(b'Profile', response.data)
			self.assertIn(b'This is Test Tester\'s profile page', response.data)
			

	def test_incorrect_login(self):
		""" Tests to see that user with invalid credentials will not be able to log in """ 
		with self.client:
			response = self.login('test@tester.com', 'WRONG')
			self.assertFalse(current_user.is_authenticated)
			self.assertIn(b'/login', request.url)
			self.assertIn(b'Invalid e-mail or password', response.data)

	def test_blank_login(self):
		""" Tests to see correct output if user enters blank password and malformed email"""
		with self.client:
			response = self.login('', '')
			self.assertFalse(current_user.is_authenticated)
			self.assertIn(b'Please enter your email address.', response.data)
			self.assertIn(b'Please enter a password.', response.data)

	def test_logout(self):
		""" Tests to see if logout is working correctly """ 
		with self.client:
			response = self.login('test@tester.com', 'test')
			response = self.logout()
			self.assertIn(b'Please signup or login.', response.data)
			self.assertFalse(current_user.is_active)

		# Check that User isn't authenticated
		test_user = self.get_test_acc()
		self.assertFalse(test_user.authenticated)

	def test_logout_route_requires_login(self):
		""" Tests to see that you have to be logged in to logout """ 
		self.assertLoginReq('/logout')

if __name__ == '__main__':
	unittest.main()