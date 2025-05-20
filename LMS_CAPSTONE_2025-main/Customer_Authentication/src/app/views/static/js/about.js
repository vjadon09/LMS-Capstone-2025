async function submitContactForm() {
    const name = document.getElementById("contact-name").value;
    const email = document.getElementById("contact-email").value;
    const message = document.getElementById("contact-message").value;
  
    try {
      const response = await fetch("/auth/send-message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: name,
          email: email,
          message: message
        })
      });
  
      const result = await response.json();
  
      if (response.ok) {
        alert(result.message);
        document.getElementById("contactForm").reset();
      } else {
        alert(result.error || "To prevent spam, please wait before resending your message.");
        document.getElementById("contactForm").reset();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Network error. Please try again.");
    }
  }
  