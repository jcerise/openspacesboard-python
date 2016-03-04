from openspacesboard import db


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(64))
    convener = db.Column(db.String(64))
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'))

    def __repr__(self):
        return '<Session: {} by {}>'.format(self.title, self.convener)
