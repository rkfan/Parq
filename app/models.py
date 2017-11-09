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
  #my_messages = db.relationship("Message", backref="users")
   
  def __init__(self, firstname, lastname, email, password):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    self.email = email.lower()
    self.set_password(password)
    self.authenticated = False
     
  def set_password(self, password):
    """ Sets the password hash for the user """ 
    self.pwdhash = generate_password_hash(password)
  
  def is_correct_password(self, password):
    """ Checks to see if the password is correct """
    return check_password_hash(self.pwdhash, password)

  def authenticate_user(self):
    self.authenticated = True
    db.session.add(self)
    db.session.commit()

  def deauthenticate_user(self):
    self.authenticated = False
    db.session.add(self)
    db.session.commit()

  def get_all_parking_spots(self):
    """ Gets all the user's valid parking spots """ 
    return Parking_Spot.query.filter_by(ownerid = self.uid, validity=True).all()

  def get_avail_parking_spots(self):
    """ Gets all the user's availible parking spots """ 
    return Parking_Spot.query.filter_by(ownerid = self.uid, availible=True).all()

  def update_profile(self, firstname, lastname):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    db.session.commit()

  @classmethod
  def user_email_taken(cls, email):
    """ Queries to see if the user email is taken. Same as seeing if 
        user has an account or not.""" 
    return cls.query.filter_by(email = email).first() is not None

  @classmethod
  def get_user(cls, email):
    """ Queries to see if the user exists and returns the User object """
    return cls.query.filter_by(email=email).first()

  @classmethod 
  def add_user(cls, newuser):
    """ Adds a new user to the database """ 
    db.session.add(newuser)
    db.session.commit()

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

  #my_messages = db.relationship("Message", backref="parking_spots")

  # ownerid? Do we need to do something with that...?
  def __init__(self, ownerid, address, city, state, zipcode, ps_size):
    self.ownerid = ownerid
    self.address = address.title()
    self.city = city.title()
    self.state = state.title()
    self.zipcode = zipcode
    self.ps_size = ps_size.title()
    self.validity = True
    self.availible = True

  def getAvailibility(self):  
    return self.availible

  @classmethod
  def get_all_spots(cls):
    """ Select all method for parking spots. Returns all Parking_Spot
        objects that are stored in the database """ 
    #return cls.query.order_by(cls.city).all()
    return cls.query.filter_by(validity=True, availible=True).all()

  @classmethod
  def get_parking_spot_by_id(cls, parking_id, uid):
    """ Gets a parking spot by its parking spot id (psd) """  
    return cls.query.filter_by(psid=parking_id, ownerid=uid).first()

  @classmethod 
  def spot_exists(cls, uid, full_address):
    """ Return true if spot exists, false otherwise """ 
    return cls.query.filter_by(ownerid=uid, address=full_address['address'],
                        city=full_address['city'], state=full_address['state'],
                        zipcode=full_address['zipcode'], validity=True).first() is not None
  @classmethod 
  def spot_exists_but_deleted(cls, uid, full_address):
    """ Returns the parking spot if it has been added by the user but 'deleted' """ 
    return cls.query.filter_by(ownerid=uid, address=full_address['address'],
                    city=full_address['city'], state=full_address['state'],
                    zipcode=full_address['zipcode'], validity=False).first()

  def get_owner_name(self):
    """ Returns the owner name based on the ownerid """
    owner = User.query.filter_by(uid=self.ownerid).first()
    return owner.firstname + " " + owner.lastname 

  def get_owner_email(self):
    owner = User.query.filter_by(uid=self.ownerid).first()
    return owner.email

  def add_spot(self):
    """ Adds a spot to the database """ 
    db.session.add(self)
    db.session.commit()

  def update_spot(self, full_address):
    """ Updates information about the parking spot using dictionary stored with the info """ 
    self.address = full_address['address'].title()
    self.city = full_address['city'].title()
    self.state = full_address['state'].title()
    self.zipcode = full_address['zipcode']
    self.ps_size = full_address['ps_size'].title()
    db.session.commit()

  def reactivate_spot(self, space_size):
    """ Reactivates a spot that has been 'deleted' prior """ 
    self.validity = 1
    self.ps_size = space_size
    db.session.commit()

  def delete_spot(self):
    """ Deletes a spot by setting the validity to false """ 
    self.validity = 0
    db.session.commit()

  def __str__(self):
    return '<Parking Spot at {0} owned by: {1}. Availibility: {2}>'.format(self.address, self.get_owner_name, 
                                                                          self.availible)

# class Message(db.Model):
#   __tablename__ = 'my_messages'

#   message_id = db.Column(db.Integer, primary_key=True)
#   sender_uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
#   receiver_uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete="CASCADE"), nullable=False)
#   psid = db.Column(db.Integer, db.ForeignKey('parking_spots.psid', ondelete="CASCADE"), nullable=False)
#   message = db.Column(db.String(500), nullable=False)
#   isRead = db.Column(db.Boolean, default=False)

#   def __init__(self, sender_uid, rcv_uid, psid, msg):
#     self.sender_uid = sender_uid
#     self.receiver_uid = rcv_uid
#     self.psid = psid
#     self.message = msg
#     self.isRead = False