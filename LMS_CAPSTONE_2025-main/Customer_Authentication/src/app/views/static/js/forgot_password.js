// Define a function to handle the form submission
async function handleLoginFormSubmit(event) {
    // Prevent the form from submitting normally (page reload)
    // event.preventDefault();
  
    // Get the values of the email and password fields
    const email = document.getElementById('email').value;
    const itemData = {email: email};

    // Get the error message container
    const errorMessage = document.getElementById('errorMessage');
    
    // Clear any previous error message
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';

    // Check if either email or password is empty
    if (email === ''){
      errorMessage.textContent = 'Fill in email field';
      errorMessage.style.display = 'block'; // Show error message
    }
    else{
      console.log('Email:', email);
    }
}

document.getElementById('forgot-password-form').addEventListener('submit', handleLoginFormSubmit);
 


  