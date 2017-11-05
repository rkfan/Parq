# tests/test_user.py
 
import unittest
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User
from werkzeug import generate_password_hash, check_password_hash

""" Tests User functionality"""
class ParqTestUser(BaseTestCase):
	########################
	#### helper methods ####
	########################
	def register(self, fname, lname, email, password):
	    return self.client.post(
	        '/signup',
	        data=dict(firstname=fname, lastname=lname, email=email, password=password),
	        follow_redirects=True
	    )

	########################
	#### Tests          ####
	########################

	def test_valid_user_registration(self):
		""" Tests that user can register """ 
		with self.client:
			response = self.register('patrick', 'kennedy', 'patkennedy79@gmail.com', 'FlaskIsAwesome')
			self.assertEqual(response.status_code, 200)
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

	def test_check_password(self):
		""" Tests password is correct after hashing """ 
		test_user = self.get_test_acc()
		pass_hash = test_user.pwdhash
		self.assertTrue(check_password_hash(pass_hash, 'test'))
		self.assertFalse(check_password_hash(pass_hash, 'TeSt'))

class UserViewsTests(BaseTestCase):
	########################
	#### helper methods ####
	########################

	def logout(self):
	    return self.client.get('/logout', follow_redirects=True)

	########################
	#### Tests 			####
	########################

	def test_login_page_loads(self):
		response = self.client.get('/login')
		self.assertIn(b'Sign In', response.data)

	def test_correct_login(self):
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
		with self.client:
			response = self.login('test@tester.com', 'WRONG')
			self.assertFalse(current_user.is_authenticated)
			self.assertIn(b'/login', request.url)

	def test_logout(self):
		with self.client:
			response = self.login('test@tester.com', 'test')
			response = self.logout()
			self.assertIn(b'Please signup or login.', response.data)
			self.assertFalse(current_user.is_active)

		# User isn't authenticated
		test_user = self.get_test_acc()
		self.assertFalse(test_user.authenticated)


	def test_profile_view(self):
		self.assertLoginReq('/profile')

		response = self.login('test@tester.com', 'test')
		self.assertIn(b'Profile', response.data)
		self.assertIn(b'This is Test Tester\'s profile page', response.data)
		self.assertIn(b'buyer', response.data)
		self.assertIn(b'seller', response.data)
		self.assertIn(b'Update Profile', response.data)

	def test_logout_route_requires_login(self):
		self.assertLoginReq('/logout')

	# Test individual pages without login first (can't get access)

if __name__ == '__main__':
	unittest.main()