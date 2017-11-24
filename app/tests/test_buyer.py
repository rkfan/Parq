#test/test_buyer.py

import unittest
# from mock import MagicMock, patch
from flask_login import current_user
from flask import request

from base import BaseTestCase
from app.models import User, Parking_Spot

class UserBuyerTestCases(BaseTestCase):
	# MOVE LATER, this is for testing some parts of the routes
	# Patch when you have a call in the routes etc and 
	# you want it to be a fake api call (return something predefined)
	# rather than the actual API call. 
	@patch('app.routes.validate_address')
	def test_buyer_search_invalid_address(self, va_mock):
		self.assertLoginReq('/buyer_search')
		va_mock.return_value=valid_addr_tuple
		with self.client: 
			self.login('test@tester.com', 'test')

	def test_buyer_search_get_view(self):
		self.assertLoginReq('/buyer_search')

		with self.client:
			self.login('test@tester.com', 'test')
			response = self.client.get('/buyer_search', follow_redirects=True)
			self.assertIn(b'/buyer_search', request.url)
