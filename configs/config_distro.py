__author__ = 'ciacicode'

class Config(object):
    SECRET_KEY = 'production key'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlalchemyurl'
    UPLOAD_FOLDER = 'upload folder for receipts'