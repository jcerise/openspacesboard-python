from osbp_app import db


class ConferenceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(64))
    convener = db.Column(db.String(64))
    space_id = db.Column(db.Integer, db.ForeignKey('conference_space.id'))

    def __init__(self, title, description, convener, space_id):
        self.title = title
        self.description = description
        self.convener = convener
        self.space_id = space_id

    def __repr__(self):
        return '<ConferenceSession: {} by {}>'.format(self.title, self.convener)

