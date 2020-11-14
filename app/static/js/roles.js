// roles.js
document.getElementById("roleCancelBtnID").addEventListener("click",cancelRole)
document.getElementById("roleSaveBtnID").addEventListener("click",saveRole)

// EVENT LISTENERS
document.getElementById('roleBodyID').addEventListener('change',roleDataChanged);

// FUNCTIONS
function roleDataChanged() {
    alert('change occurred')
    document.getElementById('roleCancelBtnID').style.display='inline';
    document.getElementById('roleSaveBtnID').style.display='inline';
}

function cancelRole() {
    alert('cancelRole rtn')
}

function saveRole() {
    alert('saveRole rtn')
}