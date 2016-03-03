import sqlite3
from contextlib import closing

from flask import Flask, g, jsonify, request, make_response

# Configuration variables
DATABASE = 'C:\\tmp\\openspacesboard.db'
DEBUG = True
SECRET_KEY = "secret"
USERNAME = 'admin'
PASSWORD = 'test'

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def connect_db():
    """
    Connect to the database specified in the settings file (assumes SQLite3)
    :return:
    """
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """
    Sets up the initial database based on the schema file located in the project root
    :return:
    """
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found...'}), 404)


@app.route('/board/api/1.0/sessions', methods=['GET'])
def get_sessions():
    """
    Return a (json) list of sessions
    :return: A json formatted list of sessions
    """
    cur = g.db.execute('select title, description, convener from sessions')
    sessions = [dict(title=row[0], description=row[1], convener=row[2]) for row in cur.fetchall()]
    return jsonify({'sessions': sessions})


@app.route('/board/api/1.0/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """
    Return a single session based on an ID
    :param session_id: The <int> ID of the session to return
    :return: A single session based on session_id
    """
    cursor = g.db.execute('select * from sessions where id = ?', str(session_id))
    session = cursor.fetchone()

    if session is not None:
        return jsonify({'session': session})
    else:
        raise InvalidUsage('Session with ID: {} does not exist'.format(session_id), status_code=400)


@app.route('/board/api/1.0/sessions', methods=['POST'])
def create_session():
    """
    Create a new session from a json object
    :return: The json representing the newly created session
    """
    try:
        json = request.json

        session = {
            'title': json['title'],
            'description': json['description'],
            'convener': json['convener']
        }

        g.db.execute('insert into sessions (title, description, convener) values (?, ?, ?)', [session['title'],
                                                                                              session['description'],
                                                                                              session['convener']])

        g.db.commit()
        return jsonify(session)
    except Exception:
        raise InvalidUsage('Invalid request. Request json: {}'.format(json), status_code=400)


@app.route('/board/api/1.0/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """
    Update a single session from a json object
    :param session_id: The <int> id of the session to update
    :return: The json object representing the newly updated session
    """
    cursor = g.db.execute('select * from sessions where id = ?', str(session_id))
    session = cursor.fetchone()

    if session is not None:
        try:
            json = request.json

            g.db.execute('update sessions set title=?, description=?, convener=? where id=?', [json['title'],
                                                                                               json['description'],
                                                                                               json['convener'],
                                                                                               session_id])

            g.db.commit()
            return jsonify(json)
        except Exception:
            raise InvalidUsage('Invalid request. Request json: {}'.format(json), status_code=400)
    else:
        raise InvalidUsage('Session with ID: {} does not exist'.format(session_id), status_code=400)


@app.route('/board/api/1.0/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a single session based on the session id
    :param session_id: The <int> id of the session to delete
    :return: A json object indicating if the deletion was a success or not
    """
    cursor = g.db.execute('select * from sessions where id = ?', str(session_id))
    session = cursor.fetchone()

    if session is not None:
        g.db.execute('delete from sessions where id = ?', [session_id])
        g.db.commit()

        return jsonify({"success": "true"})
    else:
        raise InvalidUsage('Session with ID: {} does not exist'.format(session_id), status_code=400)

if __name__ == '__main__':
    app.run()

