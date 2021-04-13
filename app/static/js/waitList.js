// ON PAGE LOAD ...
cancelBtn = document.getElementById('cancelBtn')
saveBtn = document.getElementById('saveBtn')
applicant = document.getElementById('applicantID')
applicationStatus = document.getElementById('applicationStatusID')
memberIDelement = document.getElementById('memberID')
waitListForm = document.getElementById('waitListFormID')
memberIDbtn = document.getElementById('memberID')

numberActive=document.getElementById('numberActive').innerHTML
document.title = "WAIT LIST " + numberActive 

// SET INTIAL VALUES 
if (memberIDelement.value.length > 0) {
  memberIDelement.readonly = true
  document.getElementById('printConfirmBtnID').removeAttribute('disabled')
}
else {
  memberIDelement.readonly = false
  selectAllMonths()
  document.getElementById('state').value = 'FL'
  document.getElementById('dtEntered').style.display='none'
}


// HIDE CANCEL AND SAVE BUTTONS
//cancelBtn.style.display='none'
saveBtn.style.display='none'

// DEFINE EVENT LISTENERS
document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)
document.getElementById("selectpicker").addEventListener("click",memberSelectedRtn)
applicant.addEventListener("click",applicantDataChanged)
applicant.addEventListener("change",applicantDataChanged)
applicationStatus.addEventListener("click",applicantStatusDataChanged)
applicationStatus.addEventListener("change",applicantStatusDataChanged)
document.getElementById("zipcodeSelecterID").addEventListener("change",zipCodeChangeRtn)
document.getElementById("memberID").addEventListener("change",checkVillageID)

// SET INITIAL VALUES FOR SELECT STATEMENTS
curZipcode = document.getElementById('zipcodeTextID').value

selectZipcode = document.getElementById('zipcodeSelecterID')
if (curZipcode != '') {
	selectZipcode.value = curZipcode
}
else{
	selectZipcode.value = ''
}

function checkVillageID() {
  var memberID = document.getElementById('memberID').value
  $.ajax({
      url : "/checkVillageID",
      type: "GET",
      data : {
          memberID:memberID
      },
      success: function(data, textStatus, jqXHR)
      {
          if (data.msg != 'NOT FOUND'){
            window.location.href = "/waitList/" + memberID
          }
    
          
      },
      error: function(result){
          alert("Error ..."+result)
      }
  }) 
}

function zipCodeChangeRtn() {
	newZip = this.value
	document.getElementById("zipcodeTextID").value = newZip
}

// FUNCTIONS 
function memberSelectedRtn() {
    selectedMember = this.value
    lastEight = selectedMember.slice(-8)
    currentMemberID= lastEight.slice(1,7)
    document.getElementById('selectpicker').value=''

    // SET UP LINK TO waitList FORM 
    var linkToWaitListBtn = document.getElementById('linkToWaitList');
    link='/waitList/' + currentMemberID 
    linkToWaitListBtn.setAttribute('href', link)
    linkToWaitListBtn.click()
}

function applicantDataChanged() {
    document.getElementById('saveBtn').style.display='inline' 
}

function applicantStatusDataChanged() {
  if (memberIDelement.value != '' ) {
    document.getElementById('saveBtn').style.display='inline'
  }
}

document.querySelector('#monthCheckboxesID').onclick = function(ev) {
  inputID = ev.target.id
  if (ev.target.checked) {
      document.getElementById(inputID).value='True'
  }
  else {
      document.getElementById(inputID).value='False' 
  }
}

function newApplicant() {
  // SET UP LINK TO waitList FORM 
  var linkToWaitListBtn = document.getElementById('linkToWaitList');
  link='/waitList'  
  linkToWaitListBtn.setAttribute('href', link)
  linkToWaitListBtn.click()
}

function printConfirmation() {
  // SET UP LINK TO waitList FORM 
  var linkToPrintConfirmationBtn = document.getElementById('linkToPrintConfirmation');
  memberID=document.getElementById('memberID').value 
  link='/printConfirmation/'  + memberID
  linkToPrintConfirmationBtn.setAttribute('href', link)
  linkToPrintConfirmationBtn.click()
}

$('.phones').usPhoneFormat({
  format: '(xxx) xxx-xxxx',
  });


$('.phones').keypress(function(event){
  if(event.which != 8 && isNaN(String.fromCharCode(event.which))){
  event.preventDefault(); //stop character from entering input
  }
  });
  
function selectAllMonths() {
  jan=document.getElementById('jan')
  feb=document.getElementById('feb')
  mar=document.getElementById('mar')
  apr=document.getElementById('apr')
  may=document.getElementById('may')
  jun=document.getElementById('jun')
  jul=document.getElementById('jul')
  aug=document.getElementById('aug')
  sep=document.getElementById('sep')
  oct=document.getElementById('oct')
  nov=document.getElementById('nov')
  dec=document.getElementById('dec')
  jan.setAttribute('checked','checked')
  jan.value = 'True'
  feb.setAttribute('checked','checked')
  feb.value = 'True'
  mar.setAttribute('checked','checked')
  mar.value = 'True'
  apr.setAttribute('checked','checked')
  apr.value = 'True'
  may.setAttribute('checked','checked')
  may.value = 'True'
  jun.setAttribute('checked','checked')
  jun.value = 'True'
  jul.setAttribute('checked','checked')
  jul.value = 'True'
  aug.setAttribute('checked','checked')
  aug.value = 'True'
  sep.setAttribute('checked','checked')
  sep.value = 'True'
  oct.setAttribute('checked','checked')
  oct.value = 'True'
  nov.setAttribute('checked','checked')
  nov.value = 'True'
  dec.setAttribute('checked','checked')
  dec.value = 'True'   
  }

  // $('#datepicker').datepicker({
  //   format: "yy-mm-dd",
  //   startDate: new Date(),
  //   endDate: new Date()
  // });
  