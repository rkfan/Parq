from app import app, db
from app.models import User

def createUserDataDB():
	db.drop_all()
	db.create_all()

def registerTestUsers():
	testUser1 = User("test", "tester", "test@tester.com", "test")
	testUser2 = User("Raymond", "Fan", "rfan4922@bths.edu", "test")
	db.session.add(testUser1)
	db.session.add(testUser2)
	db.session.commit()

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/UserData'

    createUserDataDB()
    registerTestUsers()