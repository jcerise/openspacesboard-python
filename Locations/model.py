from openspacesboard import db


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.column(db.String(64))

    def __repr__(self):
        return '<Location: {}>'.format(self.name)