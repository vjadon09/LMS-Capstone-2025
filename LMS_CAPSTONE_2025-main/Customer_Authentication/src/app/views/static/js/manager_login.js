// Define a function to handle the form submission
async function handleLoginFormSubmit(event) {
  // Prevent the form from submitting normally (page reload)
  event.preventDefault();

  // Get the values of the userId and password fields
  const userId = document.getElementById('user-id').value;
  const password = document.getElementById('password').value;

  // Get the error message container
  const formErrorMessage = document.getElementById('errorMessage');
  
  // Clear any previous error message
  formErrorMessage.style.display = 'none';
  formErrorMessage.textContent = '';

  // Check if either userId or password is empty
  if (userId === '') {
    formErrorMessage.textContent = 'Enter your admin id';
    formErrorMessage.style.display = 'block'; // Show error message
    setTimeout(() => {
      formErrorMessage.style.display = 'none';
    }, 1500);
    return; 
  }
  if (password === '') {
    formErrorMessage.textContent = 'Enter your password';
    formErrorMessage.style.display = 'block'; // Show error message
    setTimeout(() => {
      formErrorMessage.style.display = 'none';
    }, 1500);
    return;
  }
  const response = await fetch('/auth/manager', {
    method: 'POST',
    body: new FormData(document.getElementById('loginForm')),
  });

  if (!response.ok) {
    // If the login failed, get the error message from the JSON response
    const errorData = await response.json();
    formErrorMessage.textContent = errorData.error;  // Display the error message
    formErrorMessage.style.display = 'block';  // Show error message
    setTimeout(() => {
      formErrorMessage.style.display = 'none'; // Hide it after 1.5s
    }, 1500);
  } else {
    const successData = await response.json();
    console.log(successData);
    if (successData.url) {
      window.location.href = successData.url;
    } else {
      window.location.href = "/auth/login";
    }
  }
}

// Add an event listener for the form submission
document.getElementById('loginForm').addEventListener('submit', handleLoginFormSubmit);
