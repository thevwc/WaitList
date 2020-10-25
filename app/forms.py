# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
DateTimeField, DateField, SelectField, IntegerField, RadioField 
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, AnyOf, InputRequired, NumberRange, Length
from app.models import Member
from wtforms.fields.html5 import DateField
from wtforms import Form
from datetime import date, datetime

class LocalAddressPhone(FlaskForm):
    street = StringField('Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zip')
    village = StringField('Village')

class NewMember(FlaskForm):
        memberID = StringField('Village ID', [
            DataRequired(message='ID is required.'),
            Length(min=6,max=6,message='ID must be 6 characters.')])

        temporaryVillageID = BooleanField('Is this a temporary ID')

        temporaryIDexpirationDate = DateField('ID Expiration Date')
        firstName = StringField('First name', [
            DataRequired(message='First name is required.')])
        
        middleName = StringField('Middle name')
        lastName = StringField('Last name',[
            DataRequired(message='Last name is required.')])
        nickName = StringField('Nickname')
        dateJoined = DateField('Date joined',
            default=datetime.today)

        typeOfWork = SelectField('Type of work',[
            DataRequired(message='Please select a type of work.')],
            choices=[('General','General'),
                    ('Turning','Turning'),
                    ('Carving','Carving'),
                    ('Stained glass','Stained glass'),
                    ('Toys','Toys')])
        

        skillLevel = SelectField('Skill level',[
            DataRequired(message='Please select a skill level.')],
            choices=[('To be determined','0'),
                    ('Basic','1'),
                    ('Intermediate','2'),
                    ('Tradesman','3')])
        

        certificationDateRA = DateField('RA certification')
        certificationDateBW = DateField('BW certification')

        typeOfMembership = RadioField(
            'Type of membership',
             choices=[('1','Single membership'),('2','2nd family membership')],default='1')

        annualDues=StringField('Annual dues',default='$ 75.00')
        initiationFee=StringField('Initiation fee',default='$ 200.00')
        amtToCollect=StringField('Total amount')

        submit = SubmitField('Submit')
