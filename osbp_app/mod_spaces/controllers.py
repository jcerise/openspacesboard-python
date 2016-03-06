from datetime import datetime
from time import strptime

from flask import Blueprint, jsonify, request
from osbp_app import InvalidUsage, db
from osbp_app.mod_spaces.model import ConferenceSpace

mod_space = Blueprint('spaces', __name__, url_prefix='/conference_spaces')

@mod_space.route('/api/1.0', methods=['GET'])
def get_spaces():
    """
    Return a (json) list of spaces
    :return: A json formatted list of spaces
    """
    spaces = ConferenceSpace.query.all()
    spaces = [dict(id=row.id, space_name=row.space_name, location_id=row.location_id, event_date=row.event_date,
                   start_time=row.start_time, end_time=row.end_time) for row in spaces]
    return jsonify({'spaces': spaces})


@mod_space.route('/api/1.0/<int:space_id>', methods=['GET'])
def get_space(space_id):
    """
    Return a single space based on an ID
    :param space_id: The <int> ID of the space to return
    :return: A single space based on space_id
    """
    space = ConferenceSpace.query.get(space_id)

    if space is not None:
        space = dict(id=space.id, space_name=space.space_name, location_id=space.location_id, event_date=space.event_date,
                     start_time=space.start_time, end_time=space.end_time)
        return jsonify({'space': space})
    else:
        raise InvalidUsage('ConferenceSpace with ID: {} does not exist'.format(space_id), status_code=400)


@mod_space.route('/api/1.0', methods=['POST'])
def create_space():
    """
    Create a new space from a json object
    :return: The json representing the newly created space
    """
    try:
        json = request.json
        event_date = datetime.strptime(json['event_date'], "%Y-%m-%d")
        start_time = datetime.strptime(json['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(json['end_time'], "%Y-%m-%d %H:%M:%S")
        space = ConferenceSpace(json['space_name'], json['location_id'], event_date, start_time, end_time)

        db.session.add(space)
        db.session.commit()

        space = dict(id=space.id, space_name=space.space_name, location_id=space.location_id, event_date=space.event_date,
                     start_time=space.start_time, end_time=space.end_time)
        return jsonify({'space': space})
    except Exception as err:
        raise InvalidUsage('Invalid request. Request json: {}. Error: {}'.format(json, err), status_code=400)


@mod_space.route('/api/1.0/<int:space_id>', methods=['PUT'])
def update_space(space_id):
    """
    Update a single space from a json object
    :param space_id: The <int> id of the space to update
    :return: The json object representing the newly updated space
    """
    space = ConferenceSpace.query.get(space_id)

    if space is not None:
        try:
            json = request.json

            if 'space_name' in json:
                space.space_name = json['space_name']
            if 'location_id' in json:
                space.location_id = json['location_id']
            if 'event_date' in json:
                space.event_date = json['event_date']
            if 'start_time' in json:
                space.start_time = json['start_time']
            if 'end_time' in json:
                space.end_time = json['end_time']

            db.session.commit()

            return jsonify(json)
        except Exception:
            raise InvalidUsage('Invalid request. Request json: {}'.format(json), status_code=400)
    else:
        raise InvalidUsage('ConferenceSpace with ID: {} does not exist'.format(space_id), status_code=400)


@mod_space.route('/api/1.0/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    """
    Delete a single space based on the space id
    :param space_id: The <int> id of the space to delete
    :return: A json object indicating if the deletion was a success or not
    """
    space = ConferenceSpace.query.get(space_id)

    if space is not None:
        db.session.delete(space)
        db.session.commit()

        return jsonify({"success": "true"})
    else:
        raise InvalidUsage('ConferenceSpace with ID: {} does not exist'.format(space_id), status_code=400)
