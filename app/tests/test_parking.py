#test/test_parking.py

import unittest
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User, Parking_Spot

class ParkingTest(BaseTestCase):
	########################
	#### Tests          ####
	########################
	def test_lists_parking_spots(self):
		with self.client:
			self.assertLoginReq('/viewspots')
			self.login('test@tester.com', 'test')
			response = self.client.get('/viewspots', follow_redirects=True)
			self.assertEqual(response.status_code, 200)
			self.assertIn(b'', response.data)