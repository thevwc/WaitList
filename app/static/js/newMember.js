alert('newMember.js')
$(document).ready( function() {
    alert('set todays date')
    $('#dateJoined').val(new Date().toDateInputValue());
});​


membershipType = document.getElementById('membershipType')
membershipType.addEventListener('change',displayTotalFee);


function displayTotalFee() {
    initiationFee = document.getElementById('initiationFee').value
    annualFee = document.getElementById('annualFee').value
    if (membershipType.value == 'single') {
        totalFee = initiationFee + annualFee
    }
    else{
        totalFee = (initiationFee / 2) + annualFee
    }
    // format to currency
    document.getElementById('totalFee').value=totalFee;
}