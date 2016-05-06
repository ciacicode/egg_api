__author__ = 'ciacicode'

from main import db, ma
import bcrypt
import datetime
from operator import itemgetter
from marshmallow import ValidationError
import bcrypt
from flask import jsonify
import re
from lxml import etree
import requests
from sqlalchemy.exc import SQLAlchemyError


def create_db(db):
    """
    Create database
    """
    db.create_all()


class QuantitativeValue(object):
    """Any quantitative value that implies a unit
    value
    unit code (ISO)
    """
    def __init__(self, value=0.0, unitCode=''):
        self.value = value
        self.unitCode = unitCode

    def __repr__(self):
        out = dict()
        out['value'] = self.value
        out['unitCode'] = self.unitCode
        return str(out)


# tables and models
class IndividualProduct(db.Model):

    """Any individual product that can be used in a recipe"""
    __tablename__ = 'individualproduct'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    weight = db.Column(db.String(250))
    brand = db.Column(db.String(250))
    category = db.Column(db.String(250))
    model = db.Column(db.String(250))
    expiry_date = db.Column(db.DateTime())
    quantity = db.Column(db.Integer)
    price = db.Column(db.String(250))
    purchase_date = db.Column(db.DateTime())

    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))
    receipt_id = db.Column(db.Integer, db.ForeignKey('ocadoreceipt.id'))


    def __init__(self, name, quantity = None, weight=None, purchase_date = None, brand=None, category=None, price=None, model=None, expiry_date = None):
        self.name = name
        self.weight = weight
        self.quantity = quantity
        self.purchase_date = purchase_date
        self.brand = brand
        self.category = category
        self.model = model
        self.expiry_date = expiry_date
        self.price = price

    def add_expiry(self, expiry_date):
        assert isinstance(expiry_date, datetime)
        self.expiry_date = expiry_date

    def add_owner(self, household_id):
        self.household_id = household_id

    def use_product(self, weight):
        pass

    def throw_product(self):
        # remove product from db
        pass

    def extend_product(self):
        pass


    def __repr__(self):
        out = dict()
        out['name'] = self.name
        out['weight'] = self.weight
        out['brand'] = self.brand
        out['model'] = self.model
        out['category'] = self.category
        out['purchase_date'] = self.purchase_date
        out['expiry_date'] = self.expiry_date
        out['price'] = self.price
        return str(out)

# marshmallow schema
class IndividualProductSchema(ma.ModelSchema):
    class Meta:
        model = IndividualProduct


class User(db.Model):
    """Object representing a user """

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(500))

    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))


    def __init__(self, email, password):
        self.email = email
        # hash the password
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def get_id(self):
        return self.id

    def modify_password(self, new_password):
        self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())



class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class OcadoReceipt(db.Model):
    """
    Table of OcadoReceipts
    """
    __tablename__ = 'ocadoreceipt'
    id = db.Column(db.Integer, primary_key=True)
    file_pointer = db.Column(db.String(255))
    seller = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    price_currency = db.Column(db.String(4))
    household = db.Column(db.Integer, db.ForeignKey('household.id'))

    individualproducts = db.relationship('IndividualProduct', backref='receipt', lazy='dynamic')

    def __init__(self, seller, file_pointer, price_currency=None):

        self.purchase_date = None
        self.price_currency = price_currency
        self.seller = seller
        self.file_pointer = file_pointer
        self.xml_pointer = self.pdf_to_xml()
        self.calendar_dict = self.split_receipt()

    def add_owner(self, household_id):
        self.household_id = household_id

    def pdf_to_xml(self):
        """
        :return: directory of xml file
        """
        # to rewrite
        #out_pointer = self.file_pointer[:-4]
        #xml_dir = out_pointer + '.html'
        #command = 'pdftohtml ' + '-xml ' + self.file_pointer + ' ' + xml_dir
        #os.system(command)
        #return xml_dir + '.xml'
        # download pdf
        pdf = self.download_file(self.file_pointer)
        print pdf

        # access pdf and transform in xml
        # upload xml
    @staticmethod
    def download_file(url):
        local_filename = url.split('/')[-1]
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        return local_filename


    def get_xml_root(self):
        """
        :return: page object of parsed xml file
        """
        # to rewrite
        file_path = self.xml_pointer
        tree = etree.parse(file_path)
        root = tree.getroot()
        page = root[0]
        return page

    @staticmethod
    def pick_ocado_date(delivery_string):
        """
        :param date_string=: entire ocado delivery db.String
        :return: ('dd/mm/yyy','Saturday')
        """
        splitt = delivery_string.split()
        day = splitt[2][:-1]
        date = splitt[3]
        return date, day

    @staticmethod
    def transform_ocado_date(date_string):
        """
        :param date_string=: ocado order delivery date format db.String dd/mm/yyyy
        :return: datetime object for that day
        """
        date_object = datetime.datetime.strptime(date_string,'%d/%m/%Y')
        return date_object

    @staticmethod
    def day_variation(delivery_day, current_day):
        """

        :param current_day: expiry day the receipt refers to
        :param delivery_day: day of the week where the delivery was done
        :return: (current_day, variation from delivery)
        """
        days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        delivery_day_index = days_of_the_week.index(delivery_day)
        week_ahead = list(days_of_the_week[delivery_day_index:] + days_of_the_week)[:7]
        if current_day == 'tomorrow':
            return week_ahead[1], 1
        else:
            current_day_index = week_ahead.index(current_day)
        return current_day, int(current_day_index)

    def split_receipt(self):
        """
        :return: dict of items split by day of expiration
        {'dd/mm/yyy/':[[product name, delivered/ordered, price in GBP]]
        """
        DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        WORDS_WE_DONT_CARE_ABOUT = ['Delivered /', 'Ordered', 'Price', 'to', 'pay']
        # setting default values
        xml_root = self.get_xml_root()
        calendar_dict = dict()
        current_day_string = ''
        delivery_date = None
        current_day_date = None
        list_started_flag = False
        individual_products = list()
        # loop through the tree and find information
        for el in xml_root.iter('text'):
            if len(el) == 1:
                # detected child element
                text = el[0].text
            else:
                text = el.text

        # determine current day of delivery
            try:
                if 'Delivery date:' in text:
                    delivery_date_string, delivery_day = self.pick_ocado_date(text)
                    delivery_date = self.transform_ocado_date(delivery_date_string)
                    self.purchase_date = delivery_date
                    current_day_date = self.transform_ocado_date(delivery_date_string)
                    current_day_string = current_day_date.strftime('%d/%m/%Y')
                    continue

                if 'tomorrow' in text:
                    #'tomorrow' in text
                    list_started_flag = True
                    # found start of product list
                    day_info = self.day_variation(delivery_day, 'tomorrow')
                    current_day_date = delivery_date + datetime.timedelta(days=day_info[1])
                    current_day_string = current_day_date.strftime('%d/%m/%Y')
                    calendar_dict[current_day_string] = None
                    individual_products = []
                    continue
                if any(day in text for day in DAYS_OF_THE_WEEK):
                    # list starts with no 'tomorrow' but mentions a day
                    list_started_flag = True
                    if 'Use by end of' in text:
                        current_day_day = text.split()[4]
                    else:
                        current_day_day = text
                    day_info = self.day_variation(delivery_day, current_day_day)
                    current_day_date = delivery_date + datetime.timedelta(days=day_info[1])
                    current_day_string = current_day_date.strftime('%d/%m/%Y')
                    calendar_dict[current_day_string] = None
                    individual_products = []
                    continue

                if 'Freezer' in text or 'Cupboard' in text:

                    continue
                if 'Products with a \'use-by\' date over one week' == text:
                    try:
                        if el.getprevious()[0].text == 'Cupboard':
                            # cupboard items
                            list_started_flag = True
                            current_day_date = delivery_date + datetime.timedelta(days=12)
                            current_day_string = current_day_date.strftime('%d/%m/%Y')
                            calendar_dict[current_day_string] = None
                            individual_products = []
                            continue
                        elif el.getprevious()[0].text == 'Freezer':
                            # freezer items
                            list_started_flag = True
                            current_day_date = delivery_date + datetime.timedelta(days=30)
                            current_day_string = current_day_date.strftime('%d/%m/%Y')
                            calendar_dict[current_day_string] = None
                            individual_products = []
                            continue
                        else:
                            list_started_flag = True
                            # there is no cupboard or freezer in the previous element
                            current_day_date = delivery_date + datetime.timedelta(days=9)
                            current_day_string = current_day_date.strftime('%d/%m/%Y')
                            calendar_dict[current_day_string] = None
                            individual_products = []
                    except IndexError:
                        continue
                if text in WORDS_WE_DONT_CARE_ABOUT:
                    # remove 'ordered, delivered etc'
                    list_started_flag = False

                if 'Products with no \'use-by\' date' in text:
                    # remove toiletries
                    list_started_flag = False

                if list_started_flag and 'Offers savings' in text:
                    # we reached the end of the product list
                    break

                if list_started_flag:
                    individual_products.append(text)

                if len(individual_products) >=1:
                    # there are individual_products to add
                        calendar_dict[current_day_string] = individual_products
            except IndexError:
                current_day_string = 'unkown_expiry_date'
        return calendar_dict



    def check_if_name(self, input_string):
        """

        :param input_string:
        :return: True if the string is NOT a price or NOT an order/delivered
        """
        result = False
        if self.get_weight(input_string) is not None:
            return True
        elif '/' not in input_string and '.' not in input_string:
            return True
        return result

    @staticmethod
    def get_quantity(input_string):
        """

        :param input_string: delivered/ordered info
        :return: delivered as db.String
        """
        quantity = input_string.split('/')[0]
        return quantity

    @staticmethod
    def split_merged_field(input_string):
        """

        :param input_string: merged string of quantity price
        :return: (quantity, price) as strings in tuple
        """
        try:
            split = input_string.split()
            quantity = split[0].split('/')[0]
            price = split[1]
            return quantity, price
        except IndexError:
            return 'None', 'None'


    @staticmethod
    def merged_field_check(input_string):
        """

        :param input_string:
        :return: True if quantity and price are merged
        """
        result = False
        if '/EACH' in input_string or '/kg' in input_string:
            return result
        elif '.' in input_string:
            if '/' in input_string:
                result = True
        return result

    @staticmethod
    def get_weight(input_string):
        """

        :param input_string: a db.String that includes or not a weight info
        :return: the weight as QuantitativeValue
        """
        default = None
        regexp_weight = re.compile(r'(?:\d*\.)?\d+(g|kg|l)')
        regexp_value = re.compile(r'(?:\d*\.)?\d+')
        regexp_unit_code = re.compile(r'(g|kg|l)')
        weight_info = regexp_weight.search(input_string)

        if weight_info is not None:
            #split the weight info
            value = re.search(regexp_value, weight_info.group()).group()
            unitCode = re.search(regexp_unit_code, weight_info.group()).group()
            #make quantitative value
            weight = QuantitativeValue(float(value), str(unitCode))
            return weight
        else:
            return default

    def normalise_product_details_list(self, day_list):
        """

        :param day_list: list of product details for a given expiration day
        :return: ([normalized list], product count) as product details tuple
        """
        new_day_list = list()
        flag = False
        #sanitise double line names
        for el in range(len(day_list)):
            try:
                curr = day_list[el]
                next = day_list[el+1]
                curr_name_flag = self.check_if_name(curr)
                next_weight_flag = self.get_weight(next)
                if curr_name_flag:
                    # if we think this is a name
                    if next_weight_flag is not None:
                        # does the next item have weight info?
                        # double row name
                        new_day_list.append(str(day_list[el]) + ' ' + day_list[el+1])
                        # set a flag to true to avoid marking next item as a name
                        flag=True
                    elif 'EACH' in next or '/kg' in next:
                        new_day_list.append(day_list[el] + ' ' + day_list[el+1])
                        flag=True
                    elif 'MEDIUM' in next or 'LARGE' in next:
                        new_day_list.append(day_list[el] + ' ' + day_list[el+1])
                        flag=True
                    else:
                        if flag is True:
                            continue
                        else:
                            # name with no weight
                            new_day_list.append(day_list[el])
                            flag = False
                else:
                    new_day_list.append(day_list[el])
                    flag=False

            except IndexError:
                # at the end of list, its a price!
                new_day_list.append(curr)
                continue
        return new_day_list

    def create_individual_product(self, product_dict):
        """
        :param product_dict: with keys corresponding to product attributes
        :return: IndividualProduct object
        """
        product_dict['purchase_date'] = self.purchase_date
        product = IndividualProduct(**product_dict)
        return product

    def same_expiry_products(self, expiry_date, day_list):
        """
        :param: expiry_date: db.String of format dd/mm/yyyy
        :param day_list: list of product details for a given day expiration
        :return: individual product objects for that specific expiration date
        """
        out = list()
        new_day_list = self.normalise_product_details_list(day_list)
        #populate the product dict
        for item in new_day_list:
            if self.check_if_name(item):
                # found what we think is a product name
                product_dict = dict()
                product_dict['expiry_date'] = expiry_date
                if self.get_weight(item) is None:
                    # there is no weight data,
                    product_dict['weight'] = None
                    product_dict['name'] = item
                else:
                    # there is weight data
                    # we must add it as a tuple :(
                    weight = self.get_weight(item)
                    val = weight.value
                    unit = weight.unitCode
                    product_dict['weight'] = (val, unit)
                    length = len(str(val) + str(unit))
                    product_dict['name'] = item[:-length+1]
                continue

            elif self.merged_field_check(item):
                # this may be a merged field of quantity and price :(
                info = self.split_merged_field(item)
                product_dict['quantity'] = int(info[0])
                price_tuple = (info[1], self.price_currency)
                product_dict['price'] = price_tuple
                #this is the last field
                p = self.create_individual_product(product_dict)
                out.append(p)
                continue

            elif '/' in item:
                if len(item) == 3:
                    # this may be a regular quantity field
                    product_dict['quantity'] = int(self.get_quantity(item))
                    continue
                else:
                    # this may be a price per kg info, not interested
                    continue

            elif '.' in item and 'kg' not in item:
                # this may be a regular price field
                price_tuple = (item, self.price_currency)
                product_dict['price'] = price_tuple
        # function works on the assumption that a price indication is always the last item of a product detail

            p = self.create_individual_product(product_dict)
            out.append(p)

        return out

    def process_receipt(self):
        """
        :return: list of product objects for that receipt
        """
        # parse dictionary for each key of expiration and create a list of individual_products
        product_list = list()
        for key, value in self.calendar_dict.iteritems():
            products_by_expiration = self.same_expiry_products(key, value)
            for product in products_by_expiration:
                product_list.append(product)
        return product_list


class OcadoRecepitSchema(ma.ModelSchema):
    class Meta:
        model = OcadoReceipt

class Household(db.Model):
    """Object representing a household of more than one user"""

    __tablename__ = 'household'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    individualproducts = db.relationship('IndividualProduct', backref='product_household', lazy='dynamic')
    ocadoreceipts = db.relationship('OcadoReceipt', backref='receipt_household', lazy='dynamic')
    users = db.relationship('User', backref='user_household', lazy='joined')

    def __init__(self, name=None):
        """

        :param user: user object
        :param name: db.String to represent the household
        :return:
        """
        self.name = name

    def add_receipt(self, receipt_id):
        self.ocadoreceipts.append(receipt_id)

    def add_user(self, user_id):
        self.users.append(user_id)

    def add_individual_product(self, individual_product_id):
        self.individual_products.append(individual_product_id)


class HouseholdSchema(ma.ModelSchema):
    class Meta:
        model = Household


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

def add_receipt(email, receipt_payload):
    """
    :param user email
    :param receipt_payload: {seller:, file_pointer:, price_currency:}
    :return: receipt dict
    """
    # check if receipt was already created
    ocadoreceipt_schema = OcadoRecepitSchema()
    check = check_receipt_exists(receipt_payload)
    # fetch the database household object
    user = User.query.filter_by(email=email).first()
    household_id = user.household_id
    household = Household.query.filter_by(id=household_id).first()
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
