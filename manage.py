import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from config import basedir

from osbp_app import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'osbp_app.db')

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
