"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
from configs.config import Config


#create the app
app = Flask(__name__)
app.config.from_object(Config)

# import the modules that feed on the app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Order matters: Initialize SQLAlchemy before Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

from modules.DBModels import *
from flask_restful import Api, Resource, reqparse
from flask import request, jsonify
from flask_restful_swagger import swagger


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
api = swagger.docs(Api(app))

@app.route('/', methods=['GET'])
def home():
    return 'Hellow World!'

# endpoints as classes

class UserEndpoint(Resource):
    """
    Resource for Users in the API
    """

    def get(self):
        # function to get a user
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='You must provide an email address')
        args = parser.parse_args()
        resp = get_user(args)
        return resp

    def post(self):
        # function to create a new user
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='You must provide an email address')
        parser.add_argument('password', required=True, help='You must provide a password')
        args = parser.parse_args()
        user_payload = {'email': args['email'], 'password': args['password']}
        resp = add_user(user_payload)
        return resp

    def patch(self, id):
        # function to modify a user
        pass

    def delete(self):
        pass



class HouseholdEndpoint(Resource):
    """
    Resource for Household in the API
    """
    def get(self):
        # function to get a household
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='You must provide an email address')
        args = parser.parse_args()
        resp = Household.get_household(args)
        return resp

    def post(self):
        # function to create a new household
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help ='You must provide an email address')
        parser.add_argument('name', required=True, help='You must provide a name for the household')
        args = parser.parse_args()
        user_payload = {'email': args['email']}
        household_payload = {'name': args['name']}
        resp = add_household(user_payload, household_payload)
        return resp

    def patch(self, id):
        # function to modify a user
        pass


class ReceiptEndpoint(Resource):
    """
    Resource for Receipt in the API
    """
    def get(self, id):
        # function to get a user
        pass

    def post(self):
        # function to create a new receipt object
        pass

    def patch(self, id):
        # function to modify a user
        pass


class IndividualProductEndpoint(Resource):
    """
    Resource for IndividualProduct in the API
    """
    def get(self, id):
        # function to get a user
        pass

    def post(self):
        # function to create a new user
        pass

    def patch(self, id):
        # function to modify a user
        pass

    def delete(self, id):
        # function to delete a product
        pass


api.add_resource(UserEndpoint, '/user')
api.add_resource(HouseholdEndpoint, '/household')

# 404 handler

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
