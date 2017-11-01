from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from flaskext.mysql import MySQL
from flask_wtf.csrf import CSRFProtect

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder = template_dir)

# Configurations
#app.config.from_object('config') # Maybe have from configuration file?

# Define and cnofigure the database object imported by modules and controllers
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'vTI\x9f\xe6y\xf3g\xbb?\xa6(\x84\xf8\x82(\xd8wM\xe8}\xeb\xd1='
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/UserData'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
#db.init_app(app)
CSRFProtect(app)

# Link the Flak-Login module with flask application
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User

@login_manager.user_loader
def load_user(user_id):
	return User.query.filter(User.uid == int(user_id)).first()

# Sample HTML Error handling
@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

# Import module/component using blueprint handler variable
#from routes import app_parq

# Register blueprint(s)
#app.register_blueprint(app_parq)

from app import routes