// ON PAGE LOAD ...
cancelBtn = document.getElementById('cancelBtn')
saveBtn = document.getElementById('saveBtn')
applicant = document.getElementById('applicantID')

cancelBtn.style.display='none'
saveBtn.style.display='none'

// DEFINE EVENT LISTENERS
document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)
document.getElementById("selectpicker").addEventListener("click",memberSelectedRtn)
applicant.addEventListener("change",applicantDataChanged)
$.fn.selectpicker.Constructor.BootstrapVersion = '4';
// $(document).ready(function() {
//     $('select').selectpicker();
// })





// FUNCTIONS 
function memberSelectedRtn() {
    selectedMember = this.value
    lastEight = selectedMember.slice(-8)
    currentMemberID= lastEight.slice(1,7)
    document.getElementById('selectpicker').value=''
    

    // if (selectedMember == 'NEW APPLICANT') {
    //     alert('New applicant')
    // }

    // SET UP LINK TO waitList FORM 
    var linkToWaitListBtn = document.getElementById('linkToWaitList');
    link='/waitList/' + currentMemberID 
    linkToWaitListBtn.setAttribute('href', link)
    linkToWaitListBtn.click()
}


function showMenu() {
    document.getElementById("myDropdown").classList.toggle("show");
  }

  // Close the dropdown if the user clicks outside of it
  window.onclick = function(event) {
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

function applicantDataChanged() {
    document.getElementById('cancelBtn').style.display='inline'
    document.getElementById('saveBtn').style.display='inline'
}
