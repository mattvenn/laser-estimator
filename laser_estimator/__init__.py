from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from laser_estimator import views, models
admin = Admin(app, name='laser estimator', template_mode='bootstrap3')
admin.add_view(ModelView(models.Material, db.session))

