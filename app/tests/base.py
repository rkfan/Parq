# tests/base.py

from flask_testing import TestCase

from app import app, db, gmaps
import config
from app.models import User, Parking_Spot

class BaseTestCase(TestCase):
	""" A base test case."""

	# Helper inherited methods
	def assertLoginReq(self, page):
		""" Assert that this page requires signing in """ 
		response = self.client.get(page, follow_redirects=True)
		self.assertIn(b'Sign In', response.data)

	def get_test_acc(self):
		""" Returns the object that describes the predefined test account """ 
		return User.query.filter_by(email='test@tester.com').first()

	def register(self, fname, lname, email, password):
		""" Registers a user with the following credentials """ 
		return self.client.post('/signup', data=dict(firstname=fname, lastname=lname, 
			email=email, password=password), follow_redirects=True)

	def login(self, email, password):
		""" Logs in the with specified email and password. Returns the response """ 
		return self.client.post('/login', data=dict(email=email, password=password), 
			follow_redirects=True)

	# Overriden/set up methods

	def create_app(self):
		app.config.from_object('config.TestConfig')
		return app

	def setUp(self):
		""" Setup. Creates a test user and two parking spots """ 
		db.create_all()
		db.session.add(User("Test", "Tester", "test@tester.com", "test"))
		db.session.add(User("Adam", "Admin", "admin@admin.com", "admin"))
		db.session.add(Parking_Spot(1, "2957 Broadway", "New York", "NY", 10025, "SUV", 40.8079732, -73.9643219))	# Shake Shack
		db.session.add(Parking_Spot(2, "2013 66 Street", "Brooklyn", "NY", 11204, "LMV", 40.6156401, -73.9860273))
		db.session.commit()

	def tearDown(self):
		""" Teardown method """ 
		db.session.remove()
		db.drop_all()