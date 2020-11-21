// ON PAGE LOAD ...
cancelBtn = document.getElementById('cancelBtn')
saveBtn = document.getElementById('saveBtn')
applicant = document.getElementById('applicantID')
applicationStatus = document.getElementById('applicationStatusID')
memberIDelement = document.getElementById('memberID')
waitListForm = document.getElementById('waitListFormID')
memberIDbtn = document.getElementById('memberID')

// SET INTIAL VALUES 
if (memberIDelement.value.length > 0) {
  memberIDelement.readonly = true
  document.getElementById('printConfirmBtnID').removeAttribute('disabled')
}
else {
  memberIDelement.readonly = false
}

// HIDE CANCEL AND SAVE BUTTONS
cancelBtn.style.display='none'
saveBtn.style.display='none'

// DEFINE EVENT LISTENERS
document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)
document.getElementById("selectpicker").addEventListener("click",memberSelectedRtn)
applicant.addEventListener("change",applicantDataChanged)
applicationStatus.addEventListener("change",applicantStatusDataChanged)

// $('#printConfirmationID').click(function(){
// 	memberID = document.getElementById('memberID').value
// 	if (memberID == ''){
// 		alert("Please select an applicant to print.")
// 		return 
// 	}
// 	window.location.href = '/printConfirmation?memberID=' + memberID 
// })


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
    if (memberIDelement.value != "") {
      document.getElementById('cancelBtn').style.display='inline'
      document.getElementById('saveBtn').style.display='inline'
      
    }
    else {
      alert("Please enter a member ID.")
    }   
}

function applicantStatusDataChanged() {
  if (memberIDelement.value != '' ) {
    document.getElementById('cancelBtn').style.display='inline'
    document.getElementById('saveBtn').style.display='inline'
  }
  else {
    alert("Please enter a member ID.")
  }
}

document.querySelector('#monthCheckboxesID').onclick = function(ev) {
  inputID = ev.target.id
  console.log('inputID - '+ inputID)
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

// $('.phoneNumber')
$('input[type="tel"]')
	.keydown(function (e) {
		var key = e.which || e.charCode || e.keyCode || 0;
		$phone = $(this);

    // Don't let them remove the starting '('
    if ($phone.val().length === 1 && (key === 8 || key === 46)) {
			$phone.val('('); 
      return false;
		} 
    // Reset if they highlight and type over first char.
    else if ($phone.val().charAt(0) !== '(') {
			$phone.val('('+String.fromCharCode(e.keyCode)+''); 
		}

		// Auto-format- do not expose the mask as the user begins to type
		if (key !== 8 && key !== 9) {
			if ($phone.val().length === 4) {
				$phone.val($phone.val() + ')');
			}
			if ($phone.val().length === 5) {
				$phone.val($phone.val() + ' ');
			}			
			if ($phone.val().length === 9) {
				$phone.val($phone.val() + '-');
			}
		}

		// Allow numeric (and tab, backspace, delete) keys only
		return (key == 8 || 
				key == 9 ||
				key == 46 ||
				(key >= 48 && key <= 57) ||
				(key >= 96 && key <= 105));	
	})
	
	.bind('focus click', function () {
		$phone = $(this);
		
		if ($phone.val().length === 0) {
			$phone.val('(');
		}
		else {
			var val = $phone.val();
			$phone.val('').val(val); // Ensure cursor remains at the end
		}
	})
	
	.blur(function () {
		$phone = $(this);
		
		if ($phone.val() === '(') {
			$phone.val('');
		}
	});