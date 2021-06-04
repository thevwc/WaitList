# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables, NotesToMembers, MemberTransactions,\
DuesPaidYears, WaitList, KeysTable, ZipCode
from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta
from pytz import timezone

from flask_mail import Mail, Message
from sqlalchemy.sql import text as SQLQuery

mail=Mail(app)
def logChange(staffID,colName,memberID,newData,origData):
    if staffID == None:
        staffID = '111111'
    if staffID == '':
        staffID = '111111'

    # Write data changes to tblMember_Data_Transactions
    est = timezone('America/New_York')
    newTransaction = MemberTransactions(
        Transaction_Date = datetime.now(est),
        Member_ID = memberID,
        Staff_ID = staffID,
        Original_Data = origData,
        Current_Data = newData,
        Data_Item = colName,
        Action = 'UPDATE'
    )
    db.session.add(newTransaction)
    return
    db.session.commit()

@app.route('/', defaults={'villageID':None})
@app.route('/index/', defaults={'villageID':None})
@app.route('/index/<villageID>/')
@app.route("/waitList",defaults={'villageID':None})
@app.route("/waitList/<villageID>")
def waitList(villageID):
    # GATHER DATA FOR NEW WAIT LIST APPLICATION FORM
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    # PREPARE LIST OF MEMBER NAMES AND VILLAGE IDs
    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF MEMBERS
    applicantArray=[]
    sqlSelect = "SELECT LastName, FirstName, MemberID FROM tblMembershipWaitingList "
    sqlSelect += "ORDER BY LastName, FirstName "
    try:
        nameList = db.engine.execute(sqlSelect)
    except Exception as e:
        flash("Could not retrieve member list.","danger")
        return 'ERROR in wait list function.'
    position = 0
    if nameList == None:
        flash('There is no one on the waiting list.','info')
        return render_template("waitList.html",applicant="",applicantArray="")

    # NEED TO PLACE NAME IN AN ARRAY BECAUSE OF NEED TO CONCATENATE 
    for n in nameList:
        position += 1
        if n.FirstName == None:
            lastFirst = n.LastName
        else:
            lastFirst = n.LastName + ', ' + n.FirstName + ' (' + n.MemberID + ')'
        applicantArray.append(lastFirst)

    # GET ZIPCODES
    zipCodes = db.session.query(ZipCode).order_by(ZipCode.Zipcode).all()

    # COMPUTER NUMBER ACTIVE ON WAIT LIST
    numberActive=db.session.query(func.count(WaitList.MemberID))\
            .filter((WaitList.PlannedCertificationDate == None) | (WaitList.PlannedCertificationDate == ''))\
            .filter((WaitList.NoLongerInterested == None) | (WaitList.NoLongerInterested == '')).scalar()
        
    # IF A VILLAGE ID WAS NOT PASSED IN, DISPLAY THE waitList.html FORM WITHOUT DATA
    if villageID == None:
        return render_template("waitList.html",applicant="",applicantArray=applicantArray,zipCodes=zipCodes,\
        numberActive=numberActive)
    
    # IF A VILLAGE ID WAS PASSED IN ...
   

    # DISPLAY THE CORRESPONDING WAITLIST DATA FOR THAT VILLAGE ID
    applicant = db.session.query(WaitList).filter(WaitList.MemberID == villageID).first()

    placeOnList = findPlaceOnList(villageID)
    dateTimeAdded = applicant.DateTimeEntered.strftime('%m-%d-%Y %I:%M %p')
    return render_template("waitList.html",applicant=applicant,applicantArray=applicantArray,\
    todaySTR=todaySTR,placeOnList=placeOnList,zipCodes=zipCodes,dateTimeAdded=dateTimeAdded,\
    numberActive=numberActive)
    

@app.route("/updateWaitList", methods=('GET','POST'))
def updateWaitList():
    # POST REQUEST; PROCESS WAIT LIST APPLICATION, ADD TO MEMBER_DATA, INSERT TRANSACTION ('ADD')
    memberID = request.form.get('memberID')
    if request.form.get('waitList') == 'CANCEL':
        #return redirect(url_for('waitList',villageID=memberID))
        return redirect(url_for('waitList'))

   # RETRIEVE FORM VALUES
    expireDate = request.form.get('expireDate')
   
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip = request.form.get('zip')
    cellPhone = request.form.get('cellPhone')
    homePhone = request.form.get('homePhone')
    eMail = request.form.get('eMail')
    if request.form.get('jan') == 'True':
        jan = True
    else:
        jan = False

    if request.form.get('feb') == 'True':
        feb = True
    else:
        feb = False

    if request.form.get('mar') == 'True':
        mar = True
    else:
        mar = False

    if request.form.get('apr') == 'True':
        apr = True
    else:
        apr = False

    if request.form.get('may') == 'True':
        may = True
    else:
        may = False

    if request.form.get('jun') == 'True':
        jun = True
    else:
        jun = False
    
    if request.form.get('jul') == 'True':
        jul = True
    else:
        jul = False

    if request.form.get('aug') == 'True':
        aug = True
    else:
        aug = False

    if request.form.get('sep') == 'True':
        sep = True
    else:
        sep = False

    if request.form.get('oct') == 'True':
        oct = True
    else:
        oct = False

    if request.form.get('nov') == 'True':
        nov = True
    else:
        nov = False

    if request.form.get('dec') == 'True':
        dec = True
    else:
        dec = False
    
    notes = request.form.get('notes')
    approvedToJoin = request.form.get('approvedToJoin')
    notified = request.form.get('notified')
    applicantAccepts = request.form.get('applicantAccepts')
    applicantDeclines = request.form.get('applicantDeclines')
    noLongerInterested = request.form.get('noLongerInterested')
    plannedCertificationDate = request.form.get('plannedCertificationDate')

    # GET ID OF STAFF MEMBER 
    if ('staffID' in session):
        staffID = session['staffID']
    else:
        staffID = ''

    # GET CURRENT DATE AND TIME
    est = timezone('US/Eastern')
    todays_date = datetime.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    
    # IS THIS PERSON ALREADY ON THE WAITLIST?
    waitListRecord = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    if (waitListRecord == None):
        # ADD NEW RECORD TO tblMembershipWaitingList
        if plannedCertificationDate == '':
            plannedCertificationDate = None
        
        try:
            newWaitListRecord = WaitList( 
                MemberID = memberID,
                VillageIDexpirationDate = expireDate,
                FirstName = firstName,
                LastName = lastName, 
                StreetAddress = street,
                City = city,
                State = state,
                Zipcode = zip,
                CellPhone = cellPhone,
                HomePhone = homePhone,
                Email = eMail,
                Notes = notes,
                PlannedCertificationDate = plannedCertificationDate,
                AddedByStaffMemberID = staffID,
                Jan = jan,
                Feb = feb,
                Mar = mar,
                Apr = apr,
                May = may,
                Jun = jun,
                Jul = jul,
                Aug = aug,
                Sep = sep,
                Oct = oct,
                Nov = nov,
                Dec = dec,
                DateTimeEntered = datetime.now(est)
            ) 
        
            db.session.add(newWaitListRecord)
            db.session.commit()

        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            flash('ERROR - Record not added.'+error,'danger')
            db.session.rollback()
        
        return redirect(url_for('waitList',villageID=memberID,todaysDate=todaySTR))
        # END OF ADDING NEW APPLICANT
        
    
    # PROCESS UPDATE OF EXISTING WAIT LIST RECORD
    if waitListRecord.FirstName != firstName :
        waitListRecord.FirstName = firstName
    if waitListRecord.LastName != lastName :
        waitListRecord.LastName = lastName
    if waitListRecord.HomePhone != homePhone :
        waitListRecord.HomePhone = homePhone
    if waitListRecord.CellPhone != cellPhone :
        waitListRecord.CellPhone = cellPhone
       
    if waitListRecord.StreetAddress != street :
        waitListRecord.StreetAddress = street
    
    if waitListRecord.City != city :
        waitListRecord.City = city
    if waitListRecord.State != state :
        waitListRecord.State = state
    if waitListRecord.Zipcode != zip :
        waitListRecord.Zipcode = zip
    if waitListRecord.Email != eMail :
        waitListRecord.Email = eMail

    if waitListRecord.Notes != notes :
        waitListRecord.Notes = notes
    
    if waitListRecord.ApprovedToJoin != approvedToJoin :
        waitListRecord.ApprovedToJoin = approvedToJoin
    if waitListRecord.Notified != notified :
        waitListRecord.Notified = notified
    
    


    if waitListRecord.Jan != jan:
        waitListRecord.Jan = jan
    if waitListRecord.Feb != feb :
        waitListRecord.Feb = feb
    if waitListRecord.Mar != mar:
        waitListRecord.Mar = mar
    if waitListRecord.Apr != apr:
        waitListRecord.Apr = apr
    if waitListRecord.May != may:
        waitListRecord.May = may
    if waitListRecord.Jun != jun:
        waitListRecord.Jun = jun
    if waitListRecord.Jul != jul:
        waitListRecord.Jul = jul
    if waitListRecord.Aug != aug:
        waitListRecord.Aug = aug
    if waitListRecord.Sep != sep:
        waitListRecord.Sep = sep
    if waitListRecord.Oct != oct:
        waitListRecord.Oct = oct
    if waitListRecord.Nov != nov:
        waitListRecord.Nov = nov
    if waitListRecord.Dec != dec:
        waitListRecord.Dec = dec
    
    if waitListRecord.ApplicantAccepts != applicantAccepts :
        waitListRecord.ApplicantAccepts = applicantAccepts
    if waitListRecord.ApplicantDeclines != applicantDeclines :
        waitListRecord.ApplicantDeclines = applicantDeclines
    if waitListRecord.NoLongerInterested != noLongerInterested :
        waitListRecord.NoLongerInterested = noLongerInterested
    if waitListRecord.PlannedCertificationDate != plannedCertificationDate :
        waitListRecord.PlannedCertificationDate = plannedCertificationDate
    
    try:
        db.session.commit()
        flash("Changes to wait list successful","success")
    except Exception as e:
        flash("Could not update Wait List data.","danger")
        db.session.rollback()

    # DETERMINE APPLICANTS PLACE ON WAITING LIST
    # RETURN COUNT OF # OF RECORDS BEFORE THEIR ID WHEN ORDERED BY ID AND FILTERED BY PlannedCertificationDate is null and NoLongerInterested isnull 
    placeOnList = findPlaceOnList(memberID)
    # applicant = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    # if (applicant != None):
    #     placeOnList = findPlaceOnList(memberID)

    #     sp = "EXEC placeOnList '" + applicant.ID + "'"
    #     print('sp - ',sp)

    #     sql = SQLQuery(sp)
    #     placeNumber = db.engine.execute(sql)
    #     print('placeNumber - ',placeNumber)
            
    #     if (applicant.PlannedCertificationDate == None\
    #     or applicant.PlannedCertificationDate == '' \
    #     or applicant.PlannedCertificationDate == '1900-01-01'):
    #         PlannedCertification = False
    #     else:
    #         # applicant has been scheduled to be certified
    #         PlannedCertification = True

    #     if (applicant.NoLongerInterested == None \
    #     or applicant.NoLongerInterested == '' \
    #     or applicant.NoLongerInterested == '1900-01-01'):
    #         NoLongerInterested = False
    #     else:
    #         # applicant is no longer interested
    #         NoLongerInterested = True

    #     if (PlannedCertification == False and NoLongerInterested == False):
    #         placeOnList = 0
    #     else:
            
    #         placeOnList = db.session.query(func.count(WaitList.MemberID))\
    #         .filter((WaitList.PlannedCertificationDate == None) | (WaitList.PlannedCertificationDate == ''))\
    #         .filter((WaitList.NoLongerInterested == None) | (WaitList.NoLongerInterested == ''))\
    #         .filter(WaitList.id <= applicant.id)\
    #         .scalar() 
    # else:
    #     placeOnList = 0

    return redirect(url_for('waitList',villageID=memberID,todaysDate=todaySTR,placeOnList=placeOnList))

@app.route("/printConfirmation/<memberID>")
def printConfirmation(memberID):
    # GET MEMBER NAME
    applicant = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    if applicant == None:
        flash ("Error in printing confirmation letter.",'danger')
        return

    displayName = applicant.FirstName + ' ' + applicant.LastName
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%m-%d-%Y')
    applicationDate = applicant.DateTimeEntered.strftime('%A, %B %-d, %Y')
    # Using include statement in html file for included text 'WaitListConfirmation.html' in Template folder
    return render_template("rptAppConfirm.html",displayName=displayName,applicant=applicant,
    applicationDate=applicationDate,todays_date=todays_dateSTR)

@app.route("/checkVillageID/")
def checkVillageID():
    memberID = request.args.get("memberID")
  
    applicant = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    #applicant = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    if applicant:
        name=applicant.FirstName + " " + applicant.LastName
        msg=name + " is already on the wait list."
    else:
        msg="NOT FOUND"

    return jsonify(msg=msg)


def findPlaceOnList(memberID):
    applicant = db.session.query(WaitList).filter(WaitList.MemberID == memberID).first()
    
    if (applicant == None):
        return 0
        # msg = "No record for applicant with village ID " + villageID
        # flash(msg,"info")
        # return render_template("waitList.html",applicant='',applicantArray=applicantArray,\
        # todaySTR=todaySTR,zipCodes=zipCodes,numberActive=numberActive)
    else:
        # DETERMINE APPLICANTS PLACE ON WAITING LIST
        # RETURN COUNT OF # OF RECORDS BEFORE THEIR ID WHEN ORDERED BY ID AND FILTERED BY PlannedCertificationDate is null and NoLongerInterested isnull 
        earliestDate = datetime.strptime("19000101","%Y%m%d").date()

        if (applicant.PlannedCertificationDate != None and applicant.PlannedCertificationDate > earliestDate):
            PlannedCertification = True
        else:
            PlannedCertification = False
        
        if (applicant.NoLongerInterested != None and applicant.NoLongerInterested > earliestDate):
            NoLongerInterested = True
        else:
            NoLongerInterested = False

        if (PlannedCertification == True or NoLongerInterested == True):
            placeOnList = 0 
        else:
        
            sqlPlaceInList = "SELECT memberID FROM tblMembershipWaitingList "
            sqlPlaceInList += "WHERE NoLongerInterested is null and PlannedCertificationDate is null "
            sqlPlaceInList += "AND ID < " + str(applicant.id)

            result = db.engine.execute(sqlPlaceInList)
            if (result == None):
                placeOnList = 0
            else:
                cnt = 0
                for r in result:
                    cnt += 1
                placeOnList = cnt

            # ALTERNATE SOLUTION THAT WORKS
            # sp = "EXEC placeOnList '" + str(applicant.id) + "'"
            # sql = SQLQuery(sp)
            # result = db.engine.execute(sql)
            # for row in result:
            #     placeOnList = row[0]
    return placeOnList    
    