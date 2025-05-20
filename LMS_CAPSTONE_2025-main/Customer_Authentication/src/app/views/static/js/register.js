// Define a function to handle the form submission
async function handleLoginFormSubmit(event) {
  // Prevent the form from submitting normally (page reload)
  event.preventDefault();

  // Get the values of the email and password fields
  const fname = document.getElementById("first-name").value;
  const lname = document.getElementById("last-name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const age = parseInt(document.getElementById("age").value, 10);
  const repassword = document.getElementById("re-password").value;

  // Get the error message container
  const errorMessage = document.getElementById("errorMessage");

  // Clear any previous error message
  errorMessage.style.display = "none";
  errorMessage.textContent = "";

  // Check if either email or password is empty
  if (fname === "" || lname === "" || email === "" || password === "" || repassword === "" || age.toString() === "") {
    errorMessage.textContent = "Fill in required fields";
    errorMessage.style.display = "block"; // Show error message
    return;
  }
  if (password !== repassword) {
    errorMessage.textContent = "Passwords do not match";
    errorMessage.style.display = "block"; // Show error message
    setTimeout(() => {errorMessage.style.display = 'none';}, 1000); 
    return;
  }

  try {
    const response = await fetch("/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        fname: fname,
        lname: lname,
        email: email,
        password: password,
        age: age.toString(),
      }),
    });

    if (!response.ok) {
      const errorResponse = await response.json();
      errorMessage.textContent = errorResponse.detail;
      errorMessage.style.display = "block"; 
      setTimeout(() => {errorMessage.style.display = 'none';}, 1000); 
    } 
    else {
      window.location.href = "/auth/login"; 
    }

  } catch (error) {
    console.error("Error during registration:", error);
    errorMessage.textContent = "An error occurred. Please try again.";
    errorMessage.style.display = "block"; 
  }
}

function clear(){
  document.getElementById("registerForm").reset();
}

document
  .getElementById("registerForm")
  .addEventListener("submit", handleLoginFormSubmit);
