import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'osbp_app.db')
DATABASE_PATH = os.path.join(basedir, 'osbp_app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

DEBUG = True
SECRET_KEY = "secret"
USERNAME = 'admin'
PASSWORD = 'test'