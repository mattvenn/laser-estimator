from laser_estimator import db

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    thickness = db.Column(db.Float, default=0)
    vector_etch_speed = db.Column(db.Integer, default=0)
    cut_speed = db.Column(db.Integer, default=0)
    cost_per_unit = db.Column(db.Float, default=0)

    def __repr__(self):
        return '%s - %d mm' % (self.name, self.thickness)

