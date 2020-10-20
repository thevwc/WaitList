# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from app.forms import LocalAddressPhone
from flask_bootstrap import Bootstrap


from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables, NotesToMembers, MemberTransactions
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
    try:
        nameList = db.engine.execute(sqlSelect)
    except Exception as e:
        print('ERROR in retrieving member list.')
        flash("Could not retrieve member list.","danger")
        return 'ERROR in index function.'
    position = 0
    if nameList == None:
        print('empty nameList')

    # NEED TO PLACE NAME IN AN ARRAY BECAUSE OF NEED TO CONCATENATE 
    for n in nameList:
        position += 1
        if n.First_Name == None:
            lastFirst = n.Last_Name
        else:
            lastFirst = n.Last_Name + ', ' + n.First_Name + ' (' + n.Member_ID + ')'
        nameArray.append(lastFirst)
        
    # IF A VILLAGE ID WAS NOT PASSED IN, DISPLAY THE INDEX.HTML FORM TO PROMPT FOR AN ID
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

    # TEST FOR TEMPORARY VILLAGE ID EXPIRATION DATE
    expireMsg = ''
    #todays_date = datetime.today()
    todays_date = date.today()

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
   
    
    
    # DOES THE MEMBER HAVE AN UNEXPIRED MONITOR WAIVER?
    hasWaiver = False
    todaysDate = date.today() 
    
    if member.Monitor_Duty_Waiver_Expiration_Date == None:
        hasWaiver = False
    else:
        if member.Monitor_Duty_Waiver_Expiration_Date > todaysDate:
            hasWaiver = True
        else:
            hasWaiver = False

       
    # DOES THE MEMBER NEED TRAINING FOR EITHER LOCATION?
    RAtrainingNeeded = ''
    BWtrainingNeeded = ''
    if hasWaiver == False:
        # DOES MEMBER NEED TRAINING FOR ROLLING ACRES?
        if member.Last_Monitor_Training == None:
            RAtrainingNeeded = 'Training Needed'
        else:
            RAlastAcceptableTrainingDate = db.session.query(ControlVariables.Last_Acceptable_Monitor_Training_Date).filter(ControlVariables.Shop_Number == 1).scalar()
            #print('type training - ',type(member.Last_Monitor_Training))
            #print('type acceptable - ',type(RAlastAcceptableTrainingDate))
            if member.Last_Monitor_Training < RAlastAcceptableTrainingDate:
                RAtrainingNeeded = 'Training Needed'
        #print('RAlastAcceptableTrainingDate - ',RAlastAcceptableTrainingDate,RAtrainingNeeded)

        # DOES MEMBER NEED TRAINING FOR BROWNWOOD
        if member.Last_Monitor_Training_Shop_2 == None:
            BWtrainingNeeded = 'Training Needed'
        else:
            BWlastAcceptableTrainingDate = db.session.query(ControlVariables.Last_Acceptable_Monitor_Training_Date).filter(ControlVariables.Shop_Number == 2).scalar()
            if member.Last_Monitor_Training_Shop_2 < BWlastAcceptableTrainingDate:
                BWtrainingNeeded = 'Training Needed'
            #print('BWlastAcceptableTrainingDate - ',BWlastAcceptableTrainingDate)

    return render_template("member.html",member=member,hdgName=hdgName,nameArray=nameArray,expireMsg=expireMsg,
    futureDuty=futureDuty,pastDuty=pastDuty,RAtrainingNeeded=RAtrainingNeeded,BWtrainingNeeded=BWtrainingNeeded)
    
@app.route('/saveAddress', methods=['POST'])
def saveAddress():
    
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    staffID = request.form['staffID']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zip']
    homePhone = request.form['homePhone']
    cellPhone = request.form['cellPhone']
    eMail = request.form['eMail']

    # print ('waiver - ',request.form.get('villagesWaiverSigned'))

    if request.form.get('villagesWaiverSigned') == 'True':
        villagesWaiverSigned = True
    else:
        villagesWaiverSigned = False
    print('waiver date - ',request.form.get('villagesWaiverDateSigned'))
    villagesWaiverDateSigned = request.form.get('villagesWaiverDateSigned')

    # WAS ACTION CANCELLED?
    if request.form['localAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    fieldsChanged = 0

    if member.Address != street :
        logChange(staffID,'Street',memberID,street,member.Address)
        member.Address = street
        fieldsChanged += 1

    if member.City != city :
        logChange(staffID,'City',memberID,city,member.City)
        member.City = city
        fieldsChanged += 1

    if member.Zip != zipcode:
        logChange(staffID,'Zipcode',memberID,zipcode,member.Zip)
        member.Zip = zipcode
        fieldsChanged += 1

    if member.Home_Phone != homePhone :
        logChange(staffID,'Home Phone',memberID,homePhone,member.Home_Phone)
        member.Home_Phone = homePhone
        fieldsChanged += 1


    if member.Cell_Phone != cellPhone :
        logChange(staffID,'Cell Phone',memberID,cellPhone,member.Cell_Phone)
        member.Cell_Phone = cellPhone
        fieldsChanged += 1

    if member.eMail != eMail :
        logChange(staffID,'Email',memberID,eMail,member.eMail)
        member.eMail = eMail
        fieldsChanged += 1

    if villagesWaiverSigned != None:
        if villagesWaiverSigned != member.Villages_Waiver_Signed:
            logChange(staffID,'Waiver Signed',memberID,villagesWaiverSigned,member.Villages_Waiver_Signed)
            member.Villages_Waiver_Signed = villagesWaiverSigned
            fieldsChanged += 1

    if villagesWaiverDateSigned != None:
        if villagesWaiverDateSigned != member.Villages_Waiver_Date_Signed:
            logChange(staffID,'Waiver - Date Signed',memberID,villagesWaiverDateSigned,member.Villages_Waiver_Date_Signed)
            print(villagesWaiverDateSigned)
            # if villagesWaiverDateSigned == '1900-01-01':
            member.Villages_Waiver_Date_Signed = None 
            #else:
            member.Villages_Waiver_Date_Signed = villagesWaiverDateSigned
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
    staffID = request.form['staffID']
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
    try: 
        member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    except Exception as e:
        print('ERROR - could not read record for member # ',memberID + '/n'+e)
    if member.Alt_Adddress != street :
        logChange(staffID,'Alt Street',memberID,street,member.Alt_Adddress)
        member.Alt_Adddress = street
        fieldsChanged += 1

    if member.Alt_City != city :
        logChange(staffID,'Alt City',memberID,city,member.Alt_City)
        member.Alt_City = city
        fieldsChanged += 1

    if member.Alt_State != state :
        logChange(staffID,'Alt State',memberID,state,member.Alt_State)
        member.Alt_State = state
        fieldsChanged += 1

    if member.Alt_Country != country :
        logChange(staffID,'Alt Country',memberID,country,member.Alt_Country)
        member.Alt_Country = country
        fieldsChanged += 1

    if member.Alt_Zip != zipcode:
        logChange(staffID,'Alt Zipcode',memberID,zipcode,member.Alt_Zip)
        member.Alt_Zip = zipcode
        fieldsChanged += 1

    if member.Alt_Phone != phone :
        logChange(staffID,'Alt Phone',memberID,phone,member.Alt_Phone)
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
    
    # show what is in form for testing -
    print('request.form - ', request.form)
    print ('.........................................')

    data = request.form
    for key, value in data.items():
        print("received", key, "with value", value)

    print ('otherDiagnosis - ', request.form['otherDiagnosis'])
    
    #  DID USER CANCEL?
    memberID = request.form['memberID']
    if request.form['emergAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # GET DATA FROM FORM
    staffID = request.form['staffID']
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

    if request.form.get('pacemaker') == 'True':
        pacemaker = True
    else:
        pacemaker = False
    
    if request.form.get('stent') == 'True':
        stent = True
    else:
        stent = False

    if request.form.get('CABG') == 'True':
        CABG = True
    else:
        CABG = False

    if request.form.get('MI') == 'True':
        MI = True
    else:
        MI = False
    
    if request.form.get('diabetes1') == 'True':
        diabetes1 = True
    else:
        diabetes1 = False
    
    if request.form.get('diabetes2') == 'True':
        diabetes2 = True
    else:
        diabetes2 = False

    otherDiagnosis = request.form['otherDiagnosis']
    diabetesOther = request.form['diabetesOther']
    alergies = request.form['alergies']

     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    
    fieldsChanged = 0
    if member.Emerg_Name != contact:
        member.Emerg_Name = contact
        fieldsChanged += 1 

    if member.Emerg_Phone != phone:
        member.Emerg_Phone = phone
        fieldsChanged += 1    

    print('defibrillatorStatus - ',defibrillatorStatus, type(defibrillatorStatus))
    print('member.Defibrillator_Trained - ',member.Defibrillator_Trained,type(member.Defibrillator_Trained))

    if defibrillatorStatus != member.Defibrillator_Trained:
        logChange(staffID,'Defibrillator Trained',memberID,defibrillatorStatus,member.Defibrillator_Trained)
        member.Defibrillator_Trained = defibrillatorStatus
        fieldsChanged += 1

    if noEmergData != member.Emerg_No_Data_Provided:
        logChange(staffID,'No Data Provided',memberID,noEmergData,member.Emerg_No_Data_Provided)
        member.Emerg_No_Data_Provided = noEmergData
        fieldsChanged += 1
    
    if pacemaker != member.Emerg_Pacemaker: 
        logChange(staffID,'Pacemaker',memberID,pacemaker,member.Emerg_Pacemaker)
        member.Emerg_Pacemaker = pacemaker
        fieldsChanged += 1

    if stent != member.Emerg_Stent: 
        logChange(staffID,'Stent',memberID,stent,member.Emerg_Stent)
        member.Emerg_Stent = stent
        fieldsChanged += 1

    if CABG != member.Emerg_CABG: 
        logChange(staffID,'CABG',memberID,CABG,member.Emerg_CABG)
        member.Emerg_CABG = CABG
        fieldsChanged += 1

    if MI != member.Emerg_MI: 
        logChange(staffID,'MI',memberID,MI,member.Emerg_MI)
        member.Emerg_MI = MI
        fieldsChanged += 1

    print('diabetes1 - ',diabetes1,type(diabetes1))
    print('member.Emerg_Diabetes_Type_1 - ',member.Emerg_Diabetes_Type_1,type(member.Emerg_Diabetes_Type_1))

    if diabetes1 != member.Emerg_Diabetes_Type_1: 
        logChange(staffID,'diabetes1',memberID,diabetes1,member.Emerg_Diabetes_Type_1)
        member.Emerg_Diabetes_Type_1 = diabetes1
        fieldsChanged += 1

    if diabetes2 != member.Emerg_Diabetes_Type_2: 
        logChange(staffID,'diabetes2',memberID,diabetes2,member.Emerg_Diabetes_Type_2)
        member.Emerg_Diabetes_Type_2 = diabetes2
        fieldsChanged += 1

    if otherDiagnosis != member.Emerg_Other_Diagnosis:
        logChange(staffID,'otherDiagnosis',memberID,otherDiagnosis,member.Emerg_Other_Diagnosis)
        member.Emerg_Other_Diagnosis = otherDiagnosis
        fieldsChanged += 1

    if diabetesOther != member.Emerg_Diabetes_Other:
        logChange(staffID,'diabetesOther',memberID,diabetesOther,member.Emerg_Diabetes_Other)
        member.Emerg_Diabetes_Other = diabetesOther
        fieldsChanged += 1

    if alergies != member.Emerg_Medical_Alergies:
        logChange(staffID,'alergies',memberID,alergies,member.Emerg_Medical_Alergies)
        member.Emerg_Medical_Alergies = alergies
        fieldsChanged += 1

    # IF ANY FIELDS CHANGED, SAVE CHANGES
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
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    if request.form['memberAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))
    
    
    staffID = request.form['staffID']
    
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


     # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    if member == None:
        print("ERROR - Member "+memberID+" not found.")
    fieldsChanged = 0
    
    if duesPaid != member.Dues_Paid:
        logChange(staffID,'Dues Paid',memberID,duesPaid,member.Dues_Paid)
        member.Dues_Paid = duesPaid
        fieldsChanged += 1

    if dateJoined != member.Date_Joined:
        logChange(staffID,'Date Joined',memberID,dateJoined,member.Date_Joined)
        member.Date_Joined = dateJoined
        fieldsChanged += 1

    if volunteer != None:
        if volunteer != member.NonMember_Volunteer:
            logChange(staffID,'Volunteer',memberID,volunteer,member.NonMember_Volunteer)
            member.NonMember_Volunteer = volunteer
            fieldsChanged += 1
    
    if inactive != None:
        if inactive != member.Inactive:
            logChange(staffID,'Inactive',memberID,inactive,member.Inactive)
            member.Inactive = inactive
            fieldsChanged += 1   

    if inactiveDate != None:
        if inactiveDate != member.Inactive_Date:
            logChange(staffID,'Inactive Date',memberID,inactiveDate,member.Inactive_Date)
            member.Inactive_Date = inactiveDate
            fieldsChanged += 1 

    if deceased != None:
        if deceased != member.Deceased:
            logChange(staffID,'Deceased',memberID,deceased,member.Deceased)
            member.Deceased = deceased
            fieldsChanged += 1

    if restricted != None:
        if restricted != member.Restricted_From_Shop:
            logChange(staffID,'Restricted',memberID,restricted,member.Restricted_From_Shop)
            member.Restricted_From_Shop = restricted
            fieldsChanged += 1

    if reasonRestricted != None:
        if reasonRestricted != member.Reason_For_Restricted_From_Shop:
            logChange(staffID,'Reason Restricted',memberID,reasonRestricted,member.Reason_For_Restricted_From_Shop)
            member.Reason_For_Restricted_From_Shop = reasonRestricted
            fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            print ("Changes successful")
            flash("Changes successful","success")
        except Exception as e:
            print ("Changes NOT successful\n",e)
            flash("Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))


@app.route('/saveCertification', methods=['POST'])
def saveCertification():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    staffID = request.form['staffID']
    if request.form['certificationAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    certifiedRAdate = request.form.get('certifiedRAdate')
    certifiedBWdate = request.form.get('certifiedBWdate')
    
    if request.form.get('certifiedRA') == 'True':
        certifiedRA = True
    else:
        certifiedRA = False

    if request.form.get('certifiedBW') == 'True':
        certifiedBW = True
    else:
        certifiedBW = False

    if request.form.get('willSubRA') == 'True':
        willSubRA = True
    else:
        willSubRA = False

    if request.form.get('willSubBW') == 'True':
        willSubBW = True
    else:
        willSubBW = False

    RAmonitorTrainingDate = request.form.get('RAmonitorTrainingDate')    
    BWmonitorTrainingDate = request.form.get('BWmonitorTrainingDate')    
    
    typeOfWork = request.form.get('typeOfWorkSelecterName')

    skillLevel = request.form.get('skillLevelSelecterName')
    waiverExpirationDate = request.form.get('waiverExpirationDate')
    waiverReason = request.form.get('waiverReason')

    # GET MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    fieldsChanged = 0
     
    if certifiedRA != member.Certified:
        logChange(staffID,'Certified RA',memberID,certifiedRA,member.Certified)
        member.Certified = certifiedRA
        fieldsChanged += 1

    if certifiedBW != member.Certified_2:
        logChange(staffID,'Certified BW',memberID,certifiedBW,member.Certified_2)
        member.Certified_2 = certifiedBW
        fieldsChanged += 1

    if certifiedRAdate != member.Certification_Training_Date:
        logChange(staffID,'RA certification',memberID,certifiedRAdate,member.Certification_Training_Date)
        if certifiedRAdate == '':
            member.Certification_Training_Date = None
        else:
            member.Certification_Training_Date = certifiedRAdate
        fieldsChanged += 1
    
    if certifiedBWdate != member.Certification_Training_Date_2:
        logChange(staffID,'BW certification',memberID,certifiedBWdate,member.Certification_Training_Date_2)
        if certifiedBWdate == '':
            member.Certification_Training_Date_2 = None
        else:
            member.Certification_Training_Date_2 = certifiedBWdate
        fieldsChanged += 1

    if willSubRA != member.Monitor_Sub:
        logChange(staffID,'Will sub RA',memberID,willSubRA,member.Monitor_Sub)
        member.Monitor_Sub = willSubRA
        fieldsChanged += 1

    if willSubBW != member.Monitor_Sub_2:
        logChange(staffID,'Will sub BW',memberID,willSubBW,member.Monitor_Sub_2)
        member.Monitor_Sub_2 = willSubBW
        fieldsChanged += 1

    if RAmonitorTrainingDate != member.Last_Monitor_Training:
        logChange(staffID,'RA Monitor Training',memberID,RAmonitorTrainingDate,member.Last_Monitor_Training)
        if RAmonitorTrainingDate == '':
            member.Last_Monitor_Training = None
        else:
            member.Last_Monitor_Training = RAmonitorTrainingDate
        fieldsChanged += 1
     
    if BWmonitorTrainingDate != member.Last_Monitor_Training_Shop_2:
        logChange(staffID,'BW Monitor Training',memberID,BWmonitorTrainingDate,member.Last_Monitor_Training_Shop_2)
        if BWmonitorTrainingDate == '':
            member.Last_Monitor_Training_Shop_2 = None
        else:
            member.Last_Monitor_Training_Shop_2 = BWmonitorTrainingDate
        fieldsChanged += 1
     
    if typeOfWork != None:
        if typeOfWork != member.Default_Type_Of_Work:
            logChange(staffID,'Default_Type_Of_Work',memberID,typeOfWork,member.Default_Type_Of_Work)
            member.Default_Type_Of_Work = typeOfWork
            fieldsChanged += 1

    if skillLevel != None:
        if skillLevel != member.Skill_Level:
            logChange(staffID,'Skill_Level',memberID,skillLevel,member.Skill_Level)
            member.Skill_Level = skillLevel
            fieldsChanged += 1

    if waiverExpirationDate != member.Monitor_Duty_Waiver_Expiration_Date:
        logChange(staffID,'Monitor Waiver Expiration',memberID,waiverExpirationDate,member.Monitor_Duty_Waiver_Expiration_Date)
        if waiverExpirationDate == '':
            member.Monitor_Duty_Waiver_Expiration_Date = None
        else:
            member.Monitor_Duty_Waiver_Expiration_Date = waiverExpirationDate
        fieldsChanged += 1

    if waiverReason != member.Monitor_Duty_Waiver_Reason:
        logChange(staffID,'Monitor Waiver Reason',memberID,waiverReason,member.Monitor_Duty_Waiver_Reason)
        if waiverReason == '':
            member.Monitor_Duty_Waiver_Reason = None
        else:
            member.Monitor_Duty_Waiver_Reason = waiverReason
        fieldsChanged += 1

    if fieldsChanged > 0:
        try:
            db.session.commit()
            print('Certification Info SAVED')
            flash("Changes successful","success")
        except Exception as e:
            print("Certification Info - Could not update member data.","danger")
            flash("Certification Info - Could not update member data.","danger")
            db.session.rollback()

    return redirect(url_for('index',villageID=memberID))


@app.route('/saveMonitorDuty', methods=['POST'])
def saveMonitorDuty():
    # GET DATA FROM FORM
    memberID = request.form['memberID']
    staffID = request.form['staffID']

    # DID USER CANCEL?
    if request.form['monitorAction'] == 'CANCEL':
        return redirect(url_for('index',villageID=memberID))

    # RETRIEVE MEMBER RECORD 
    member = db.session.query(Member).filter(Member.Member_ID == memberID).first()
    fieldsChanged = 0

    if request.form['jan'] == 'True':
        jan = True
    else:
        jan = False
    if member.Jan_resident != jan:
        logChange(staffID,'Jan',memberID,jan,member.Jan_resident)
        member.Jan_resident = jan
        fieldsChanged += 1

    if request.form['feb'] == 'True':
        feb = True
    else:
        feb = False
    if member.Feb_resident != feb:
        logChange(staffID,'Feb',memberID,feb,member.Feb_resident)
        member.Feb_resident = feb
        fieldsChanged += 1

    if request.form['mar'] == 'True':
        mar = True
    else:
        mar = False
    if member.Mar_resident != mar:
        logChange(staffID,'Mar',memberID,mar,member.Mar_resident)
        member.Mar_resident = mar
        fieldsChanged += 1

    if request.form['apr'] == 'True':
        apr = True
    else:
        apr = False
    if member.Apr_resident != apr:
        logChange(staffID,'Apr',memberID,apr,member.Apr_resident)
        member.Apr_resident = apr
        fieldsChanged += 1

    if request.form['may'] == 'True':
        may = True
    else:
        may = False
    if member.May_resident != may:
        logChange(staffID,'may',memberID,may,member.May_resident)
        member.May_resident = may
        fieldsChanged += 1

    if request.form['jun'] == 'True':
        jun = True
    else:
        jun = False
    if member.Jun_resident != jun:
        logChange(staffID,'Jun',memberID,jun,member.Jun_resident)
        member.Jun_resident = jun
        fieldsChanged += 1

    if request.form['jul'] == 'True':
        jul = True
    else:
        jul = False
    if member.Jul_resident != jul:
        logChange(staffID,'Jul',memberID,jul,member.Jul_resident)
        member.Jul_resident = jul
        fieldsChanged += 1

    if request.form['aug'] == 'True':
        aug = True
    else:
        aug = False
    if member.Aug_resident != aug:
        logChange(staffID,'Aug',memberID,aug,member.Aug_resident)
        member.Aug_resident = aug
        fieldsChanged += 1

    if request.form['sep'] == 'True':
        sep = True
    else:
        sep = False
    if member.Sep_resident != sep:
        logChange(staffID,'Sep',memberID,sep,member.Sep_resident)
        member.Sep_resident = sep
        fieldsChanged += 1

    if request.form['oct'] == 'True':
        oct = True
    else:
        oct = False
    if member.Oct_resident != oct:
        logChange(staffID,'Oct',memberID,oct,member.Oct_resident)
        member.Oct_resident = oct
        fieldsChanged += 1

    if request.form['nov'] == 'True':
        nov = True
    else:
        nov = False
    if member.Nov_resident != nov:
        logChange(staffID,'Nov',memberID,nov,member.Nov_resident)
        member.Nov_resident = nov
        fieldsChanged += 1

    if request.form['dec'] == 'True':
        dec = True
    else:
        dec = False
    if member.Dec_resident != dec:
        logChange(staffID,'Dec',memberID,dec,member.Dec_resident)
        member.Dec_resident = dec
        fieldsChanged += 1


    # jan=request.form['jan']
    # feb=request.form['feb']
    # mar=request.form['mar']
    # apr=request.form['apr']
    # may=request.form['may']
    # jun=request.form['jun']
    # jul=request.form['jul']
    # aug=request.form['aug']
    # sep=request.form['sep']
    # oct=request.form['oct']
    # nov=request.form['nov']
    # dec=request.form['dec']
    
    
    # if (jan=='True'):
    #     member.Jan_resident = True
    # else:
    #     member.Jan_resident = False
    # if (feb=='True'):
    #     member.Feb_resident = True
    # else:
    #     member.Feb_resident = False
    # if (mar=='True'):
    #     member.Mar_resident = True
    # else:
    #     member.Mar_resident = False
    # if (apr=='True'):
    #     member.Apr_resident = True
    # else:
    #     member.Apr_resident = False
    # if (may=='True'):
    #     member.May_resident = True
    # else:
    #     member.May_resident = False
    # if (jun=='True'):
    #     member.Jun_resident = True
    # else:
    #     member.Jun_resident = False
    # if (jul=='True'):
    #     member.Jul_resident = True
    # else:
    #     member.Jul_resident = False
    # if (aug=='True'):
    #     member.Aug_resident = True
    # else:
    #     member.Aug_resident = False
    # if (sep=='True'):
    #     member.Sep_resident = True
    # else:
    #     member.Sep_resident = False
    # if (oct=='True'):
    #     member.Oct_resident = True
    # else:
    #     member.Oct_resident = False
    # if (nov=='True'):
    #     member.Nov_resident = True
    # else:
    #     member.Nov_resident = False
    # if (dec=='True'):
    #     member.Dec_resident = True
    # else:
    #     member.Dec_resident = False
   
    try:
        db.session.commit()
        flash("Changes successful","success")
    except Exception as e:
        flash("Could not update member data.","danger")
        db.session.rollback()
    
    return redirect(url_for('index',villageID=memberID))

@app.route("/getNoteToMember")
def getNoteToMember():
    print('getNoteToMember')
    memberID = request.args.get('memberID')
    currentNote = db.session.query(NotesToMembers).filter(NotesToMembers.memberID == memberID).first()
    if (currentNote):
        msg = currentNote.noteToMember
        msg += '\n-----------------------------------------------\n'
        print('return msg')
        return jsonify(msg=msg)
    print('return Nothing')
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
    

def logChange(staffID,colName,memberID,newData,origData):

    # Write data changes to tblMember_Data_Transactions
    #print('log - ',staffID,"|",colName,"|",memberID,"|New- ",newData,"|Orig-",origData),"|"
    newTransaction = MemberTransactions(
        Transaction_Date = datetime.now(),
        Member_ID = memberID,
        Staff_ID = staffID,
        Original_Data = origData,
        Current_Data = newData,
        Data_Item = colName,
        Action = 'UPDATE'
    )
    db.session.add(newTransaction)
    db.session.commit()
    return

@app.route("/newMemberApplication")
def newMemberApplication():
    todays_date = datetime.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    return render_template("newMemberApplication.html")
