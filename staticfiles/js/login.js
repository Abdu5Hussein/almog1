document.addEventListener("DOMContentLoaded", () => {
    /* -------------------------------------------------
     * 1. Elements
     * -------------------------------------------------*/
    const loginForm = document.getElementById("login-form");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");

    /* -------------------------------------------------
     * 2. Submit handler
     * -------------------------------------------------*/
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const csrfToken = document.querySelector("[name='csrfmiddlewaretoken']")?.value || "";

        // Get the role from a select input or radio buttons in your form
        // Example: <select id="role"><option value="employee">Employee</option><option value="client">Client</option></select>
        const roleElement = document.getElementById("role");
        const role = roleElement ? roleElement.value : "employee";  // default to employee if no selector

        const payload = {
            username: document.getElementById("username").value.trim(),
            password: passwordInput.value,
            role: role,  // dynamically set role
        };

        try {
            const res = await fetch("http://45.13.59.226/process-login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });

            const result = await res.json();

            if (res.ok) {
                /* ---------- Save response values ---------- */
                localStorage.setItem("session_data@username", JSON.stringify(result.username));
                localStorage.setItem("session_data@name", JSON.stringify(result.name));
                localStorage.setItem("session_data@role", JSON.stringify(result.role));
                localStorage.setItem("session_data@user_id", JSON.stringify(result.user_id));
                localStorage.setItem("session_data@access_token", JSON.stringify(result.access_token));
                localStorage.setItem("session_data@refresh_token", JSON.stringify(result.refresh_token));

                // Save employee/client-specific IDs and types if present
                if (role === "employee") {
                    localStorage.setItem("session_data@emp_id", JSON.stringify(result.emp_id));
                    localStorage.setItem("session_data@employee_type", JSON.stringify(result.employee_type));
                } else if (role === "client") {
                    localStorage.setItem("session_data@client_id", JSON.stringify(result.client_id));
                }

                /* ---------- Redirect ---------- */
                window.location.href = result.redirect_url || "/login";

            } else {
                showError(result.message || "Login failed. Please try again.");
            }
        } catch {
            showError("An error occurred. Please check your internet connection.");
        }
    });

    /* -------------------------------------------------
     * 3. Password visibility toggle
     * -------------------------------------------------*/
    togglePassword.addEventListener("click", () => {
        const hidden = passwordInput.type === "password";
        passwordInput.type = hidden ? "text" : "password";
        eyeIcon.classList.toggle("bi-eye", !hidden);
        eyeIcon.classList.toggle("bi-eye-slash", hidden);
    });

    /* -------------------------------------------------
     * 4. Helper – flash error message
     * -------------------------------------------------*/
    function showError(msg) {
        const box = document.createElement("div");
        box.className = "alert alert-danger mb-2";
        box.textContent = msg;
        (document.querySelector(".card-body") || document.body).prepend(box);
        setTimeout(() => box.remove(), 5_000);
    }
});