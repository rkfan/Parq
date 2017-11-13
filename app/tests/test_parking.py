#test/test_parking.py

import unittest
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User, Parking_Spot

class ParqSellerFunctTests(BaseTestCase):
	def test_see_garage(self):
		""" Tests to see that the tester's parking spots are listed """ 
		self.assertLoginReq('/viewspots')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/viewspots', follow_redirects=True)
			self.assertIn(b'600 Broadway', response.data)
			self.assertIn(b'New York', response.data)
			self.assertIn(b'10001', response.data)

			user_garage = current_user.get_all_parking_spots()
			for spot in user_garage:
				self.assertEqual(str(spot), '<Parking Spot at {0} owned by: {1}. Availibility: {2}>'.format(spot.address, 
				spot.get_owner_name, spot.availible))

	def test_new_user_has_no_spots(self):
		""" Tests to see that a new user that registers has no associated parking spots """
		self.register('jimmy', 'buckets', 'jbuckets@aol.com', 'igetBuckets')
		with self.client:
			self.login('jbuckets@aol.com', 'igetBuckets')
			user_garage = current_user.get_all_parking_spots()
			self.assertTrue(user_garage, None)

	def test_add_parking_space(self):
		""" Tests to see if you can add a parking spot """ 
		self.assertLoginReq('/addspots')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/addspots', follow_redirects=True)
			self.assertIn(b'Add a parking spot', response.data)
			self.assertIn(b'Enter Details Here', response.data)

			response = self.client.post('/addspots', data=dict(address='1022 Bay Ridge Parkway',
				city='Brooklyn', state='NY', zipcode=11217, ps_size='LMV'), follow_redirects=True)
			self.assertIn(b'/seller', request.url)

	def cant_add_same_parking_space(self):
		self.assertLoginReq('/addspots')

		with self.client:
			self.login('test@tester.com', 'test')

			response = self.client.post('/addspots', data=dict(address='1022 Bay Ridge Parkway',
				city='Brooklyn', state='NY', zipcode=11217, ps_size='LMV'), follow_redirects=True)
			self.assertIn(b'/seller', request.url)

			# Tries to add things in tester's garage as new spots
			user_garage = current_user.get_parking_spots()
			for spot in user_garage:
				response = self.client.post('/addspots', data=dict(address=spot.address,
					city=spot.city, state=spot.state, zipcode=spot.zipcode, ps_size=spot.ps_size), 
					follow_redirects=True)
				self.assertIn(b'You already added this spot to your garage', response.data)

	def test_update_spots(self):
		# Does nothing much for now because the updating spot implementation has been changed
		# TODO UPDATE THIS TEST!!!
		self.assertLoginReq('/update_spot/1')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/update_spot/1')
			self.assertTrue(response.status_code, 200)

	def cannot_update_spot_that_isnt_yours(self):
		""" Tests to see that you cant update a spot that isnt yours """ 
		self.assertLoginReq('/update_spot/2')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/update_spot/2', follow_redirects=True)
			self.assertIn(b'/notallowed', request.url)
			self.assertIn(b'NO NOT ALLOWED!!!!', response.data)

class SellerFormValidationTests(BaseTestCase):
	def test_invalid_vehicle_type(self):
		""" Tests to see that it doesn't proceed if invalid vehicle type forced """
		self.assertLoginReq('/addspots')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.post('/addspots', data=dict(address='1022 Bay Ridge Parkway',
				city='Brooklyn', state='NY', zipcode=11217, ps_size='LVC'), follow_redirects=True)
			self.assertIn(b'/addspots', request.url)


class ParqBuyerFunctTests(BaseTestCase):
	def test_see_availible_parking_spots(self):
		""" Test the buyer page. May need to change after first iteration, since first lists all """
		self.assertLoginReq('/buyer')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/buyer')
			self.assertIn(b'Buyer Page', response.data)
			self.assertIn(b'Here is a list of all availible parking spots', response.data)

			# Check to see that page displays all spots. NTS don't actually need byte representation!  
			all_spots = Parking_Spot.get_all_spots()
			for spot in all_spots:
				self.assertIn(spot.address, response.data)
				self.assertIn(spot.city, response.data)
				self.assertIn(spot.state, response.data)
				self.assertIn(str(spot.zipcode), response.data)
				self.assertIn(spot.ps_size, response.data)

#class BuyerFormValidationTests(BaseTestCase):

if __name__ == '__main__':
	unittest.main()