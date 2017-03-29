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

    def __init__(self, name=None, thickness=None, vector_etch_speed=None, cut_speed=None, cost_per_unit=None):
        self.name = name
        self.thickness = thickness
        self.vector_etch_speed = vector_etch_speed
        self.cut_speed = cut_speed
        self.cost_per_unit = cost_per_unit

