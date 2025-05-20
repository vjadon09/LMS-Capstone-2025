//function to check passwords match
function checkPasswords(){
    const pass = document.getElementById("password");
    const newPass = document.getElementById("re-password");

    if (pass.value !== newPass.value) { //check the rentered password
        const passErrorMessage = document.getElementById('passwordErrorMessage');  
        passErrorMessage.textContent = 'Passwords do not match';  
        passErrorMessage.style.display = 'block';  
        return false;
    } else {
        const passErrorMessage = document.getElementById('passwordErrorMessage');
        passErrorMessage.style.display = 'none';  
        return true;
    }  
}

document.getElementById("user-register-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));
    if (!checkPasswords()) {
      //alert("Passwords do not match. Fix errors before submitting.");
      return;
    }

    const formData = new FormData();
    formData.append("firstName", document.getElementById("first-name").value);
    formData.append("lastName", document.getElementById("last-name").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("password", document.getElementById("password").value);
    const isManager = document.getElementById("is-manager").checked;
    formData.append("isManager", isManager ? "true" : "false");

    if (isManager) {
      formData.append("managerID", document.getElementById("manager-id").value);
    } else {
      formData.append("age", document.getElementById("age").value);
    }
    for (let [key, value] of formData.entries()) {
      console.log(`${key}: ${value}`);
    }
    
    try {
      const response = await fetch("/userManage/users/add-user", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const result = await response.json();

      if (response.ok) {
        document.getElementById('modal-body').innerHTML = formatModal(false, result.message);
        myModal.show();
        const closeButton = document.querySelector('.btn-close');
        closeButton.addEventListener('click', function () {
          window.location.href = "/userManage/add-user";
        });
      } else {
        document.getElementById('modal-body').innerHTML = formatModal(true, result.message);
        myModal.show();
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      document.getElementById('modal-body').innerHTML = formatModal(true, 'Error submitting form');
      myModal.show();
    }
  });


//clear any password or user exist errors when refresh form
function clearErrors(){
    const passErrorMessage = document.getElementById('passwordErrorMessage');
    passErrorMessage.style.display = 'none';

    const userErrorMessage = document.getElementById('user-error-message');  
    userErrorMessage.style.display = 'none';
}

function checkManager() {
  var managerCheckbox = document.getElementById("is-manager");
  var managerIDField = document.getElementById("manager-id-row");
  var ageField = document.getElementById("age-row");

  // Show Manager ID input and hide Age field if checked
  if (managerCheckbox.checked) {
      managerIDField.style.display = "block";
      ageField.style.display = "none"; // Hide age field when manager is selected
  } else {
      managerIDField.style.display = "none";
      ageField.style.display = "block"; // Show age field when manager is not selected
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