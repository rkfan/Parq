app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/UserData'
from models import db
db.init_app(app)
