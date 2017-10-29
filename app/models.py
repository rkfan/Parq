from app import db
from werkzeug import generate_password_hash, check_password_hash

class User(db.Model):
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key = True)
  firstname = db.Column(db.String(100))
  lastname = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(100))

  parking_spots = db.relationship("Parking_Spot", backref="users")
   
  def __init__(self, firstname, lastname, email, password):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    self.email = email.lower()
    self.set_password(password)
     
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)

class Parking_Spot(db.Model):
  __tablename__ = 'parking_spots'
  psid = db.Column(db.Integer, primary_key = True)
  ownerid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
  address = db.Column(db.String(200), nullable=False)
  city = db.Column(db.String(100), nullable=False)
  state = db.Column(db.String(100), nullable=False)
  zipcode = db.Column(db.Integer, nullable=False)
  ps_size = db.Column(db.String(120), nullable=False)

  # ownerid? Do we need to do something with that...?
  def __init__(self, ownerid, address, city, state, zipcode, ps_size):
    self.ownerid = ownerid
    self.address = address.title()
    self.city = city.title()
    self.state = state.title()
    self.zipcode = zipcode
    self.ps_size = ps_size.title()

