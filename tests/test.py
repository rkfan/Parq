import sys
sys.path.append('..')

from app import app
import urllib2
from flask import Flask
from flask_testing import LiveServerTestCase
import unittest

# Testing with LiveServer
class MyTest(LiveServerTestCase):
  # if the create_app is not implemented NotImplementedError will be raised
	def create_app(self):
		app.config['TESTING'] = True
		return app

	def test_flask_application_is_up_and_running(self):
		response = urllib2.urlopen(self.get_server_url())
		self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main()
