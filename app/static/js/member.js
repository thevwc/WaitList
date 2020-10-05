// member.js

// DEFINE VARIABLES
// Color constants
const colors = {
    bg_NeedSM:  "#0000FF",  // Blue
    fg_NeedSM:  "#FFFFFF",  // White 
    bg_NeedTC:  "#00FF00",  // Green
    fg_NeedTC:  "#000000",  // Black (#000000)
    bg_NeedBoth:"#FF0000",  // Red (#FF0000)
    fg_NeedBoth:"#FFFFFF",  // White (#FFFFFF)
    bg_Filled:  "#FFFFFF",  // White (#FFFFFF)
    fg_Filled:  "#000000",  // Black (#000000)
    bg_Sunday:  "#cccccc",  // Light grey
    fg_Sunday:  "#FFFFFF",  // White (#FFFFFF)
    bg_Closed:  "#2E86C1",  // Aqua
    fg_Closed:  "#FFFFFF",  // White (#FFFFFF)
    bg_ToManySM:"#FAFE02",  // Yellow
    fg_ToManySM:"#000000",  // Black
    bg_ToManyTC:"#FE4E02",  // Orange
    fg_ToManyTC:"#000000",  // Black
    bg_PastDate:"#cccccc",  // Light grey
    fg_PastDate:"#FFFFFF"   // White (#FFFFFF)
};

// Declare global variables)

// clientLocation, staffID will be set in localStorage within login routine
var clientLocation = ''
var todaysDate = new Date();
var shopNames = ['Rolling Acres', 'Brownwood']
var currentMemberID = ''
var curShopNumber = ''

// SET OPTIONS IN SELECT ELEMENTS BASED ON TEXT VALUES
typeOfWorkText = document.getElementById('typeOfWorkTextID').value
typeOfWorkSelect = document.getElementById('typeOfWorkSelecterID')
typeOfWorkSelect.value = typeOfWorkText

skillLevelText = document.getElementById('skillLevelTextID').value
skillLevelSelect = document.getElementById('skillLevelSelecterID')
if (skillLevelSelect != null) {
    skillLevelSelect.value = skillLevelText
}
// ASSIGN PANELS TO VARIABLES
localContactInfo = document.getElementById('localContactID')
altContactInfo = document.getElementById('altContactID')
emergencyInfo = document.getElementById('emergencyID')
membershipInfo = document.getElementById('membershipID')
certificationInfo = document.getElementById('certificationID')
monitorDutyInfo = document.getElementById('monitorDutyID')

// DEFINE EVENT LISTENERS
localContactInfo.addEventListener('change',localDataChanged);
altContactInfo.addEventListener('change',altDataChanged);
emergencyInfo.addEventListener('change',emergencyDataChanged);
membershipInfo.addEventListener('change',membershipDataChanged);
certificationInfo.addEventListener('change',certificationDataChanged);
monitorDutyInfo.addEventListener('change',monitorDutyDataChanged);
// showPhotoBtn.addEventListener('click','setPhotoSrc');
// MODAL EVENT LISTENERS
document.getElementById("cancelNoteID").addEventListener("click",cancelNote)
document.getElementById("processMsgID").addEventListener("click",processNote)
//document.getElementById("medicalModalBtn").addEventListener("click",showMedicalInfo)

document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)
document.getElementById("selectpicker").addEventListener("click",memberSelectedRtn)

document.getElementById("typeOfWorkSelecterID").addEventListener("change",typeOfWorkRtn)
document.getElementById("skillLevelSelecterID").addEventListener("change",skillLevelRtn)

document.querySelector('#monthCheckboxesID').onclick = function(ev) {
    inputID = ev.target.id + 'ResidentValue'
    if (ev.target.checked) {
        document.getElementById(inputID).value='True'
    }
    else {
        document.getElementById(inputID).value='False' 
    }
}
document.querySelector('#dues').onclick = function(ev) {
    inputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(inputID).value = 'True'
    }
    else {
        document.getElementById(inputID).value = 'False'
    }
}
document.querySelector('#volunteer').onclick = function(ev) {
    alert('inputID - '+inputID)
    inputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(inputID).value = 'True'
    }
    else {
        document.getElementById(inputID).value = 'False'
    }
}
document.querySelector('#inactive').onclick = function(ev) {
    inputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(inputID).value = 'True'
    }
    else {
        document.getElementById(inputID).value = 'False'
    }
    alert('inactive - '+ document.getElementById(inputID).value)
}

document.querySelector('#deceased').onclick = function(ev) {
    inputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(inputID).value = 'True'
    }
    else {
        document.getElementById(inputID).value = 'False'
    }
}

document.querySelector('#restricted').onclick = function(ev) {
    inputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(inputID).value = 'True'
    }
    else {
        document.getElementById(inputID).value = 'False'
    }
}

document.querySelector('#waiver').onclick = function(ev) {
    waiverInputID = ev.target.id + 'Text'
    if (ev.target.checked) {
        document.getElementById(waiverInputID).value = 'True'
    }
    else {
        document.getElementById(waiverInputID).value = 'False'
    }
}

// HIDE DETAIL UNTIL A MEMBER IS SELECTED
memberID = document.getElementById('memberID').value
if (memberID.length == 0)
{
    // FIND METHOD TO DISPLAY BLANK SCREEN BELOW HEADING

    
    // localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // localContactInfo.style.color="rgba(0,0,0,0.6)"
    // altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // altContactInfo.style.color="rgba(0,0,0,0.6)"
    // emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // emergencyInfo.style.color="rgba(0,0,0,0.6)"
    // membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // membershipInfo.style.color="rgba(0,0,0,0.6)"
    // certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // certificationInfo.style.color="rgba(0,0,0,0.6)"
    // monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    // monitorDutyInfo.style.color="rgba(0,0,0,0.6)"

}

// CHECK BOX LISTENERS
document.getElementById('defibrillatorID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('defibrillatorID').value='True'
    }
    else {
        document.getElementById('defibrillatorID').value='False' 
    }
}

document.getElementById('noEmergDataID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('noEmergDataID').value='True'
    }
    else {
        document.getElementById('noEmergDataID').value='False' 
    }
}
// MODAL OF ADDITIONAL MEDICAL INFO
document.getElementById('emergPacemakerID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergPacemakerID').value='True'
    }
    else {
        document.getElementById('emergPacemakerID').value='False' 
    }
}
document.getElementById('emergStentID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergStentID').value='True'
    }
    else {
        document.getElementById('emergStentID').value='False' 
    }
}
document.getElementById('emergCABGID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergCABGID').value='True'
    }
    else {
        document.getElementById('emergCABGID').value='False' 
    }
}
document.getElementById('emergMIID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergMIID').value='True'
    }
    else {
        document.getElementById('emergMIID').value='False' 
    }
}
document.getElementById('emergDiabetes1ID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergDiabetes1ID').value='True'
    }
    else {
        document.getElementById('emergDiabetes1ID').value='False' 
    }
}
document.getElementById('emergDiabetes2ID').onclick = function(ev) {
    if (ev.target.checked) {
        document.getElementById('emergDiabetes2ID').value='True'
    }
    else {
        document.getElementById('emergDiabetes2ID').value='False' 
    }
}


// SELECT CONTROL LISTENERS
// typeOfWork = document.getElementById('typeOfWorkSelect')
// typeOfWork.onchange = function(ev) {
//     alert('selected value - '+ target.value)
// }

// document.getElementById('typeOfWorkSelect').onclick = function(ev) {
//     alert('selected item - ' + target.value)
//     document.getElementById('typeOfWorkText').value=target.value
// }

// RETRIEVE LOCAL STORAGE VALUES
if (!localStorage.getItem('staffID')) {
    localStorage.setItem('staffID','111111')
}
staffID = localStorage.getItem('staffID')
 

// IF clientLocation IS NOT FOUND IN LOCAL STORAGE
// THEN PROMPT WITH MODAL FORM FOR LOCATION AND YEAR
if (!clientLocation) {
    localStorage.setItem('clientLocation','RA')
}
clientLocation = localStorage.getItem('clientLocation')

setShopFilter(clientLocation)

// ------------------------------------------------------------------------------------------------------
// FUNCTIONS    
// ------------------------------------------------------------------------------------------------------
function setShopFilter(shopLocation) {
    switch(shopLocation){
        case 'RA':
            localStorage.setItem('shopFilter','RA')
            shopFilter = 'RA'
            curShopNumber = '1'
            break;
        case 'BW':
            localStorage.setItem('shopFilter','BW')
            shopFilter = 'BW'
            curShopNumber = '2'
            break;
        default:
            localStorage.setItem('shopFilter','RA')
            shopFilter = 'RA'
            curShopNumber = '1'
    }   
}

function memberSelectedRtn() {
    selectedMember = this.value
    lastEight = selectedMember.slice(-8)
    currentMemberID= lastEight.slice(1,7)
    document.getElementById('selectpicker').value=''
    imgLink = document.getElementById('memberImgID')
    imgLink.link = "{{ url_for('static', filename='memberPhotos/" + currentMemberID + ".jpg') }}"
    localStorage.setItem('currentMemberID',currentMemberID)
    
    // SET UP LINK TO MEMBER FORM 
    var linkToMemberBtn = document.getElementById('linkToMember');
    link='/index/' + currentMemberID 
    linkToMemberBtn.setAttribute('href', link)
    linkToMemberBtn.click()
    // hdgTitle = document.getElementById('hdgTitleID')
    // hdgTitle.style.display='inline'
}

function localDataChanged() {
    document.getElementById('localCancelBtn').style.display='inline';
    document.getElementById('localSaveBtn').style.display='inline';
    altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    altContactInfo.style.color="rgba(0,0,0,0.6)"
    emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    emergencyInfo.style.color="rgba(0,0,0,0.6)"
    membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    membershipInfo.style.color="rgba(0,0,0,0.6)"
    certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    certificationInfo.style.color="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.color="rgba(0,0,0,0.6)"

}

function altDataChanged() {
    document.getElementById('altCancelBtn').style.display='inline';
    document.getElementById('altSaveBtn').style.display='inline';
    localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    localContactInfo.style.color="rgba(0,0,0,0.6)"
    emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    emergencyInfo.style.color="rgba(0,0,0,0.6)"
    membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    membershipInfo.style.color="rgba(0,0,0,0.6)"
    certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    certificationInfo.style.color="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.color="rgba(0,0,0,0.6)"
}

function emergencyDataChanged() {
    document.getElementById('emergCancelBtn').style.display='inline';
    document.getElementById('emergSaveBtn').style.display='inline';
    localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    localContactInfo.style.color="rgba(0,0,0,0.6)"
    altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    altContactInfo.style.color="rgba(0,0,0,0.6)"
    membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    membershipInfo.style.color="rgba(0,0,0,0.6)"
    certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    certificationInfo.style.color="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.color="rgba(0,0,0,0.6)"
}

function membershipDataChanged() {
    document.getElementById('memberCancelBtn').style.display='inline';
    document.getElementById('memberSaveBtn').style.display='inline';
    localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    localContactInfo.style.color="rgba(0,0,0,0.6)"
    altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    altContactInfo.style.color="rgba(0,0,0,0.6)"
    emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    emergencyInfo.style.color="rgba(0,0,0,0.6)"
    certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    certificationInfo.style.color="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.color="rgba(0,0,0,0.6)"
}

function certificationDataChanged() {
    document.getElementById('certificationCancelBtn').style.display='inline';
    document.getElementById('certificationSaveBtn').style.display='inline';
    localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    localContactInfo.style.color="rgba(0,0,0,0.6)"
    altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    altContactInfo.style.color="rgba(0,0,0,0.6)"
    emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    emergencyInfo.style.color="rgba(0,0,0,0.6)"
    membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    membershipInfo.style.color="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    monitorDutyInfo.style.color="rgba(0,0,0,0.6)"
}

function monitorDutyDataChanged() {
    document.getElementById('monitorDutyCancelBtn').style.display='inline';
    document.getElementById('monitorDutySaveBtn').style.display='inline';
    localContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    localContactInfo.style.color="rgba(0,0,0,0.6)"
    altContactInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    altContactInfo.style.color="rgba(0,0,0,0.6)"
    emergencyInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    emergencyInfo.style.color="rgba(0,0,0,0.6)"
    membershipInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    membershipInfo.style.color="rgba(0,0,0,0.6)"
    certificationInfo.style.backgroundColor="rgba(0,0,0,0.6)"
    certificationInfo.style.color="rgba(0,0,0,0.6)"
}

// function cancelRtn(){
//     // SET UP LINK TO MEMBER FORM 
//     alert('currentMemberID- ',currentMemberID)
//     var refreshPageBtn = document.getElementById('refreshPage');
//     link='/index/' + currentMemberID 
//     refreshPageBtn.setAttribute('href', link)
//     refreshPageBtn.click()
// }

function monthCheckboxRtn() {
    if (this.checked) {
        this.value = True
    }
    else {
        this.value = False
    }
}

function findAllVariables() { 
    msg=''
    for (let variable in window) { 
        if (window.hasOwnProperty(variable)) { 
            msg += variable + '\n'
            console.log(variable); 
        } 
    } 
    alert(msg)
} 

/* When the user clicks on the button, 
toggle between hiding and showing the dropdown content */
function myFunction() {
    //alert('myFunction')
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown if the user clicks outside of it
  window.onclick = function(event) {
    //alert('window.onclick')
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }

function noteRoutine() {
    // CHECK FOR EXISTING NOTE
    // IF FOUND, DISPLAY IN MSG
    memberID = document.getElementById('memberID').value
    //memberName = document.getElementById('modal-title').value

    $.ajax({
        url : "/getNoteToMember",
        type: "GET",
        data : {
            memberID:memberID,
            },
 
        success: function(data, textStatus, jqXHR)
        {
            if (data.msg) {
                msg = data.msg
                msgElement = document.getElementById('msgID')
                msgElement.value = msg
            }
            //alert("SUCCESS"+ data)
        },
        error: function(result){
            alert("Error ..."+result)
        }
    })    
    $('#noteModalID').modal('show')
}

// $('#noteModalID').on('hide.bs.modal', function () {
//     alert('modal was hidden')
// })

function cancelNote() {
    $('#noteModalID').modal('hide')
}

function processNote() {
    console.log('processNote')
    memberID = document.getElementById('memberID').value
    show = document.getElementById('showAtCheckIn')
    send = document.getElementById('sendEmail')
    msg = document.getElementById('msgID').value
    eMailAddr = document.getElementById('eMailID').value
    console.log('memberID - '+memberID + '\nshow - '+show.checked+'\nsend - '
    +send.checked+'\nmsg - '+msg+'\neMailAddr - '+eMailAddr)
    
    if (show.checked) {
        showAtCheckIn='true'
    }
    else {
        showAtCheckIn='false'
    }
    if (send.checked) {
        console.log('send routine ...')
        sendEmail = 'true'
        
        console.log ('eMailAddr - ' + eMailAddr)
        alert ('emailAddress - '+eMailAddr)
    }
    else {
        sendEmail = 'false' 
    } 
      
    $.ajax({
        url : "/processNoteToMember",
        type: "GET",
        data : {
            showAtCheckIn: showAtCheckIn,
            sendEmail: sendEmail,
            memberID:memberID,
            eMailAddr:'hartl1r@gmail.com',
            msg:msg},

        success: function(data, textStatus, jqXHR)
        {
            alert(data)
        },
        error: function(result){
            alert("Error ..."+result)
        }
    }) 
    
    $('#noteModalID').modal('hide')

}
// $('#noteModalID').on('shown.bs.modal', function () {
//     $('#msgID').focus();
// }) 
// function showMedicalInfo() {
//     alert('show emergModalID')
//     $('#emergModalID').modal('show')
// }
// function medicalInfoRoutine() {
//     // CHECK FOR EXISTING MEDICAL DATA
//     // IF FOUND, DISPLAY IN FORM
//     memberID = document.getElementById('memberID').value
    
//     $.ajax({
//         url : "/getMedicalInfo",
//         type: "GET",
//         data : {
//             memberID:memberID,
//             },
 
//         success: function(data, textStatus, jqXHR)
//         {
//             //alert('data - '+ data.medData.OtherDiagnosis)
//             //console.log('OtherDiagnosis - '+data.medData.OtherDiagnosis)
//             //console.log('otherDiagnosis - '+data.otherDiagnosis)
//             console.log('pacemaker - '+data.pacemaker)
//             console.log('alergies - '+data.alergies)
//             //console.log('stent - '+data.stent)
//             //console.log('MI - '+data.MI)
//             if (data.pacemaker == true) {
//                 pacemaker = document.getElementById('emergPacemaker')
//                 pacemaker.value = 'True'
//                 pacemaker.checked = true
//                 //console.log('pacemaker = true')
//             }
//             if (data.stent == true) {
//                 stent = document.getElementById('emergStent')
//                 stent.value = 'True'
//                 stent.checked = true
//                 //console.log('stent = true')
//             }
//             if (data.CABG == true) {
//                 CABG = document.getElementById('emergCABG')
//                 CABG.value = 'True'
//                 CABG.checked = true
//                 //console.log('CABG = true')
//             }
//             if (data.MI == true) {
//                 MI = document.getElementById('emergMI')
//                 MI.value = 'True'
//                 MI.checked = true
//                 //console.log('MI = true')
//             }
//             if (data.diabetes1 == true) {
//                 diabetes1 = document.getElementById('emergDiabetes1')
//                 diabetes1.value = 'True'
//                 diabetes1.checked = true
//                 //console.log('diabetes1 = true')
//             }
//             if (data.diabetes2 == true) {
//                 diabetes2 = document.getElementById('emergDiabetes2')
//                 diabetes2.value = 'True'
//                 diabetes2.checked = true
//                 //console.log('diabetes2 = true')
//             }
//             document.getElementById('emergOtherDiagnosis').value = data.otherDiagnosis
//             document.getElementById('emergDiabetesOther').value = data.diabetesOther
//             document.getElementById('emergAlergies').value = data.alergies

//             document.getElementById('emergMemberID').value = data.emergMemberID
//             alert("SUCCESS")
//         },
//         error: function(result){
//             alert("Error ..."+result)
//         }
//     })    
//     $('#emergModalID').modal('show')
// }

// $("#emergCancelBtn").click(function () {
//     alert('emergCancelBtn clicked')
//     $("#emergencyID").modal("hide");
// });

function setPhotoSrc() {
    photo = document.getElementsByClassName('memberImgID')
    photo.src = "{{ url_for('static', filename='memberPhotos/" + currentMemberID + ".jpg') }}"
}
function showHidePhoto(objBtn) {
    photo = document.getElementById('memberImgID')
    memberID = document.getElementById('memberID').value
    if (objBtn.innerHTML == 'SHOW PHOTO'){
        objBtn.innerHTML = 'HIDE PHOTO'
        photo.src = "/static/memberPhotos/" + memberID + ".jpg "
        photo.style.display='inline'
    }
    else {
        objBtn.innerHTML = 'SHOW PHOTO'
        photo.style.display='none'
    }
}

function typeOfWorkRtn() {
    typeOfWork = this.value
    document.getElementById('typeOfWorkTextID').value=this.value
}

function skillLevelRtn() {
    skillLevel = this.value
    document.getElementById('skillLevelTextID').value=this.value
}
function clearScreen() {
    // alert('clear screen')
    // hdgTitle = document.getElementById('hdgTitleID')
    // hdgTitle.style.display='none'
    var linkToMemberBtn = document.getElementById('linkToMember');
    link='/index/' 
    linkToMemberBtn.setAttribute('href', link)
    linkToMemberBtn.click()
}

function cancelAddtlMedicalInfo() {
    $("#emergModalID").modal("hide");
}
function saveAddtlMedicalInfo() {
    memberID = document.getElementById('memberID').value
    $.ajax({
        url : "/saveAddtlMedicalInfo",
        type: "GET",
        data : {
            memberID:memberID,
            
            },
 
        success: function(data, textStatus, jqXHR)
        {
            // if (data.msg) {
            //     msg = data.msg
            //     msgElement = document.getElementById('msgID')
            //     msgElement.value = msg
            // }
            alert("SUCCESS"+ data)
        },
        error: function(result){
            alert("Error ..."+result)
        }
    })    
    $('#emergModalID').modal('hide')
}
  
