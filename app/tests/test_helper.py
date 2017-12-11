#test/test_helper.py

import unittest
from mock import MagicMock
from flask_login import current_user
from flask import request

from base import BaseTestCase
#from app.models import User, Parking_Spot
from app.routes import validate_address, parse_search_query

valid_address_return = [{u'geometry': {u'location': {u'lat': 40.8079732, u'lng': -73.9643219}, 
u'viewport': {u'northeast': {u'lat': 40.8093221802915, u'lng': -73.96297291970849}, 
u'southwest': {u'lat': 40.8066242197085, u'lng': -73.9656708802915}}, u'location_type': u'ROOFTOP'}, 
u'address_components': [{u'long_name': u'2957', u'types': [u'street_number'], u'short_name': u'2957'}, 
{u'long_name': u'Broadway', u'types': [u'route'], u'short_name': u'Broadway'}, 
{u'long_name': u'Manhattan', u'types': [u'political', u'sublocality', u'sublocality_level_1'], u'short_name': u'Manhattan'}, 
{u'long_name': u'New York', u'types': [u'locality', u'political'], u'short_name': u'New York'}, 
{u'long_name': u'New York County', u'types': [u'administrative_area_level_2', u'political'], u'short_name': u'New York County'},
{u'long_name': u'New York', u'types': [u'administrative_area_level_1', u'political'], u'short_name': u'NY'}, 
{u'long_name': u'United States', u'types': [u'country', u'political'], u'short_name': u'US'}, {u'long_name': u'10025', 
u'types': [u'postal_code'], u'short_name': u'10025'}, {u'long_name': u'7802', u'types': [u'postal_code_suffix'], u'short_name': u'7802'}], 
u'place_id': u'ChIJgXOmuD72wokRRD2f6MLhY9c', u'formatted_address': u'2957 Broadway, New York, NY 10025, USA', u'types': [u'street_address']}]

valid_addr_tuple = ('2957 Broadway, New York, NY 10025, USA', [40.8079732, -73.9643219])

class FakeGmaps():
	""" Fake class for mocking the gmaps module """ 
	pass

class HelperFunctionTestCases(BaseTestCase):
	def test_validate_address(self):
		fake_gmaps = FakeGmaps()
		fake_gmaps.geocode = MagicMock(return_value=valid_address_return)
		valid_address = "2957 Broadway, New York, NY 10025"
		response = validate_address(valid_address, fake_gmaps)
		fake_gmaps.geocode.assert_called_once_with(valid_address)

		# Tests that it returns the correct tuple: (full_place_name, coordinates)
		self.assertEqual(len(response), 2)
		self.assertEqual(response[0],  '2957 Broadway, New York, NY 10025, USA')
		self.assertEqual(len(response[1]), 2)
		self.assertEqual(response[1], [40.8079732, -73.9643219])

	def test_empty_invalid_address(self):
		fake_gmaps = FakeGmaps()
		fake_gmaps.geocode = MagicMock(return_value=[])
		response = validate_address('', fake_gmaps)
		fake_gmaps.geocode.assert_called_once_with('')

		self.assertFalse(response)

	def test_partial_match_validate_address(self):
		fake_gmaps = FakeGmaps()
		fake_gmaps.geocode = MagicMock(return_value=[{'partial_match' : True}])
		response = validate_address('', fake_gmaps)
		fake_gmaps.geocode.assert_called_once_with('')

		self.assertFalse(response)

	def test_parse_search_query(self):
		#query = "40.8079732%-73.9643219%10025%2957 Broadway" # Stub query
		query = "40.8079732"+"%"+"-73.9643219"+"%"+"10025"+"%"+"2957 Broadway"

		ret = parse_search_query(query)

		self.assertEqual(len(ret), 3)
		self.assertEqual(len(ret[0]), 2)
		lat_lon = ret[0]
		self.assertTrue(isinstance(lat_lon[0], float))
		self.assertTrue(isinstance(lat_lon[1], float))
		self.assertTrue(isinstance(ret[1], int))
		self.assertTrue(isinstance(ret[2], str))

