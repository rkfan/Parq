from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, validators, \
                    SubmitField, RadioField, IntegerField

from models import db, User, Parking_Spot, Message


class ContactForm(Form):
  name = TextField("Name")
  email = TextField("Email")
  subject = TextField("Subject")
  message = TextAreaField("Message")
  submit = SubmitField("Send")


class SignupForm(Form):
  firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
  lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Create account")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False

    if User.user_email_taken(self.email.data.lower()):
      self.email.errors.append("That email is already taken")
      return False
    
    return True

class SigninForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Sign In")
   
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False

    user = User.get_user(self.email.data.lower()) 
    if user and user.is_correct_password(self.password.data):
      return True

    self.email.errors.append("Invalid e-mail or password")
    return False

class SellerForm(Form):
  address = TextField("Street Address", [validators.Required("Please enter your street address.")])
  city = TextField("City", [validators.Required("Please enter your city.")])
  state = TextField("State", [validators.Required("Please enter your state.")])
  zipcode = IntegerField("Zip Code", [validators.Required("Please enter your zip code."), \
                      validators.NumberRange(min=10001, max=14975, message="Invalid NY zipcode.")]) 
  ps_size = RadioField('Parking Size', choices=[('LMV', 'LMV'), ('SUV', 'SUV'),('HMV', 'HMV')])

  submit = SubmitField("Add Parking Spot")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self, uid):
    if not Form.validate(self):
      return False

    # Looks to see if that parking space is already listed by this user. For now, only allow one parking
    # space for a seller for one type of car

    full_address_dict = {'address':self.address.data.title(), 'city':self.city.data.title(),
    'state': self.state.data.title(), 'zipcode':self.zipcode.data}

    if Parking_Spot.spot_exists(uid, full_address_dict):
      self.address.errors.append("You already added this spot to your garage.")
      return False

    return True


class UpdateProfileForm(Form):
  firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
  lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
  submit = SubmitField("Update Profile")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False


class UpdateParkingSpotForm(Form):
  address = TextField("Street Address", [validators.Required("Please enter your street address.")])
  city = TextField("City", [validators.Required("Please enter your city.")])
  state = TextField("State", [validators.Required("Please enter your state.")])
  zipcode = IntegerField("Zip Code", [validators.Required("Please enter your zip code."), \
                      validators.NumberRange(min=10001, max=14975, message="Invalid NY zipcode.")]) 
  ps_size = RadioField('Parking Size', choices=[('LMV', 'LMV'), ('SUV', 'SUV'),('HMV', 'HMV')])

  submit = SubmitField("Add Parking Spot")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self, uid):
    if not Form.validate(self):
      return False

class ApprovalForm(Form):
  submit = SubmitField("Approve Request")
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self, uid):
    if not Form.validate(self):
      return False


    # Not neccesary?
    # # Looks to see if that parking space is already listed by this user. For now, only allow one parking
    # # space for a seller for one type of car
    # full_address_dict = {'address':self.address.data.title(), 'city':self.city.data.title(), \
    # 'state': self.city.data.title(), 'zipcode':self.zipcode.data}

    # if Parking_Spot.spot_exists(uid, full_address_dict):
    #   self.address.errors.append("You already added this spot to your garage.")
    #   return False

    return True

class MessageForm(Form):
  message = TextAreaField("Message",  [validators.Required("Please enter your message")])
  submit = SubmitField("Send Message")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False

class BuyerForm(Form):
  address = TextField("Street Address", [validators.Required("Please enter your street address.")])
  city = TextField("City", [validators.Required("Please enter your city.")])
  state = TextField("State", [validators.Required("Please enter your state.")])
  zipcode = IntegerField("Zip Code", [validators.Required("Please enter your zip code."), \
                      validators.NumberRange(min=10001, max=14975, message="Invalid NY zipcode.")]) 
  ps_size = RadioField('Parking Size', choices=[('LMV', 'LMV'), ('SUV', 'SUV'),('HMV', 'HMV')])

  submit = SubmitField("Search parking Spot")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self, uid):
    if not Form.validate(self):
      return False

    return True

