from flask import jsonify, request, Blueprint

from osbp_app import InvalidUsage, db
from osbp_app.mod_conference_sessions.models import ConferenceSession
from flask.ext.cors import CORS

mod_session = Blueprint('session', __name__, url_prefix='/conference_sessions')
CORS(mod_session)


@mod_session.route('/api/1.0', methods=['GET'])
def get_sessions():
    """
    Return a (json) list of sessions
    :return: A json formatted list of sessions
    """
    sessions = ConferenceSession.query.all()

    sessions_list = []
    for session in sessions:
        session_space = session.space
        session_location = session_space.location
        timespan = {'start_time': session_space.start_time, 'end_time': session_space.end_time}
        session = dict(id=session.id, title=session.title, description=session.description, convener=session.convener,
                       space_name=session_space.space_name, location=session_location.name,
                       date=session_space.event_date, timespan=timespan)
        sessions_list.append(session)

    return jsonify({'sessions': sessions_list})


@mod_session.route('/api/1.0/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """
    Return a single session based on an ID
    :param session_id: The <int> ID of the session to return
    :return: A single session based on session_id
    """
    session = ConferenceSession.query.get(session_id)

    if session is not None:
        session_space = session.space
        session_location = session_space.location
        timespan = {'start_time': session_space.start_time, 'end_time': session_space.end_time}
        session = dict(id=session.id, title=session.title, description=session.description, convener=session.convener,
                       space_name=session_space.space_name, location=session_location.name,
                       date=session_space.event_date, timespan=timespan)
        return jsonify({'session': session})
    else:
        raise InvalidUsage('ConferenceSession with ID: {} does not exist'.format(session_id), status_code=400)


@mod_session.route('/api/1.0', methods=['POST'])
def create_session():
    """
    Create a new session from a json object
    :return: The json representing the newly created session
    """
    try:
        json = request.json
        session = ConferenceSession(json['title'], json['description'], json['convener'], json['space_id'])

        db.session.add(session)
        db.session.commit()

        session = dict(id=session.id, title=session.title, description=session.description, convener=session.convener, space_id=session.space_id)
        return jsonify({'session': session})
    except Exception as err:
        raise InvalidUsage('Invalid request. Request json: {}. Error: {}'.format(json, err), status_code=400)


@mod_session.route('/api/1.0/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """
    Update a single session from a json object
    :param session_id: The <int> id of the session to update
    :return: The json object representing the newly updated session
    """
    session = ConferenceSession.query.get(session_id)

    if session is not None:
        try:
            json = request.json

            if 'title' in json:
                session.title = json['title']
            if 'description' in json:
                session.description = json['description']
            if 'convener' in json:
                session.convener = json['convener']
            if 'space_id' in json:
                session.space_id = json['space_id']

            db.session.commit()

            return jsonify(json)
        except Exception:
            raise InvalidUsage('Invalid request. Request json: {}'.format(json), status_code=400)
    else:
        raise InvalidUsage('ConferenceSession with ID: {} does not exist'.format(session_id), status_code=400)


@mod_session.route('/api/1.0/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a single session based on the session id
    :param session_id: The <int> id of the session to delete
    :return: A json object indicating if the deletion was a success or not
    """
    session = ConferenceSession.query.get(session_id)

    if session is not None:
        db.session.delete(session)
        db.session.commit()

        return jsonify({"success": "true"})
    else:
        raise InvalidUsage('ConferenceSession with ID: {} does not exist'.format(session_id), status_code=400)
