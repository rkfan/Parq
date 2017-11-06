# tests/base.py

from flask_testing import TestCase

from app import app, db
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
		db.session.add(Parking_Spot(1, "600 Broadway", "New York", "NY", 10001, "SUV"))
		db.session.add(Parking_Spot(2, "100 West 14 Street", "New York", "NY", 10002, "LMV"))
		db.session.commit()

	def tearDown(self):
		""" Teardown method """ 
		db.session.remove()
		db.drop_all()