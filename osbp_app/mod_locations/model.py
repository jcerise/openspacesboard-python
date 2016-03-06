from osbp_app import db


class ConferenceLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    spaces = db.relationship('ConferenceSpace', backref='location', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Location: {}>'.format(self.name)