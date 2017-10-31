from app import app, db
import urllib2
from flask import Flask
from flask_testing import LiveServerTestCase
import unittest

# Testing with LiveServer
class MyTest(LiveServerTestCase, unittest.TestCase):
	TESTING = True

  	# if the create_app is not implemented NotImplementedError will be raised
	def create_app(self):
		app.config['TESTING'] = True
		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 5000
		# Default timeout is 5 seconds
		app.config['LIVESERVER_TIMEOUT'] = 10

		# URI for our test database
		app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/ParqTest'
		return app

	def test_flask_application_is_up_and_running(self):
		response = urllib2.urlopen(self.get_server_url())
		self.assertEqual(response.code, 200)

	def setUp(self):
		db.drop_all()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	# Does not work!!! :(
	def test_get_home(self):
		rv = urllib2.urlopen(self.get_server_url()+'/login')
		self.assertEqual(rv.code, 200)
	########################
	#### helper methods ####
	########################
	 
	# def register(self, fname, lname, email, password):
	#     return self.app.post(
	#         '/signup',
	#         data=dict(firstname=fname, lastname=lnmae, email=email, password=password),
	#         follow_redirects=True
	#     )
	 
	# # def login(self, email, password):
	# #     return self.app.post(
	# #         '/signin',
	# #         data=dict(email=email, password=password),
	# #         follow_redirects=True
	# #     )
	 
	# # def logout(self):
	# #     return self.app.get(
	# #         '/logout',
	# #         follow_redirects=True
	# #     )

	# def test_valid_user_registration(self):
	#     response = self.register('patrick', 'kennedy', 'patkennedy79@gmail.com', 'FlaskIsAwesome')
	#     self.assertEqual(response.status_code, 200)
	#     #self.assertIn(b'Thanks for registering!', response.data)


if __name__ == '__main__':
    unittest.main()
