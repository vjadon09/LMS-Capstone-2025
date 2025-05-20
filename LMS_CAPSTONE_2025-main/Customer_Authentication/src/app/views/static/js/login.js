// Define a function to handle the form submission
async function handleLoginFormSubmit(event) {
  event.preventDefault();

  // Get the values of the email and password fields
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Get the error message container
  const errorMessage = document.getElementById('errorMessage');
  
  // Clear any previous error message
  errorMessage.style.display = 'none';
  errorMessage.textContent = '';

  // Check if either email or password is empty
  if (email === '') {
    errorMessage.textContent = 'Enter your email';
    errorMessage.style.display = 'block';
    return; // Prevent form submission
  } 
  else if (password === '') {
    errorMessage.textContent = 'Enter your password';
    errorMessage.style.display = 'block';
    return; // Prevent form submission
  }

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        email: email,
        pword: password,
      }),
    });

    // Check if the response is not OK
    if (!response.ok) {
      const errorResponse = await response.json();
      errorMessage.textContent = errorResponse.detail;
      errorMessage.style.display = 'block';
      setTimeout(() => {errorMessage.style.display = 'none';}, 1000); 
    } 
    else {
      window.location.href = "/auth/home";
    }

  } catch (error) {
    console.error("Error during login:", error);
    errorMessage.textContent = "An error occurred. Please try again.";
    errorMessage.style.display = 'block';
  }
}

// Add an event listener for the form submission
document.getElementById('loginForm').addEventListener('submit', handleLoginFormSubmit);
