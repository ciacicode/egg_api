__author__ = 'ciacicode'


class Config(object):
    SECRET_KEY = 'very secret key'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/egg?unix_socket=/cloudsql/egg-api:egg'
    UPLOAD_FOLDER = '/home/maria/Desktop/ciacicode/recipe_suggest/egg/receipts/'
    ALLOWED_EXTENSIONS = 'pdf'
