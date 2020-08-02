# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, AnyOf, InputRequired, NumberRange
from app.models import Member
from wtforms.fields.html5 import DateField
from wtforms import Form


class LocalAddressPhone(FlaskForm):
    street = StringField('Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zip')
    village = StringField('Village')