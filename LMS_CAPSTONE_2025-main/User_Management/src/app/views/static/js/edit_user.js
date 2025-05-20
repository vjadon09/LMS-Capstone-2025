/* Notes:
-maybe only submit form if any of the fields change
-need to prevent form from submitting if error 
-same logic as admin edit profile (just copied it)
 */

//load initial user information
let user = [];
let newUser = [];

async function getUserInfo() {
    try {
        const user_email = document.getElementById("user_email").innerText;
        const response = await fetch(`/userManage/customer-info/${user_email}`);
        
        if (!response.ok) {
            alert("Error getting the user's information!");
        }
        
        user = await response.json();
        console.log("User Data:", user);
        
        loadUserInfo(user);
        
    } catch (error) {
        console.error("Failed to fetch user info:", error);
    }
}

function loadUserInfo(user){
    userStatus = document.getElementById("status").innerText;

    const firstName = document.getElementById("first-name");
    firstName.value = user.firstName; 

    const lastName = document.getElementById("last-name");
    lastName.value = user.lastName;

    if (userStatus === "Manager"){
        const email = document.getElementById("managerID");
        email.value = user.managerID;

    } else if (userStatus === "Customer"){
        const age = document.getElementById("age");
        age.value = user.age;
    }

    const email = document.getElementById("email");
    email.value = user.email;
}

//reset the form with user info from db
function resetForm(){
    console.log(user);
    loadUserInfo(user);

    const userErrorMessage = document.getElementById('user-error-message');  
    userErrorMessage.style.display = 'none';
}

//check new passwords match when submitting
async function submitUser(event) {
    event.preventDefault(); 
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));
    const formData = new FormData();
    formData.append("firstName", document.getElementById("first-name").value);
    formData.append("lastName", document.getElementById("last-name").value);
    formData.append("email", document.getElementById("email").value);

    userStatus = document.getElementById("status").innerText;
    if (userStatus === "Customer"){
        formData.append("age", document.getElementById("age").value);
    } else if(userStatus === "Manager"){
        formData.append("managerID", document.getElementById("managerID").value);
    }
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    try {
        let username;
        if (userStatus === "Customer"){
            username = user.email;
        } else {
            username = user.managerID;
        }
        const response = await fetch(`/userManage/users/edit-user/${username}`, {
            method: "POST",
            body: formData,
            credentials: "include" // Ensures cookies (manager_login_token) are sent
        });
        
        const result = await response.json();
        if (response.ok) {
          document.getElementById('modal-body').innerHTML = formatModal(false, result.message);
        } else {
          document.getElementById('modal-body').innerHTML = formatModal(true, result.message);
        }
        myModal.show();
        const closeButton = document.querySelector('.btn-close');
        closeButton.addEventListener('click', function () {
          window.location.href = "/userManage/main";
        });
        
    } catch (error) {
        console.log("An error occurred while editing the user.");
    }
}

function formatModal(error, message){
  let modalBody;
  if (error){
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">❎</p></div>
                <div class="row"><p class="text-center fs-5">${message}</p></div>
                <div class="row"><p class="text-center">Please try again.</p></div>`
    
  } else{
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">✅</p></div>
                <div class="row"><p class="text-center fs-5">${message}!</p></div>`
  }
  return modalBody
}

document.addEventListener("DOMContentLoaded", function () {
    getUserInfo();
    let userStatus = document.getElementById("status").innerText;

    if (userStatus === "Manager") {
        document.getElementById("manager-id-field").style.display = "block";
        document.getElementById("age-field").style.display = "none";
    } else if(userStatus === "Customer"){
        document.getElementById("age-field").style.display = "block";
        document.getElementById("manager-id-field").style.display = "none";
    }
});