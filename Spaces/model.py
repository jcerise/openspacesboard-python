from openspacesboard import db

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    space_name = db.Column(db.String(64))
    location_id = db.Column(db.String(64), db.ForeignKey('location.id'))
    event_date = db.Column(db.Date)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Session: {} by {}>'.format(self.title, self.convener)