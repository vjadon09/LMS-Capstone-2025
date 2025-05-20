// Define a function to handle the form submission
async function handleLoginFormSubmit(event) {
    // Prevent the form from submitting normally (page reload)
    event.preventDefault();
  
    // Get the values of the email and password fields
    const userId = document.getElementById('user-id').value;
    const password = document.getElementById('password').value;
    const itemData = {userId: userId, password: password};

    // Get the error message container
    const errorMessage = document.getElementById('errorMessage');
    
    // Clear any previous error message
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';

    // Check if either email or password is empty
    if (userId === ''){
      errorMessage.textContent = 'Enter your admin id';
      errorMessage.style.display = 'block'; // Show error message
    }
    else if (password === ''){
      errorMessage.textContent = 'Enter your password';
      errorMessage.style.display = 'block'; // Show error message
    }
    else {
      console.log('Email:', userId);
      console.log('Password:', password);
      location.href = "admin_dashboard.html";
    }
  }
  // Add an event listener for the form submission
  document.getElementById('loginForm').addEventListener('submit', handleLoginFormSubmit);
  