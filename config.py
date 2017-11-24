# app/config.py

# Source: https://github.com/realpython/discover-flask/blob/master/config.py

class BaseConfig(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'vTI\x9f\xe6y\xf3g\xbb?\xa6(\x84\xf8\x82(\xd8wM\xe8}\xeb\xd1='
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/UserData'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class TestConfig(BaseConfig):
	DEBUG = True
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
	SQLALCHEMY_ECHO = False

class DevelopmentalConfig(BaseConfig):
	DEBUG = True

class ProductionConfig(BaseConfig):
	DEBUG = False
