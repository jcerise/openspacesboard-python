from osbp_app import db


class ConferenceSpace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    space_name = db.Column(db.String(64), unique=True)
    location_id = db.Column(db.Integer, db.ForeignKey('conference_location.id'))
    event_date = db.Column(db.Date)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self, space_name, location_id, event_date, start_time, end_time):
        self.space_name = space_name
        self.location_id = location_id
        self.event_date = event_date
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return '<Space: {} on {} from {} to {}>'.format(self.space_name,
                                                        self.event_date,
                                                        self.start_time,
                                                        self.end_time)