#test/test_buyer.py

import unittest
from mock import MagicMock, patch
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User, Parking_Spot

valid_addr_tuple = ('2957 Broadway, New York, NY 10025, USA', [40.8079732, -73.9643219])

class UserBuyerTestCases(BaseTestCase):
	def test_buyer_search_get_view(self):
		self.assertLoginReq('/buyer_search')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/buyer_search', follow_redirects=True)
			self.assertIn(b'/buyer_search', request.url)

	def test_invalid_inputs(self):
		self.assertLoginReq('/buyer_search')
		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.post('/buyer_search', data=dict(address='',
				city='', state='', zipcode=10000, ps_size=''), follow_redirects=True)
			self.assertIn(b'/buyer_search', request.url)

			response = self.client.post('/buyer_search', data=dict(address='',
				city='', state='', zipcode=14976, ps_size=''), follow_redirects=True)
			self.assertIn(b'/buyer_search', request.url)

	# Patch when you have a call in the routes etc and 
	# you want it to be a fake api call (return something predefined)
	# rather than the actual API call. 
	@patch('app.routes.validate_address')
	def test_buyer_search_invalid_address(self, va_mock):
		self.assertLoginReq('/buyer_search')
		va_mock.return_value = False

		with self.client: 
			self.login('test@tester.com', 'test')
			response = self.client.post('/buyer_search', data=dict(address='1022 Bay Ridge Parkway',
			city='New York', state='NY', zipcode=11219, ps_size='SUV'), follow_redirects=True)
			self.assertIn(b'/buyer_search', request.url)
			self.assertIn(b'Invalid Address', response.data)

	@patch('app.routes.validate_address')
	def test_buyer_search_valid_address_hit(self, va_mock):
		self.assertLoginReq('/buyer_search')
		va_mock.return_value = valid_addr_tuple

		with self.client:
			self.login('admin@admin.com', 'admin')
			response = self.client.post('/buyer_search', data=dict(address='2957 Broadway',
			city='New York', state='NY', zipcode=10025, ps_size='SUV'), follow_redirects=True)
			self.assert_template_used('buyer_search_map.html')

	@patch('app.routes.validate_address')
	def test_buyer_search_valid_address_miss(self, va_mock):
		self.assertLoginReq('/buyer_search')

		# Change it to something that is not within the vicinity
		valid_addr_tuple = ('90 Church St, New York, NY 10007, USA', [40.7127847, -74.0102577])
		va_mock.return_value = valid_addr_tuple

		with self.client:
			self.login('admin@admin.com', 'admin')
			response = self.client.post('/buyer_search', data=dict(address='2957 Broadway',
			city='New York', state='NY', zipcode=10025, ps_size='SUV'), follow_redirects=True)
			self.assert_template_used('buyer_search_results.html')
			self.assertIn(b'Your search yielded no results :-(', response.data)
