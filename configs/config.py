__author__ = 'ciacicode'


class Config(object):
    SECRET_KEY = 'aa76&6(w1osj5y_!$cy0up&qtf3!b*%9%1dvmj8ujns5r&mfaw-1a9'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:78uLL9(:f5r%poe@/egg?unix_socket=/cloudsql/egg-api:egg'
    UPLOAD_FOLDER = '/home/maria/Desktop/ciacicode/recipe_suggest/egg/receipts/'
    ALLOWED_EXTENSIONS = 'pdf'
