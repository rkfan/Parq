from app import app, db
from app.models import User, Parking_Spot

def createUserDataDB():
	db.drop_all()
	db.create_all()

def registerTestUsers():
	testUser1 = User("test", "tester", "test@tester.com", "test")
	testUser2 = User("Raymond", "Fan", "rfan4922@bths.edu", "test")
	db.session.add(testUser1)
	db.session.add(testUser2)
	db.session.commit()

# Change this to 
def loadParkingSpots():
	parkingSpot1 = Parking_Spot(2, "2013 66 Street", "Brooklyn", "NY", 11204, "LMV", 40.6156401, -73.9860273)
	parkingSpot2 = Parking_Spot(2, "6702 20 Avenue", "Brooklyn", "NY", 11204, "SUV", 40.6154347, -73.9873838)
	parkingSpot3 = Parking_Spot(2, "2025 66 Street", "Brooklyn", "NY", 11204, "LMV", 40.6157197, -73.9855921)
	parkingSpot4 = Parking_Spot(2, "1857 66 Street", "Brooklyn", "NY", 11204, "LMV", 40.6178453, -73.9890897)
	parkingSpot5 = Parking_Spot(2, "1866 68 Street", "Brooklyn", "NY", 11204, "SUV", 40.6162409, -73.9901626)
	parkingSpot6 = Parking_Spot(2, "1942 Bay Ridge Avenue", "Brooklyn", "NY", 11204, "SUV", 40.6148971, -73.9893686)

	db.session.add(parkingSpot1)	
	db.session.add(parkingSpot2)
	db.session.add(parkingSpot3)
	db.session.add(parkingSpot4)
	db.session.add(parkingSpot5)
	db.session.add(parkingSpot6)
	db.session.commit()

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/UserData'

    createUserDataDB()
    registerTestUsers()
    loadParkingSpots()