# models.py 

from datetime import datetime 
from time import time
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, func, Column, extract, ForeignKey
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.ext.hybrid import hybrid_property
#from flask_login import UserMixin
#import jwt
from app import app

#@login.user_loader
#def load_user(id):
#    return User.query.get(int(id))

    

# @staticmethod
# def verify_reset_password_token(token):
#     try:
#         id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
#     except:
#         return
#     return User.query.get(id)

class ControlVariables(db.Model):
    __tablename__ = 'tblControl_Variables'
    __table_args__ = {"schema": "dbo"}
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Last_Acceptable_Monitor_Training_Date = db.Column(db.DateTime)
        

class Member(db.Model):
    __tablename__ = 'tblMember_Data'
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Member_ID = db.Column(db.String(6),
         index=True,
         unique=True)
    Last_Name = db.Column(db.String(25))
    First_Name = db.Column(db.String(25))
    Middle_Name = db.Column(db.String(25))
    Nickname = db.Column(db.String(25))
    Initials = db.Column(db.String(3))
    Date_Joined = db.Column(db.DateTime)
    Certified = db.Column(db.Boolean)
    Certification_Training_Date = db.Column(db.DateTime)
    Certified_2 = db.Column(db.Boolean)
    Certification_Training_Date_2 = db.Column(db.DateTime)
    Address = db.Column(db.String(30))
    City = db.Column(db.String(25))
    State = db.Column(db.String(2))
    Zip = db.Column(db.String(10))
    Village = db.Column(db.String(30))

    Home_Phone = db.Column(db.String(14))
    Cell_Phone = db.Column(db.String(14))
    eMail = db.Column(db.String(50))
    Dues_Paid=db.Column(db.Boolean)
    NonMember_Volunteer=db.Column(db.Boolean)
    Restricted_From_Shop = db.Column(db.Boolean)
    Reason_For_Restricted_From_Shop = db.Column(db.String(255))
    Last_Monitor_Training = db.Column(db.DateTime)
    Deceased = db.Column(db.Boolean)
    Inactive = db.Column(db.Boolean)
    Inactive_Date = db.Column(db.DateTime)
    Villages_Waiver_Signed = db.Column(db.Boolean)
    Villages_Waiver_Date_Signed = db.Column(db.DateTime)
    Jan_resident = db.Column(db.Boolean)
    Feb_resident = db.Column(db.Boolean)
    Mar_resident = db.Column(db.Boolean)
    Apr_resident = db.Column(db.Boolean)
    May_resident = db.Column(db.Boolean)
    Jun_resident = db.Column(db.Boolean)
    Jul_resident = db.Column(db.Boolean)
    Aug_resident = db.Column(db.Boolean)
    Sep_resident = db.Column(db.Boolean)
    Oct_resident = db.Column(db.Boolean)
    Nov_resident = db.Column(db.Boolean)
    Dec_resident = db.Column(db.Boolean)

    Alt_Adddress = db.Column(db.String(30))
    Alt_City = db.Column(db.String(25))
    Alt_State = db.Column(db.String(2))
    Alt_Zip = db.Column(db.String(10))
    Alt_Country = db.Column(db.String(30))
    Alt_Phone = db.Column(db.String(14))
    
    Emerg_Name = db.Column(db.String(30))
    Emerg_Phone = db.Column(db.String(14))
    Emerg_Pacemaker = db.Column(db.Boolean)
    Emerg_Stent = db.Column(db.Boolean)
    Emerg_CABG = db.Column(db.Boolean)
    Emerg_MI = db.Column(db.Boolean)
    Emerg_Other_Diagnosis = db.Column(db.String(50))
    Emerg_Diabetes_Type_1 = db.Column(db.Boolean)
    Emerg_Diabetes_Type_2 = db.Column(db.Boolean)
    Emerg_Diabetes_Other = db.Column(db.String(50))
    Emerg_Medical_Alergies = db.Column(db.String(255))
    Emerg_No_Data_Provided = db.Column(db.Boolean)
    Defibrillator_Trained = db.Column(db.Boolean)
    Monitor_Duty_Notes = db.Column(db.String(255))
    Requires_Tool_Crib_Duty = db.Column(db.Boolean)
    Member_Notes = db.Column(db.String(255))
    Monitor_Coordinator = db.Column(db.Boolean)
    Default_Type_Of_Work = db.Column(db.String(50))

    Monitor_Duty_Waiver_Reason = db.Column(db.String(50))
    Monitor_Duty_Waiver_Expiration_Date = db.Column(db.DateTime)
    
    Temporary_Village_ID = db.Column(db.Boolean)
    Temporary_ID_Expiration_Date = db.Column(db.DateTime)

    fullName = column_property(First_Name + " " + Last_Name)
    # Relationships
    #activities = db.relationship('MemberActivity', backref='member')
    def wholeName(self):
        return self.lastName + ", " + self.firstName 
  
class ShopName(db.Model):
    __tablename__ = 'tblShop_Names'
    __table_args__ = {"schema": "dbo"}
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Shop_Name = db.Column(db.String(30))

class MemberActivity(db.Model):
    __tablename__ = 'tblMember_Activity'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer, primary_key=True)
    Member_ID = db.Column(db.String(6), db.ForeignKey('member.Member_ID'))
    Check_In_Date_Time = db.Column(db.DateTime)
    Check_Out_Date_Time = db.Column(db.DateTime)
    Type_Of_Work = db.Column(db.String(20))
    Shop_Number = db.Column(db.Integer)
    Door_Used = db.Column(db.String(5))

class MonitorSchedule(db.Model):
    __tablename__ = 'tblMonitor_Schedule'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer,autoincrement=True)
    Member_ID = db.Column(db.String(6), primary_key=True)
    Date_Scheduled = db.Column(db.DateTime, primary_key=True)
    AM_PM = db.Column(db.String(2), primary_key=True)
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Monitor_Notes = db.Column(db.String(255))
    Duty = db.Column(db.String(20))
    No_Show = db.Column(db.Boolean)
    Optional = db.Column(db.Boolean)

class MonitorScheduleTransaction(db.Model):
    __tablename__ = 'tblMonitor_Scheduled_Transactions'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer,primary_key=True, autoincrement=True)
    Transaction_Date = db.Column(db.DateTime)
    Week_Number = db.Column(db.Integer)
    Staff_ID = db.Column(db.String(6))
    Member_ID = db.Column(db.String(6))
    Transaction_Type = db.Column(db.String(10))
    Date_Scheduled = db.Column(db.DateTime)
    AM_PM = db.Column(db.String(2))
    Duty = db.Column(db.String(20))
    
class MonitorWeekNote(db.Model):
    __tablename__ = 'monitorWeekNotes'
    __table_args__ = {"schema":"dbo"}
    ID = db.Column(db.Integer, primary_key=True)
    Shop_Number = db.Column(db.Integer)
    WeekOf = db.Column(db.DateTime)
    Author_ID = db.Column(db.String(6))
    Date_Of_Change = db.Column(db.DateTime)
    Schedule_Note = db.Column(db.String(255))


class ShopDates(db.Model):
    __tablename__ = 'tblShop_Dates'
    __table_args__ = {"schema": "dbo"}
    Shop_Number = db.Column(db.Integer, primary_key=True)
    MM_DD_YYYY = db.Column(db.DateTime, primary_key=True)
    Status  = db.Column(db.String(10))
    Reason = db.Column(db.String(255))
    SM_AM_REQD = db.Column(db.Integer)
    SM_PM_REQD = db.Column(db.Integer)
    TC_AM_REQD = db.Column(db.Integer)
    TC_PM_REQD = db.Column(db.Integer)

class CoordinatorsSchedule(db.Model):
    __tablename__ = 'coordinatorsSchedule'
    __table_args__ = {"schema":"dbo"}
    ID = db.Column(db.Integer)
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Start_Date = db.Column(db.DateTime, primary_key=True)
    End_Date = db.Column(db.DateTime)
    Coordinator_ID = db.Column(db.String(6))

class NotesToMembers(db.Model):
    __tablename__ = "notesToMembers"
    __table_args__={"schema":"dbo"}
    memberID = db.Column(db.String(6), primary_key=True)
    noteToMember = db.Column(db.String(255))
