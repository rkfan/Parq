# tests/test_basic.py
 
import unittest
from base import BaseTestCase

# Basic parq test cases with getting certain views
class ParqBasicTestCases(BaseTestCase):
	def test_unauthenticated_index(self):
		""" Correctly gets index page """
		# Not authenticated, authenticated will be tested laters
		response = self.client.get('/', content_type='html/text', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(b'Please signup or login.' in response.data)

	def test_about(self):
		""" Gets about page """
		response = self.client.get('/about', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'We are a small startup in the heart of Manhattan.', response.data)

	def test_junk(self):
		""" Tests to see if 404 page is yielded """ 
		response = self.client.get('/safjsdlkjfsdlkjf', follow_redirects=True)
		self.assertEquals(response.status_code, 404)

if __name__ == '__main__':
	unittest.main()