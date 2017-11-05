# tests/test_user.py
 
import unittest
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User

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
	 
	def login(self, email, password):
	    return self.client.post(
	        '/login',
	        data=dict(email=email, password=password),
	        follow_redirects=True
	    )
	 
	def logout(self):
	    return self.client.get('/logout', follow_redirects=True)
	    
	def test_valid_user_registration(self):
		""" Tests that user can register """ 
		with self.client:
			response = self.register('patrick', 'kennedy', 'patkennedy79@gmail.com', 'FlaskIsAwesome')
			self.assertEqual(response.status_code, 200)
			self.assertIn(b'/login', request.url)
			#print current_user.is_active()

			# See if user stored in database
			user = User.query.filter_by(email='patkennedy79@gmail.com').first()
			self.assertTrue(str(user) == 'User {0} {1} with email: {2}'.format(user.firstname, user.lastname, user.email))

	def test_incorrect_user_registration(self):
		""" Tests that user cannot register with existing email """ 
		with self.client:
			response = self.register('testurrr', 'teetee', 'test@tester.com', 'duplicate')
			self.assertIn(b'That email is already taken', response.data)
			self.assertIn(b'/signup', request.url)

	def test_get_by_id(self):
		""" Tests that id is correct for currently logged in user """
		pass

	def test_check_password(self):
		""" Tests password is correct after hashing """ 
		pass

class UserViewsTests(BaseTestCase):
	def test_login_page_loads(self):
		response = self.client.get('/login')
		self.assertIn(b'Sign In', response.data)

	def test_correct_login(self):
		pass

	def test_incorrect_login(self):
		pass

	def test_logout(self):
		pass

	def test_logout_route_requires_login(self):
		self.assertLoginReq('/logout')

	# Test individual pages without login first (can't get access)

if __name__ == '__main__':
	unittest.main()