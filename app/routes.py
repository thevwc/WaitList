# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from app.forms import LocalAddressPhone
from flask_bootstrap import Bootstrap


from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables
from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta


@app.route('/', defaults={'villageID':None})
@app.route('/index/', defaults={'villageID':None})
@app.route('/index/<villageID>/')
def index(villageID):
    # PREPARE LIST OF MEMBER NAMES AND VILLAGE IDs
    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF MEMBERS
    nameArray=[]
    sqlSelect = "SELECT Last_Name, First_Name, Member_ID FROM tblMember_Data "
    sqlSelect += "ORDER BY Last_Name, First_Name "
    
    nameList = db.engine.execute(sqlSelect)
    position = 0
    
    # NEED TO PLACE NAME IN AN ARRAY BECAUSE OF NEED TO CONCATENATE 
    for n in nameList:
        position += 1
        lastFirst = n.Last_Name + ', ' + n.First_Name + ' (' + n.Member_ID + ')'
        nameArray.append(lastFirst)
    
    # IF A VILLAGE ID WAS NOT PASSED IN DISPLAY THE INDEX.HTML FORM TO PROMPT FOR AN ID
    if villageID == None:
        return render_template("index.html",nameArray=nameArray)


    # IF A VILLAGE ID WAS PASSED IN ...
    # GET REQUEST TO POPULATE LOCAL ADDRESS PHONE EMAIL
    member = db.session.query(Member).filter(Member.Member_ID == villageID).first()
    if (member == None):
        print('No record for village ID ', villageID )
        return render_template("member.html",member='',nameArray=nameArray)
         

    hdgName = member.First_Name
    if member.Middle_Name is not None:
        if len(member.Middle_Name) > 0 :
            hdgName += ' ' + member.Middle_Name
    hdgName += ' ' + member.Last_Name
    if member.Nickname is not None:
        if len(member.Nickname) > 0 :
            hdgName += ' (' + member.Nickname + ')'

    # EMERGENCY NOTES   
    emergNotes = ''
    if member.Emerg_Pacemaker:
        emergNotes = 'Pacemaker'
    if member.Emerg_Stent:
        emergNotes += ', Stent'
    if member.Emerg_CABG :
        emergNotes += ', CABG'
    if member.Emerg_MI:
        emergNotes += ', MI'

    if member.Emerg_Other_Diagnosis:
        emergNotes += ', ' + member.Emerg_Other_Diagnosis
    if member.Emerg_Diabetes_Type_1:
        emergNotes += ', Diabetes Type 2'
    if member.Emerg_Diabetes_Type_2:
        emergNotes += ', Diabetes Type 2'
    if member.Emerg_Diabetes_Other:
        emergNotes += ', Diabetes Type Other'
    if member.Emerg_Medical_Alergies:
        emergNotes += ', ' + member.Emerg_Medical_Alergies
    if member.Emerg_No_Data_Provided:
        emergNotes += ', No data provided.'

    
    # TEST FOR TEMPORARY VILLAGE ID EXPIRATION DATE
    expireMsg = ''
    todays_date = datetime.today()

    if member.Temporary_Village_ID is not None:
        if member.Temporary_ID_Expiration_Date is not None:
            minus30 = member.Temporary_ID_Expiration_Date - timedelta(days=30)
            if minus30 < todays_date:
                expireMsg = 'Expires within 30 days'
            if member.Temporary_ID_Expiration_Date < todays_date:
                expireMsg = 'ID EXPIRED!'

    # SET BEGIN DATE TO 12 MONTHS PRIOR TO CURRENT DATE
    beginDateDAT = todays_date - timedelta(days=365)
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')

    todaySTR = todays_date.strftime('%m-%d-%Y')

    # print('Today-',todaySTR)
    # print('beginDateSTR-',beginDateSTR)

    # FUTURE MONITOR DUTY
    sqlFutureDuty = "SELECT format(Date_Scheduled,'ddd M/d/y') as DateScheduled, AM_PM, Duty, Shop_Abbr, Shop_Name FROM tblMonitor_Schedule "
    sqlFutureDuty += "LEFT JOIN tblShop_Names ON tblMonitor_Schedule.Shop_Number = tblShop_Names.Shop_Number "
    sqlFutureDuty += "WHERE Member_ID = '" + villageID + "' and Date_Scheduled >='" + todaySTR + "' "
    sqlFutureDuty += "ORDER BY Date_Scheduled DESC"

    #print('sqlFutureDuty-',sqlFutureDuty)

    futureDuty = db.engine.execute(sqlFutureDuty)
    # print('FUTURE DUTY')
    # for f in futureDuty:
    #     print(f.DateScheduled,f.AM_PM,f.Duty,f.Shop_Abbr)

    # PAST MONITOR DUTY
    sqlPastDuty = "SELECT format(Date_Scheduled,'ddd M/d/y') as DateScheduled, AM_PM, Duty, Shop_Abbr, Shop_Name, iif(No_Show = 1,'NS','') as NoShow "
    sqlPastDuty += " FROM tblMonitor_Schedule "
    sqlPastDuty += "LEFT JOIN tblShop_Names ON tblMonitor_Schedule.Shop_Number = tblShop_Names.Shop_Number "
    sqlPastDuty += "WHERE Member_ID = '" + villageID + "' and Date_Scheduled BETWEEN '" + beginDateSTR + "' and '" + todaySTR + "' "
    sqlPastDuty += "ORDER BY Date_Scheduled DESC"
    pastDuty = db.engine.execute(sqlPastDuty)
    # print('')
    # print('PAST DUTY')
    # for p in pastDuty:
    #     print(p.DateScheduled,p.AM_PM,p.Duty,p.Shop_Abbr)

    return render_template("member.html",member=member,hdgName=hdgName,nameArray=nameArray,emergNotes=emergNotes,expireMsg=expireMsg,futureDuty=futureDuty,pastDuty=pastDuty)
    
@app.route('/saveAddress', methods=['POST'])
def saveAddress():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zip']
    homePhone = request.form['homePhone']
    cellPhone = request.form['cellPhone']
    eMail = request.form['eMail']
    
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    fieldsChanged = 0

    if member.Address != street :
        member.Address = street
        fieldsChanged += 1

    if member.City != city :
        member.City = city
        fieldsChanged += 1

    if member.Zip != zipcode:
        member.Zip = zipcode
        fieldsChanged += 1

    if member.Home_Phone != homePhone :
        member.Home_Phone = homePhone
        fieldsChanged += 1


    if member.Cell_Phone != cellPhone :
        member.Cell_Phone = cellPhone
        fieldsChanged += 1

    if member.eMail != eMail :
        member.eMail = eMail
        fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            flash("Changes successful","success")
        except Exception as e:
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))

@app.route('/saveAltAddress', methods=['POST'])
def saveAltAddress():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    street = request.form['altStreet']
    city = request.form['altCity']
    state = request.form['altState']
    country=request.form['altCountry']
    zipcode = request.form['altZip']
    phone = request.form['altPhone']
    
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # INITIALIZE COUNTER FOR NUMBER OF FIELDS CHANGED
    fieldsChanged = 0

    # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    if member.Alt_Adddress != street :
        member.Alt_Adddress = street
        fieldsChanged += 1

    if member.Alt_City != city :
        member.Alt_City = city
        fieldsChanged += 1

    if member.Alt_Country != country :
        member.Alt_Country = country
        fieldsChanged += 1

    if member.Alt_Zip != zipcode:
        member.Alt_Zip = zipcode
        fieldsChanged += 1

    if member.Alt_Phone != phone :
        member.Alt_Phone = phone
        fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            flash("Changes successful","success")
        except Exception as e:
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))

@app.route('/saveEmergency', methods=['POST'])
def saveEmergency():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    contact = request.form['emergContact']
    phone = request.form['emergPhone']

     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    fieldsChanged = 0
    if member.Emerg_Name != contact:
        member.Emerg_Name = contact
        fieldsChanged += 1 

    if member.Emerg_Phone != phone:
        member.Emerg_Phone = phone
        fieldsChanged += 1     

    #  add code for bit fields

    if fieldsChanged > 0:
        try:
            db.session.commit()
            flash("Changes successful","success")
        except Exception as e:
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))

@app.route('/saveMemberStatus', methods=['POST'])
def saveMemberStatus():
    print('saveMemberStatus routine')
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    

    fieldsChanged = 0
    if fieldsChanged > 0:
        try:
            db.session.commit()
            flash("Changes successful","success")
        except Exception as e:
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))


@app.route('/saveCertification', methods=['POST'])
def saveCertification():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()

    fieldsChanged = 0
    if fieldsChanged > 0:
        try:
            db.session.commit()
            flash("Changes successful","success")
        except Exception as e:
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))


@app.route('/saveMonitorDuty', methods=['POST'])
def saveMonitorDuty():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    jan=request.form['jan']
    feb=request.form['feb']
    mar=request.form['mar']
    apr=request.form['apr']
    may=request.form['may']
    jun=request.form['jun']
    jul=request.form['jul']
    aug=request.form['aug']
    sep=request.form['sep']
    oct=request.form['oct']
    nov=request.form['nov']
    dec=request.form['dec']
    
    if request.form['action'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    
    if (jan=='True'):
        member.Jan_resident = True
    else:
        member.Jan_resident = False
    if (feb=='True'):
        member.Feb_resident = True
    else:
        member.Feb_resident = False
    if (mar=='True'):
        member.Mar_resident = True
    else:
        member.Mar_resident = False
    if (apr=='True'):
        member.Apr_resident = True
    else:
        member.Apr_resident = False
    if (may=='True'):
        member.May_resident = True
    else:
        member.May_resident = False
    if (jun=='True'):
        member.Jun_resident = True
    else:
        member.Jun_resident = False
    if (jul=='True'):
        member.Jul_resident = True
    else:
        member.Jul_resident = False
    if (aug=='True'):
        member.Aug_resident = True
    else:
        member.Aug_resident = False
    if (sep=='True'):
        member.Sep_resident = True
    else:
        member.Sep_resident = False
    if (oct=='True'):
        member.Oct_resident = True
    else:
        member.Oct_resident = False
    if (nov=='True'):
        member.Nov_resident = True
    else:
        member.Nov_resident = False
    if (dec=='True'):
        member.Dec_resident = True
    else:
        member.Dec_resident = False
   
    try:
        db.session.commit()
        flash("Changes successful","success")
    except Exception as e:
        flash("Could not update member data.","danger")
        db.session.rollback()
    
    return redirect(url_for('index',villageID=memberID))