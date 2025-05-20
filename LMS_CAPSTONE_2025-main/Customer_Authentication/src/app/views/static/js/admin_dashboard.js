var today = new Date()
var curHr = today.getHours()

if (curHr >= 0 && curHr <= 12) {
    document.getElementById("greeting").innerHTML = 'Good Morning {{name}} 🖥️';
} else if (curHr >= 12 && curHr < 17) {
    document.getElementById("greeting").innerHTML = 'Good Afternoon {{name}} 🖥️';
} else {
    document.getElementById("greeting").innerHTML = 'Good Evening {{name}} 🖥️';
}

function editInventory(){
    location.href = "edit_inventory.html";
}