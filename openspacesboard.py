import sqlite3
from contextlib import closing
from os import abort

from flask import Flask, g, render_template, jsonify, request, make_response

# Configuration variables
DATABASE = 'C:\\tmp\\openspacesboard.db'
DEBUG = True
SECRET_KEY = "secret"
USERNAME = 'admin'
PASSWORD = 'test'

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


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found...'}), 404)

@app.route('/board/api/1.0/sessions', methods=['GET'])
def get_sessions():
    cur = g.db.execute('select title, description, convener from sessions')
    sessions = [dict(title=row[0], description=row[1], convener=row[2]) for row in cur.fetchall()]
    return jsonify({'sessions': sessions})


@app.route('/board/api/1.0/sessions', methods=['POST'])
def create_session():
    if not request.json or not 'title' in request.json:
        abort(400)



if __name__ == '__main__':
    app.run()
