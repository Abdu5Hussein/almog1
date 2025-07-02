document.addEventListener("DOMContentLoaded", function () {

  document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission

    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    // Get form values
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = "client";

    // Prepare the request payload
    const payload = {
      username: username,
      password: password,
      role: role
    };
    console.log(payload);
    try {
      // Send POST request
      const response = await fetch("/mobile/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok) {
        // Store session data in local storage
        if (result.session_data) {
          localStorage.setItem("session_data@username", JSON.stringify(result.session_data.username));
          localStorage.setItem("session_data@name", JSON.stringify(result.session_data.name));
          localStorage.setItem("session_data@role", JSON.stringify(result.session_data.role));
          const rawUserId = result.session_data.user_id; // e.g., "c-14"
          const cleanedUserId = rawUserId.replace(/^c-/, ""); // removes only "c-" from the start
          localStorage.setItem("session_data@user_id", JSON.stringify(cleanedUserId));

          localStorage.setItem("session_data@access_token", JSON.stringify(result.access_token.replace(/"/g, '')));
          localStorage.setItem("session_data@refresh_token", JSON.stringify(result.refresh_token.replace(/"/g, '')));
        }
        console.log(result);
        // Redirect to dashboard on success


        window.location.href = "/hozma/products/"; // Change to your actual dashboard route
        // Change to your actual dashboard route
      } else {
        // Show error message
        showError(result.message || "Login failed. Please try again.");
      }
    } catch (error) {
      showError("An error occurred. Please check your internet connection.");
    }
  });

  function showError(message) {
    const alertBox = document.createElement("div");
    alertBox.className = "alert alert-danger";
    alertBox.textContent = message;
    const formContainer = document.querySelector(".card-body");
    formContainer.insertBefore(alertBox, formContainer.firstChild);

    // Remove the error message after 5 seconds
    setTimeout(() => alertBox.remove(), 5000);
  }
});

const passwordInput = document.getElementById("password");
const togglePasswordBtn = document.getElementById("togglePassword");
const eyeIcon = document.getElementById("eyeIcon");

togglePasswordBtn.addEventListener("click", () => {
  const type = passwordInput.type === "password" ? "text" : "password";
  passwordInput.type = type;
  eyeIcon.classList.toggle("bi-eye");
  eyeIcon.classList.toggle("bi-eye-slash");
});
