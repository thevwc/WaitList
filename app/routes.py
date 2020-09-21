# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from app.forms import LocalAddressPhone
from flask_bootstrap import Bootstrap


from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables, NotesToMembers
from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta

from flask_mail import Mail, Message
mail=Mail(app)

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
        return render_template("member.html",member="",nameArray=nameArray)
        # return render_template("index.html",nameArray=nameArray)


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
   
    print('date joined type and value - ',type(member.Date_Joined),member.Date_Joined)

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
    print('localAction cancelled - ',request.form['localAction'])
    if request.form['localAction'] == 'CANCEL':
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
    
    if request.form['altAction'] == 'CANCEL':
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
    if request.form.get('emergDefib') == 'True':
        defibrillatorStatus = True
    else:
        defibrillatorStatus = False

    if request.form.get('emergNoData') == 'True':
        noEmergData = True
    else:
        noEmergData = False

    #  DID USER CANCEL?
    if request.form['emergAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    
    fieldsChanged = 0
    if member.Emerg_Name != contact:
        member.Emerg_Name = contact
        fieldsChanged += 1 

    if member.Emerg_Phone != phone:
        member.Emerg_Phone = phone
        fieldsChanged += 1    

    if defibrillatorStatus != member.Defibrillator_Trained:
        member.Defibrillator_Trained = defibrillatorStatus
        fieldsChanged += 1

    if noEmergData != member.Emerg_No_Data_Provided:
        member.Emerg_No_Data_Provided = noEmergData
        fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            print('Changes successful')
            flash("Changes successful","success")
        except Exception as e:
            print('Could not update emergency data')
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))

@app.route('/saveMemberStatus', methods=['POST'])
def saveMemberStatus():
    print('saveMemberStatus routine')
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    print('duesPaid',request.form.get('duesPaid'))
    print('dateJoined',request.form.get('dateJoined'))
    print('volunteer',request.form.get('volunteer'))
    print('inactive',request.form.get('inactive'))
    print('inactiveDate',request.form.get('inactiveDate'))
    print('deceased',request.form.get('deceased'))
    print('restricted',request.form.get('restricted'))
    print('reasonRestricted',request.form.get('reasonRestricted'))
    print('villagesWaiverSigned',request.form.get('villagesWaiverSigned'))
    print('waiverDateSigned',request.form.get('waiverDateSigned'))

    if request.form['memberAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))
    
    if request.form.get('duesPaid') == 'True':
        duesPaid = True
    else:
        duesPaid = False 

    dateJoined = request.form.get('dateJoined')

    if request.form.get('restricted') == 'True':
        restricted = True
    else:
        reasonRestricted = False
    
    if request.form.get('volunteer') == 'True':
        volunteer = True
    else:
        volunteer = False

    if request.form.get('inactive') == 'True':
        inactive = True
    else:
        inactive = False

    inactiveDate = request.form.get('inactiveDate')

    if request.form.get('deceased') == 'True':
        deceased = True
    else:
        deceased = False
    
    if request.form.get('restricted') == 'True':
        restricted = True
    else:
        restricted = False
    
    reasonRestricted = request.form.get('reasonRestricted')

    if request.form.get('villagesWaiverSigned') == 'True':
        villagesWaiverSigned = True
    else:
        villagesWaiverSigned = False
    
    waiverDateSigned = request.form.get('waiverDateSigned')


     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    fieldsChanged = 0

    if duesPaid != member.Dues_Paid:
        logChange('Dues Paid',memberID,duesPaid,member.Dues_Paid)
        member.Dues_Paid = duesPaid
        fieldsChanged += 1

    if dateJoined != member.Date_Joined:
        logChange('Date Joined',memberID,dateJoined,member.Date_Joined)
        member.Date_Joined = dateJoined
        fieldsChanged += 1

    if volunteer != None:
        if volunteer != member.NonMember_Volunteer:
            logChange('Volunteer',memberID,volunteer,member.NonMember_Volunteer)
            member.NonMember_Volunteer = volunteer
            fieldsChanged += 1

    if inactive != None:
        if inactive != member.Inactive:
            logChange('Inactive',memberID,inactive,member.Inactive)
            member.Inactive = inactive
            fieldsChanged += 1   

    if inactiveDate != None:
        if inactiveDate != member.Inactive_Date:
            logChange('Inactive Date',memberID,inactiveDate,member.Inactive_Date)
            member.Inactive_Date = inactiveDate
            fieldsChanged += 1 

    if deceased != None:
        if deceased != member.Deceased:
            logChange('Deceased',memberID,deceased,member.Deceased)
            member.Deceased = deceased
            fieldsChanged += 1

    if restricted != None:
        if restricted != member.Restricted_From_Shop:
            logChange('Restricted',memberID,restricted,member.Restricted_From_Shop)
            member.Restricted_From_Shop = restricted
            fieldsChanged += 1

    if reasonRestricted != None:
        if reasonRestricted != member.Reason_For_Restricted_From_Shop:
            logChange('Reason Restricted',memberID,reasonRestricted,member.Reason_For_Restricted_From_Shop)
            member.Reason_For_Restricted_From_Shop = reasonRestricted
            fieldsChanged += 1

    if villagesWaiverSigned != None:
        if villagesWaiverSigned != member.Villages_Waiver_Signed:
            logChange('Waiver Signed',memberID,villagesWaiverSigned,member.Villages_Waiver_Signed)
            member.Villages_Waiver_Signed = villagesWaiverSigned
            fieldsChanged += 1

    if waiverDateSigned != None:
        if waiverDateSigned != member.Villages_Waiver_Date_Signed:
            logChange('Waiver - Date Signed',memberID,waiverDateSigned,member.Villages_Waiver_Date_Signed)
            member.Villages_Waiver_Date_Signed = waiverDateSigned
            fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            print ("Changes successful")
            flash("Changes successful","success")
        # except SQLAlchemyError as e:
        #     error = str(e.__dict__['orig'])
        #     return error
        except Exception as e:
            print ("Changes NOT successful\n",e)
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))


@app.route('/saveCertification', methods=['POST'])
def saveCertification():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    if request.form['certificationAction'] == 'CANCEL':
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
    
    if request.form['monitorAction'] == 'CANCEL':
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

@app.route("/getNoteToMember")
def getNoteToMember():
    memberID = request.args.get('memberID')
    currentNote = db.session.query(NotesToMembers).filter(NotesToMembers.memberID == memberID).first()
    if (currentNote):
        msg = currentNote.noteToMember
        msg += '\n-----------------------------------------------\n'
        return jsonify(msg=msg)
    return make_response('Nothing')

@app.route("/processNoteToMember")
def processNoteToMember():
    todays_date = datetime.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    
    showAtCheckIn=request.args.get('showAtCheckIn')
    sendEmail=request.args.get('sendEmail')
    memberID=request.args.get('memberID')
    emailAddress = request.args.get('emailAddress')
    msg = request.args.get('msg')
    response = ""

    # PREPARE A NOTE TO DISPLAY AT CHECK-IN, IF REQUESTED
    if (showAtCheckIn == 'true'):
        currentNote = db.session.query(NotesToMembers).filter(NotesToMembers.memberID == memberID).first()
        if (currentNote != None):
            db.session.delete(currentNote)
            db.session.commit()

        # CREATE A NEW MSG RECORD; ANY OLD DATA WILL REMAIN AT BEGINNING OF MESSAGE.
        try:
            newNote = NotesToMembers(
                memberID = memberID, 
                noteToMember = msg)
            db.session.add(newNote)
            db.session.commit()
            response = "New note successfully created!"
            
        except SQLAlchemyError as e:
            newNote.rollback()
            return make_response(f"ERROR - Could not add a new note.")
 
    # PREPARE AN EMAIL, IF REQUESTED
    if (sendEmail == 'true'):
        # PREPARE AN EMAIL
        recipient = eMailAddress
        #recipient = ("Richard Hartley", "hartl1r@gmail.com")
        #bcc=("Woodshop","villagesWoodShop@embarqmail.com")
        recipientList = []
        recipientList.append(recipient)
        message = Message('Hello', sender = 'hartl1r@gmail.com', recipients = recipientList)
        message.subject = "Note from front desk"
        message.body = msg
        mail.send(message)
        response += "/nEmail sent."

    return make_response (f"{response}")
    

def logChange(colName,memberID,beforeData,afterData):
    # get staff ID, date, write change
    print('log - ',colName,"|",memberID,"|",beforeData,"|",afterData),"|"
    return

@app.route("/newMemberApplication")
def newMemberApplication():
    todays_date = datetime.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    return render_template("newMemberApplication.html")