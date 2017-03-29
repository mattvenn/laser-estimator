import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# mail

MAIL_USERNAME = "samples@nice-cuts.com"
MAIL_SERVER = "smtp.zoho.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
#MAIL_PORT : default 25
#MAIL_USE_SSL : default False
#MAIL_DEBUG : default app.debug
#MAIL_DEFAULT_SENDER : default None
#MAIL_MAX_EMAILS : default None
#MAIL_SUPPRESS_SEND : default app.testing
#MAIL_ASCII_ATTACHMENTS : default False


from password import SECRET_KEY, USERNAME, PASSWORD, MAIL_PASSWORD, EMAIL
COST_PER_SEC = 40.0 / 60 / 60
UNIT_SIZE_MM = 50 * 50 # mm
UPLOAD_DIR = 'uploads'
WTF_CSRF_ENABLED = True
