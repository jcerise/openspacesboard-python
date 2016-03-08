from flask import Blueprint, jsonify, request

from osbp_app import InvalidUsage, db
from osbp_app.mod_locations.model import ConferenceLocation

mod_location = Blueprint('locations', __name__, url_prefix='/conference_locations')


@mod_location.route('/api/1.0', methods=['GET'])
def get_locations():
    """
    Return a (json) list of locations
    :return: A json formatted list of locations
    """
    locations = ConferenceLocation.query.all()
    locations = [dict(id=row.id, name=row.name) for row in locations]
    return jsonify({'locations': locations})


@mod_location.route('/api/1.0/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """
    Return a single location based on an ID
    :param location_id: The <int> ID of the location to return
    :return: A single location based on location_id
    """
    location = ConferenceLocation.query.get(location_id)

    if location is not None:
        location = dict(id=location.id, name=location.name)
        return jsonify({'location': location})
    else:
        raise InvalidUsage('ConferenceLocation with ID: {} does not exist'.format(location_id), status_code=400)


@mod_location.route('/api/1.0', methods=['POST'])
def create_location():
    """
    Create a new location from a json object
    :return: The json representing the newly created location
    """
    try:
        json = request.json
        location = ConferenceLocation(json['name'])

        db.session.add(location)
        db.session.commit()

        location = dict(id=location.id, location_name=location.name)
        return jsonify({'location': location})
    except Exception as err:
        raise InvalidUsage('Invalid request. Request json: {}. Error: {}'.format(json, err), status_code=400)


@mod_location.route('/api/1.0/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """
    Update a single location from a json object
    :param location_id: The <int> id of the location to update
    :return: The json object representing the newly updated location
    """
    location = ConferenceLocation.query.get(location_id)

    if location is not None:
        try:
            json = request.json

            if 'name' in json:
                location.name = json['name']

            db.session.commit()

            return jsonify(json)
        except Exception:
            raise InvalidUsage('Invalid request. Request json: {}'.format(json), status_code=400)
    else:
        raise InvalidUsage('Conferencelocation with ID: {} does not exist'.format(location_id), status_code=400)


@mod_location.route('/api/1.0/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """
    Delete a single location based on the location id
    :param location_id: The <int> id of the location to delete
    :return: A json object indicating if the deletion was a success or not
    """
    location = ConferenceLocation.query.get(location_id)

    if location is not None:
        db.session.delete(location)
        db.session.commit()

        return jsonify({"success": "true"})
    else:
        raise InvalidUsage('ConferenceLocation with ID: {} does not exist'.format(location_id), status_code=400)
