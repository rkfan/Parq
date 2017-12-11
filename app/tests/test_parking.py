#test/test_parking.py

import unittest
from mock import MagicMock, patch
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User, Parking_Spot

valid_addr_tuple = ('1020 Bay Ridge Avenue, Brooklyn, NY 11219, USA', [40.627258, -74.010027])

class ParqSellerFunctTests(BaseTestCase):
	def test_see_garage(self):
		""" Tests to see that the tester's parking spots are listed """ 
		self.assertLoginReq('/viewspots')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/viewspots', follow_redirects=True)
			self.assertIn(b'2957 Broadway', response.data)
			self.assertIn(b'New York', response.data)
			self.assertIn(b'10025', response.data)

			user_garage = current_user.get_all_parking_spots()
			for spot in user_garage:
				self.assertEqual(str(spot), '<Parking Spot at {0} owned by: {1}. Availibility: {2}>'.format(spot.address, 
				spot.get_owner_name(), spot.availible))

	def test_new_user_has_no_spots(self):
		""" Tests to see that a new user that registers has no associated parking spots """
		self.register('jimmy', 'buckets', 'jbuckets@aol.com', 'igetBuckets')
		with self.client:
			self.login('jbuckets@aol.com', 'igetBuckets')
			user_garage = current_user.get_all_parking_spots()
			self.assertFalse(user_garage)

	@patch('app.routes.validate_address')
	def test_add_parking_space(self, va_mock):
		""" Tests to see if you can add a parking spot """ 
		self.assertLoginReq('/addspots')
		va_mock.return_value = valid_addr_tuple

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/addspots', follow_redirects=True)
			self.assertIn(b'Add a parking spot', response.data)
			self.assertIn(b'Enter Details Here', response.data)

			response = self.client.post('/addspots', data=dict(address='1020 Bay Ridge Avenue',
				city='Brooklyn', state='NY', zipcode=11219, ps_size='LMV'), follow_redirects=True)
			self.assert_template_used('seller.html')

			# User has two parking spaces now, see if this is true.
			garage = current_user.get_all_parking_spots()
			self.assertEqual(2, len(garage))

	@patch('app.routes.validate_address')
	def test_cant_add_same_parking_space(self, va_mock):
		self.assertLoginReq('/addspots')
		va_mock.return_value = False 

		with self.client:
			self.login('test@tester.com', 'test')

			# Tries to add things in tester's garage as new spots
			response = self.client.post('/addspots', data=dict(address='2957 Broadway',
				city='New York', state='NY', zipcode=10025, ps_size='SUV'), 
				follow_redirects=True)

			self.assertIn(b'You already added this spot to your garage', response.data)
			self.assert_template_used('addspots.html')

	def test_update_spots(self):
		# Does nothing much for now because the updating spot implementation has been changed
		# TODO UPDATE THIS TEST!!!
		self.assertLoginReq('/update_spot/1')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/update_spot/1')
			self.assertTrue(response.status_code, 200)

	def test_cannot_update_spot_that_isnt_yours(self):
		""" Tests to see that you can't update a spot that isn't yours """ 
		self.assertLoginReq('/update_spot/2')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/update_spot/2', follow_redirects=True)
			self.assert_template_used('notallowed.html')
			# self.assertIn(b'/notallowed', request.url)
			# self.assertIn(b'NO NOT ALLOWED!!!!', response.data)

class SellerFormValidationTests(BaseTestCase):
	def test_invalid_vehicle_type(self):
		""" Tests to see that it doesn't proceed if invalid vehicle type forced """
		self.assertLoginReq('/addspots')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.post('/addspots', data=dict(address='1022 Bay Ridge Parkway',
				city='Brooklyn', state='NY', zipcode=11217, ps_size='LVC'), follow_redirects=True)
			self.assertIn(b'/addspots', request.url)
