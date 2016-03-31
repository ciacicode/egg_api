__author__ = 'ciacicode'


class Config(object):
    SECRET_KEY = '6AA0p[$f//LOLlpw'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://egg_admin:dev_admin@localhost:3306/egg'
    UPLOAD_FOLDER = '/home/maria/Desktop/ciacicode/recipe_suggest/egg/receipts/'
    ALLOWED_EXTENSIONS = 'pdf'
