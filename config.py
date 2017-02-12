import os
basedir = os.path.abspath(os.path.dirname(__file__))
from password import SECRET_KEY
UPLOAD_DIR = 'uploads'
WTF_CSRF_ENABLED = True
