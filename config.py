import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

from password import SECRET_KEY, USERNAME, PASSWORD
COST_PER_SEC = 40.0 / 60 / 60
UPLOAD_DIR = 'uploads'
WTF_CSRF_ENABLED = True
