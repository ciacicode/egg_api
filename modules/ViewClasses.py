__author__ = 'ciacicode'

from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, validators, DateTimeField, IntegerField, DecimalField
from flask_wtf.file import FileField


# create a class for the signup form
class SignUp(Form):
    email = StringField('email')
    password = PasswordField('password',[validators.DataRequired(), validators.EqualTo('password_confirm', message='Passwords must match'), validators.Length(min=6, max=20)])
    password_confirm = PasswordField('password_confirmation')
    submit = SubmitField('SignUp')

# create a class for the household creation form
class Household(Form):
    name = StringField('name')
    submit = SubmitField('Create')

# create a class for the signin form
class SignIn(Form):
    email = StringField('email')
    password = PasswordField('password')
    submit = SubmitField('SignIn')

# create a class for the file upload form
class FileUpload(Form):
    receipt = FileField('OcadoReceipt')
    submit = SubmitField('Upload')

# create a class for the single product add form
class AddProduct(Form):
    name = StringField('name')
    expiry_date = DateTimeField('expiry_date')
    weight = DecimalField('weight')
    unitCode = StringField('unitCode', [validators.Length(min=1, max=4)])
    quantity = IntegerField('quantity')
    purchase_date = DateTimeField('purchase_date')
    submit = SubmitField('Add')