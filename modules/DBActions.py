__author__ = 'ciacicode'
from flask import jsonify
from modules.DBModels import *
from operator import itemgetter
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
import pdb


# add to database functions
def check_if_exists(user_payload):
    """

    :param user_payload: {'email', 'password'}
    :return: True if user exists, False if it does not exist
    """
    email = user_payload['email']
    user_queried = User.query.filter_by(email=email).first()
    if user_queried is None:
        return False
    else:
        return True

def get_user(user_payload):
    """

    :param user_payload:
    :return: if the user exists returns it otherwise 404

    """
    user_schema = UserSchema()
    check = check_if_exists(user_payload)
    if check is False:
        resp = jsonify({"error": "There is no user with this email address"})
        resp.status_code = 404
        return resp
    else:
        user_queried = User.query.filter_by(email=user_payload['email']).first_or_404()
        user = user_schema.dump(user_queried).data
        del user['password']
        resp = jsonify(user)
        resp.status_code = 200
        return resp

def add_user(user_payload):
    """

    :param user_payload: {'email','password'}
    :return: returns existing user object or new user object
    """
    # check if user exists
    check = check_if_exists(user_payload)
    user_schema = UserSchema()
    if check is False:
        try:
            user_schema.validate(user_payload)
            user = User(**user_payload)
            db.session.add(user)
            db.session.commit()
            user = user_schema.dump(user).data
            # remove password from result!
            del user['password']
            resp = jsonify(user)
            resp.status_code = 201
            return resp
        except ValidationError as e:
            resp = jsonify({"error": e.messages})
            resp.status_code = 401
            return resp
        except SQLAlchemyError as e:
            resp = jsonify({"error": e.messages})
            resp.status_code = 403
            return resp
    else:
        # user already exist, prompt sign in
        resp=jsonify({"error": "User with this email address already exists"})
        resp.status_code = 201



def check_household_exists(user_payload):
    """

    :param user: user payload
    :return: True, if there is already a household for the user, False if there is not, or 404 in case of request for non existing user
    """
    check = check_if_exists(user_payload)
    if check:
        # user exists, do they have a household?
        user = User.query.filter_by(email=user_payload['email']).first()
        household_id = user.household_id
        if household_id is None:
            # there is no household
            return False
        else:
            # there is a household
            return True
    else:
        return get_user(user_payload)


def get_household(user_payload):
    """

    :param user_payload:
    :return: response with household object or 404 error
    """
    check = check_household_exists(user_payload)
    household_schema = HouseholdSchema()
    if check is False:
        # household does not exist
        resp = jsonify({"error": "no household exists for this user"})
        resp.status_code = 404
        return resp
    elif check is True:
        #household exists
        user = User.query.filter_by(email=user_payload['email']).first()
        household_id = user.household_id
        household = Household.query.filter_by(id=household_id).first()
        result = household_schema.dump(household).data
        resp = jsonify(result)
        resp.status_code = 200
        return resp
    else:
        # return check which is a response
        return check

def add_household(user_payload, household_payload):
    """
    :param: user_payload
    :param household_payload:
    :return:household dict
    """
    pdb.set_trace()
    check = check_household_exists(user_payload)
    household_schema = HouseholdSchema()
    if check:
        # user already has household we should
        resp = jsonify({"error": "This user already has a household associated, only one household per user is allowed"})
        resp.status_code = 403
        return resp
    else:
        # there is no household associated with the user_payload
        household = Household(**household_payload)
        db.session.add(household)
        db.session.commit()
        user_payload = User.query.filter_by(email=user_payload['email']).first()
        # connect user_payload with its newly created household
        household.users.append(user_payload)
        db.session.commit()
        resp = jsonify(household_schema.dump(household).data)
        resp.status_code = 201
        return resp


def check_receipt_exists(receipt_payload):
    """

    :param receipt_payload: {seller:, file_pointer:, price_currency:}
    :return: True if the receipt already exists, False if this is a new receipt
    """
    check = OcadoReceipt.query.filter_by(file_pointer=receipt_payload['file_pointer']).first()
    if check is None:
        return False
    else:
        return True

def add_receipt(household, receipt_payload):
    """
    :param household is a household object
    :param receipt_payload: {seller:, file_pointer:, price_currency:}
    :return: receipt dict
    """
    # check if receipt was already created
    ocadoreceipt_schema = OcadoRecepitSchema()
    check = check_receipt_exists(receipt_payload)
    # fetch the database household object
    household = Household.query.filter_by(id=household['id']).first()
    if check:
        receipt = OcadoReceipt.query.filter_by(file_pointer=receipt_payload['file_pointer']).first()
        # a receipt exists, let's extract the products from the database
        products = receipt.individualproducts.all()
    else:
        # a receipt does not exist, create one and add it to database
        receipt = OcadoReceipt(**receipt_payload)
        db.session.add(receipt)
        db.session.commit()
        # process receipt so to obtain a list of product objects
        products = receipt.process_receipt()

    # loop through the products and add them
    for p in products:
        add_product_auto(household, p, receipt)

    # make sure the new receipt is associated with the household
    household.ocadoreceipts.append(receipt)
    return ocadoreceipt_schema.dump(receipt).data


def add_product_manual(household_payload, product_payload):
    """

    :param household_payload: from user interface
    :param individual_product_payload:
    :return: one new product in database with no receipt info
    """
    # clean up full form payload
    weight = product_payload['weight'], product_payload['unitCode']
    product_payload['weight'] = weight
    del product_payload['unitCode']
    del product_payload['submit']
    # generate instance of product
    product = IndividualProduct(**product_payload)
    household = get_household(household_payload)
    add_product_auto(household, product)


def add_product_auto(household, individual_product, receipt=None):
    """

    :param household: sqlalchemy object
    :param receipt: sqlalchemy object
    :param individual_product: istance of individual_product class
    :return: adds products to database and all relationships
    """
    try:
        individual_product_schema = IndividualProductSchema()
        # add the product to the session and commit it to the database
        db.session.add(individual_product)
        db.session.commit()
        if receipt is not None:
            # make sure that receipt is connected with the products
            receipt.individualproducts.append(individual_product)
            db.session.commit()
        # make sure that househ0lds are connected with the products
        household.individualproducts.append(individual_product)
        db.session.commit()
        return individual_product_schema.dump(individual_product).data
    except SQLAlchemyError as e:
        raise e


def get_products(household_payload):
    """

    :param household_payload: dict object
    :return: a list of products representing the household_payload inventory
    """
    individualproduct_schema = IndividualProductSchema()
    products = IndividualProduct.query.filter_by(household_id=household_payload['id']).all()
    inventory = list()
    for p in products:
        item = individualproduct_schema.dump(p).data
        inventory.append(item)
    products_by_expiry = sorted(inventory, key=itemgetter('expiry_date'))
    return products_by_expiry


def login_user(user_payload):
    """

    :param user_payload: {'email', 'password'}
    :return: user if the login was successful, False if the credentials are wrong
    """
    user_schema = UserSchema()
    check = check_if_exists(user_payload)
    password = user_payload['password']
    user_email = user_payload['email']
    if check:
        #check password is correct
        user = User.query.filter_by(email=user_email).first()
        household_id = user.household_id
        # get the password associated with the user and encode it
        hashed = user.password.encode('utf-8')
        # check if the hashed password corresponds to the new hashed of the input password
        if bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed:
            user = user_schema.dump(user).data
            user['household_id'] = household_id
            # remove password !
            del user['password']
            return user
        else:
            return False
    else:
        return False
