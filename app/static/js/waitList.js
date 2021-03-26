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

$('#datepicker').datepicker({
  format: "yy-mm-dd",
  startDate: new Date(),
  endDate: new Date()
});

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


// function showMenu() {
//     document.getElementById("myDropdown").classList.toggle("show");
//   }

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
$('#homePhone').usPhoneFormat({
  format:"(xxx) xxx-xxxx",
})

$('#cellPhone').usPhoneFormat({
  format:"(xxx) xxx-xxxx",
})

$('.phones').keypress(function(event){
  if(event.which != 8 && isNaN(String.fromCharCode(event.which))){
  event.preventDefault(); //stop character from entering input
  }
  });
  
// $('input[type="tel"]')
// 	.keydown(function (e) {
// 		var key = e.which || e.charCode || e.keyCode || 0;
// 		$phone = $(this);

//     // Don't let them remove the starting '('
//     if ($phone.val().length === 1 && (key === 8 || key === 46)) {
// 			$phone.val('('); 
//       return false;
// 		} 
//     // Reset if they highlight and type over first char.
//     else if ($phone.val().charAt(0) !== '(') {
// 			$phone.val('('+String.fromCharCode(e.keyCode)+''); 
// 		}

// 		// Auto-format- do not expose the mask as the user begins to type
// 		if (key !== 8 && key !== 9) {
// 			if ($phone.val().length === 4) {
// 				$phone.val($phone.val() + ')');
// 			}
// 			if ($phone.val().length === 5) {
// 				$phone.val($phone.val() + ' ');
// 			}			
// 			if ($phone.val().length === 9) {
// 				$phone.val($phone.val() + '-');
// 			}
// 		}

// 		// Allow numeric (and tab, backspace, delete) keys only
// 		return (key == 8 || 
// 				key == 9 ||
// 				key == 46 ||
// 				(key >= 48 && key <= 57) ||
// 				(key >= 96 && key <= 105));	
// 	})
	
// 	.bind('focus click', function () {
// 		$phone = $(this);
		
// 		if ($phone.val().length === 0) {
// 			$phone.val('(');
// 		}
// 		else {
// 			var val = $phone.val();
// 			$phone.val('').val(val); // Ensure cursor remains at the end
// 		}
// 	})
	
// 	.blur(function () {
// 		$phone = $(this);
		
// 		if ($phone.val() === '(') {
// 			$phone.val('');
// 		}
//   });
  
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
    
    // THE FOLLOWING CODE SHOULD WORK!
    // var monthBoxes = document.querySelectorAll('.monthCheckboxes input')
    // for (var i = 0; i > monthBoxes.length; i++) {
    //   monthBoxes[i].setAttribute('checked','checked')
    //   monthBoxes[i].value = 'True'
    // }   
  }