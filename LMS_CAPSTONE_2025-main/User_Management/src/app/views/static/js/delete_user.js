let user = [];

async function getUserInfo() {
    try {
        const user_email = document.getElementById("user_email").innerText;
        const response = await fetch(`/userManage/customer-info/${user_email}`);
        
        if (!response.ok) {
            alert("Error getting the user's information!");
        }
        
        user = await response.json();
        console.log("User Data:", user);
        
        // After getting user data, load it
        loadUserInfo(user);
        
    } catch (error) {
        console.error("Failed to fetch user info:", error);
    }
}

function loadUserInfo(user) {
    userStatus = document.getElementById("status").innerText;

    const firstName = document.getElementById("first-name");
    firstName.textContent = user.firstName; 

    const lastName = document.getElementById("last-name");
    lastName.textContent = user.lastName;

    if (userStatus === "Manager"){
      const managerID = document.getElementById("managerID");
      managerID.textContent = user.managerID;
      const password = document.getElementById("password");
      password.textContent = user.password;
      
    } else if (userStatus === "Customer"){
      const age = document.getElementById("age");
      age.textContent = user.age;
      const password = document.getElementById("password");
      password.textContent = user.password;
    }

    const email = document.getElementById("email");
    email.textContent = user.email;
}

async function deleteUser(event) {
  event.preventDefault();
  var myModal = new bootstrap.Modal(document.getElementById('successModal'));
  try {
    userStatus = document.getElementById("status").innerText;
    console.log(userStatus);
    let response;
    
    if (userStatus === "Manager"){
      response = await fetch(`/userManage/users/delete-user/${user.managerID}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: user.managerID }),
      });
    } else {
      response = await fetch(`/userManage/users/delete-user/${user.email}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: user.email }),
      });
    }

    if (!response.ok) {
      const result = await response.json()
      document.getElementById('modal-body').innerHTML = formatModal(true, result.message);
      console.log(result.message);
    } else {
      const result = await response.json()
      document.getElementById('modal-body').innerHTML = formatModal(false, result.message);
      console.log(result.message);    
    }
    myModal.show();
    const closeButton = document.querySelector('.btn-close');
    closeButton.addEventListener('click', function () {
      window.location.href = "/userManage/main";
    });
  } catch (error) {
    console.error("Failed to delete user:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
    getUserInfo();
});

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

function formatModal(error, message){
  let modalBody;
  if (error){
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">❎</p></div>
                <div class="row"><p class="text-center fs-5">${message}</p></div>`;
    
  } else{
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">✅</p></div>
                <div class="row"><p class="text-center fs-5">${message}</p></div>`;
  }
  return modalBody
}

document.getElementById('delete-profile-form').addEventListener('submit', deleteUser);
