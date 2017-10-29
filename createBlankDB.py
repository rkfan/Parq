from app import app, db

def createUserDataDB():
	db.drop_all()
	db.create_all()


if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/UserData'

    createUserDataDB()
