from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, validators, \
                    SubmitField, RadioField, IntegerField

# Need to import for querying for the purpose of validation
from models import db, User, Parking_Spot


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

    user = User.query.filter_by(email = self.email.data.lower()).first()
    if user:
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
     
    user = User.query.filter_by(email = self.email.data.lower()).first()
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
    parking_space = Parking_Spot.query.filter_by(ownerid=uid, address=self.address.data.title(),
                                                city=self.city.data.title(), state=self.state.data.title(),
                                                zipcode=self.zipcode.data).first()
    if parking_space:
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

    # Looks to see if that parking space is already listed by this user. For now, only allow one parking
    # space for a seller for one type of car
    parking_space = Parking_Spot.query.filter_by(ownerid=uid, address=self.address.data.title(),
                                                city=self.city.data.title(), state=self.state.data.title(),
                                                zipcode=self.zipcode.data).first()
    if parking_space:
      self.address.errors.append("You already added this spot to your garage.")
      return False

    return True
