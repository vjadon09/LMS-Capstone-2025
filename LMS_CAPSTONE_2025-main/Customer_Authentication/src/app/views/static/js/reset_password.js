async function resetPassword(event){
    event.preventDefault();

    const new_password = document.getElementById('password').value;
    const re_entered_password = document.getElementById('re-password').value;
  
    const passErrorMessage = document.getElementById('passwordErrorMessage');
    passErrorMessage.style.display = 'none';
    passErrorMessage.textContent = '';
  
    if (new_password === '' || re_entered_password ===''){
      passErrorMessage.textContent = 'Enter required fields';
      passErrorMessage.style.display = 'block'; // Show error message      
    }
    else if (new_password !== re_entered_password){
      passErrorMessage.textContent = 'Passwords do not match';
      passErrorMessage.style.display = 'block'; // Show error message   
    }
    else {
      console.log("Password", new_password);
    }
  }

  document.getElementById('reset-password-form').addEventListener('submit', resetPassword);

  // Define a function to handle the form submission
async function resetPassword(event) {
  event.preventDefault();
  
  // Get the values of the new password and re-entered password fields
  const new_password = document.getElementById('password').value;
  const re_entered_password = document.getElementById('re-password').value;

  // Get the error message container
  const passErrorMessage = document.getElementById('passwordErrorMessage');
  passErrorMessage.style.display = 'none';
  passErrorMessage.textContent = '';

  // Check if fields are empty
  if (new_password === '' || re_entered_password === '') {
      passErrorMessage.textContent = 'Enter required fields';
      passErrorMessage.style.display = 'block';
      return;
  } 
  else if (new_password !== re_entered_password) {
      passErrorMessage.textContent = 'Passwords do not match';
      passErrorMessage.style.display = 'block';
      return;
  }

  // Send a POST request to the server
  try {
      const response = await fetch("/auth/reset_password", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
              first: new_password,
              second: re_entered_password,
          }),
      });

      // Handle server response
      if (response.ok) {
          const successResponse = await response.json();
          alert(successResponse.success);
          window.location.href = "/auth/login";
      } 
      else {
          const errorResponse = await response.json();
          passErrorMessage.textContent = errorResponse.error;
          passErrorMessage.style.display = 'block';
          setTimeout(() => { passErrorMessage.style.display = 'none'; }, 2000); 
      }
  } catch (error) {
      console.error("Error during password reset:", error);
      passErrorMessage.textContent = "An error occurred. Please try again.";
      passErrorMessage.style.display = 'block';
  }
}

document.getElementById('reset-password-form').addEventListener('submit', handleResetPasswordFormSubmit);
