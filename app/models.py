from app import db
from werkzeug import generate_password_hash, check_password_hash

class User(db.Model):
  __tablename__ = 'users'

  uid = db.Column(db.Integer, primary_key = True)
  firstname = db.Column(db.String(100))
  lastname = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(100))
  authenticated = db.Column(db.Boolean, default=False)

  parking_spots = db.relationship("Parking_Spot", backref="users")
   
  def __init__(self, firstname, lastname, email, password):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    self.email = email.lower()
    self.set_password(password)
    self.authenticated = False
     
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
  
  def is_correct_password(self, password):
    return check_password_hash(self.pwdhash, password)

  def get_all_parking_spots(self):
    return Parking_Spot.query.filter_by(ownerid = self.uid, validity=1).all()

  def get_all_messages(self):
    """ Gets a user's messages """  
    return Message.query.filter_by(receiver_uid=self.uid).all()

  def get_my_messages_by_status(self, approved=0):
    """ Returns user's unapproved messages """ 
    return Message.query.filter_by(sender_uid=self.uid, approved=approved).all()

  @classmethod
  def user_email_taken(cls, email):
    """ Queries to see if the user email is taken. Same as seeing if 
        user has an account or not.""" 
    return cls.query.filter_by(email = email).first() is not None

  @classmethod 
  def get_user_name(cls, id):
    """ Returns a user's name by uid """ 
    user = cls.query.filter_by(uid=id).first()
    return user.firstname+" "+ user.lastname 

  @classmethod
  def get_user(cls, email):
    """ Queries to see if the user exists and returns the User object """
    return cls.query.filter_by(email=email).first()

  # Stuff for flask_login
  @property
  def is_authenticated(self):
    """ Returns True if the user is authenticated """ 
    return self.authenticated

  @property
  def is_active(self):
    """ Always true, as all users are active. """
    return True

  @property
  def is_anonymous(self):
    """ Always False, users aren't supposed to be anonymouse """
    return False

  def get_id(self):
    """ Returns the uid as an int """ 
    return self.uid

  def __str__(self):
    return 'User {0} {1} with email: {2}'.format(self.firstname, self.lastname, self.email)

class Parking_Spot(db.Model):
  __tablename__ = 'parking_spots'
  psid = db.Column(db.Integer, primary_key = True)
  ownerid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
  address = db.Column(db.String(200), nullable=False)
  city = db.Column(db.String(100), nullable=False)
  state = db.Column(db.String(100), nullable=False)
  zipcode = db.Column(db.Integer, nullable=False)
  ps_size = db.Column(db.String(120), nullable=False)
  validity = db.Column(db.Boolean, default=True)
  availible = db.Column(db.Boolean, default=True)
  lat = db.Column(db.Float, nullable=False)
  lon = db.Column(db.Float, nullable=False)

  # ownerid? Do we need to do something with that...?
  def __init__(self, ownerid, address, city, state, zipcode, ps_size, lat, lon):
    self.ownerid = ownerid
    self.address = address
    self.city = city
    self.state = state
    self.zipcode = zipcode
    self.ps_size = ps_size.title()
    self.validity = True
    self.availible = True
    self.lat = lat
    self.lon = lon

  def getAvailibility(self):  
    return self.availible

  @classmethod
  def get_all_spots(cls):
    """ Select all method for parking spots. Returns all Parking_Spot
        objects that are stored in the database """ 
    return cls.query.order_by(cls.city).all()

  @classmethod
  def get_parking_spot_by_id(cls, parking_id):
    """ Gets a parking spot by parking id only """
    return cls.query.filter_by(psid=parking_id).first()

  @classmethod
  def get_user_parking_spot_by_id(cls, parking_id, uid):
    """ Gets a user's parking spot by its parking spot id (psid) """  
    return cls.query.filter_by(psid=parking_id, ownerid=uid).first()

  @classmethod 
  def spot_exists(cls, uid, full_address):
    """ Return true if spot exists, false otherwise """ 
    return cls.query.filter_by(ownerid=uid, address=full_address['address'],
                        city=full_address['city'], state=full_address['state'],
                        zipcode=full_address['zipcode']).first() is not None

  @classmethod 
  def get_spots_for_buyer(cls, uid):
    return cls.query.filter(cls.ownerid != uid, cls.validity == 1).all()


  def get_owner_name(self):
    """ Returns the owner name based on the ownerid """
    owner = User.query.filter_by(uid=self.ownerid).first()
    return owner.firstname + " " + owner.lastname 

  def get_owner_email(self):
    """ Returns the owner's email """ 
    owner = User.query.filter_by(uid=self.ownerid).first()
    return owner.email

  def __str__(self):
    return '<Parking Spot at {0} owned by: {1}. Availibility: {2}>'.format(self.address, self.get_owner_name, 
                                                                          self.availible)


class Message(db.Model):
  __tablename__ = 'my_messages'

  message_id = db.Column(db.Integer, primary_key=True)
  sender_uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
  receiver_uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
  psid = db.Column(db.Integer, db.ForeignKey('parking_spots.psid', ondelete="CASCADE"), nullable=False)
  message = db.Column(db.String(500), nullable=False)
  isRead = db.Column(db.Boolean, default=False)
  approved = db.Column(db.Boolean, default=False)

  def __init__(self, sender_uid, rcv_uid, psid, msg):
    self.sender_uid = sender_uid
    self.receiver_uid = rcv_uid
    self.psid = psid
    self.message = msg
    self.isRead = False
    self.approved = False

  @classmethod 
  def get_message_by_id(cls, message_id):
    return cls.query.filter_by(message_id=message_id).first()

  @classmethod
  def get_message_by_id_status(cls, message_id, status):
    return cls.query.filter_by(message_id=message_id, approved=status).first()


