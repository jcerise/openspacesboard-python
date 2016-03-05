# Import flask and template operators
from flask import Flask, make_response, jsonify

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

from osbp_app.exceptions import InvalidUsage

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found...'}), 404)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


from osbp_app.mod_conference_sessions.controllers import mod_session as conference_sessions
from osbp_app.mod_spaces.controllers import mod_space as conference_spaces
from osbp_app.mod_locations.controllers import mod_location as conference_locations

# Register Blueprints
app.register_blueprint(conference_sessions)
app.register_blueprint(conference_spaces)
app.register_blueprint(conference_locations)



