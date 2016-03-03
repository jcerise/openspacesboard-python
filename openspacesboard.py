import sqlite3
from contextlib import closing


from flask import Flask, g, jsonify, request, make_response, redirect, url_for, session
from flask_oauthlib.client import OAuth

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


oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key='2a13319f2059625dbeb9',
    consumer_secret='660136b970b0acc7b764c665cf3cea4b3ae332fc',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/')
def index():
    if 'github_token' in session:
        me = github.get('user')
        return jsonify(me.data)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return jsonify(me.data)


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


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


@app.route('/board/api/1.0/spaces', methods=['GET'])
def get_spaces():
    """
    Return a (json) list of spaces
    :return: A json formatted list of spaces
    """
    cur = g.db.execute('select space_name, location_id, event_date, start_time, end_time from spaces')
    spaces = [dict(space_name=row[0], location_id=row[1], event_date=row[2], start_time=row[3], end_time=row[4]) for row in cur.fetchall()]
    return jsonify({'spaces': spaces})


@app.route('/board/api/1.0/spaces/<int:space_id>', methods=['GET'])
def get_space(space_id):
    """
    Return a single space based on an ID
    :param space_id: The <int> ID of the space to return
    :return: A single space based on space_id
    """
    cursor = g.db.execute('select * from spaces where id = ?', str(space_id))
    space = cursor.fetchone()

    if space is not None:
        return jsonify({'space': space})
    else:
        raise InvalidUsage('space with ID: {} does not exist'.format(space_id), status_code=400)


@app.route('/board/api/1.0/spaces', methods=['POST'])
def create_space():
    """
    Create a new space from a json object
    :return: The json representing the newly created space
    """
    try:
        json = request.json

        space = {
            'space_name': json['space_name'],
            'location_id': json['location_id'],
            'event_date': json['event_date'],
            'start_time': json['start_time'],
            'end_time': json['end_time']
        }

        g.db.execute('insert into spaces (space_name, location_id, event_date, start_time, end_time) values (?, ?, ?, ?, ?)', [space['space_name'],
                                                                                                                         space['location_id'],
                                                                                                                         space['event_date'],
                                                                                                                         space['start_time'],
                                                                                                                         space['end_time']])

        g.db.commit()
        return jsonify(space)
    except Exception as err:
        raise InvalidUsage('Invalid request. Request json: {}. Error: {}'.format(json, err), status_code=400)


@app.route('/board/api/1.0/spaces/<int:space_id>', methods=['PUT'])
def update_space(space_id):
    """
    Update a single space from a json object
    :param space_id: The <int> id of the space to update
    :return: The json object representing the newly updated space
    """
    cursor = g.db.execute('select * from spaces where id = ?', str(space_id))
    space = cursor.fetchone()

    if space is not None:
        try:
            json = request.json
            if 'space_name' in json:
                space_name = json['space_name']
            else:
                space_name = space['space_name']
            if 'location_id' in json:
                location_id = json['location_id']
            else:
                location_id = space['location_id']
            if 'event_date' in json:
                event_date = json['event_date']
            else:
                event_date = space['event_date']
            if 'start_time' in json:
                start_time = json['start_time']
            else:
                start_time = json['start_time']
            if 'end_time' in json:
                end_time = json['end_time']
            else:
                end_time = json['end_time']

            g.db.execute('update spaces set space_name=?, location_id=?, event_date=?, start_time=?, end_time=? where id=?', [space_name,
                                                                                                                        location_id,
                                                                                                                        event_date,
                                                                                                                        start_time,
                                                                                                                        end_time,
                                                                                                                        space_id])

            g.db.commit()
            return jsonify(json)
        except Exception as err:
            raise InvalidUsage('Invalid request. Request json: {}. Error: {}'.format(json, err), status_code=400)
    else:
        raise InvalidUsage('space with ID: {} does not exist'.format(space_id), status_code=400)


@app.route('/board/api/1.0/spaces/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    """
    Delete a single space based on the space id
    :param space_id: The <int> id of the space to delete
    :return: A json object indicating if the deletion was a success or not
    """
    cursor = g.db.execute('select * from spaces where id = ?', str(space_id))
    space = cursor.fetchone()

    if space is not None:
        g.db.execute('delete from spaces where id = ?', [space_id])
        g.db.commit()

        return jsonify({"success": "true"})
    else:
        raise InvalidUsage('space with ID: {} does not exist'.format(space_id), status_code=400)

if __name__ == '__main__':
    app.run()
