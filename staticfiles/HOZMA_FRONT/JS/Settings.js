
document.addEventListener('DOMContentLoaded', function () {
    try {
        const username = localStorage.getItem("session_data@name");
        const email = localStorage.getItem("session_data@username"); // optional if you store it

        const nameElement = document.getElementById('userNamePlaceholder');
        const emailElement = document.getElementById('userEmailPlaceholder');

        if (username) {
            nameElement.textContent = username;
            if (email) {
                emailElement.textContent = email;
            }
        } else {
            nameElement.textContent = "حسابي";
            emailElement.textContent = "غير معروف";
            alert("No user data found. Please log in.");
        }
    } catch (e) {
        console.error('Error accessing localStorage:', e);
    }
});


document.addEventListener('DOMContentLoaded', async () => {
    const raw = localStorage.getItem('session_data@emp_id');
    if (!raw) return;
  
    const employeeId = raw.replace(/"/g, '');
  
    try {
      const res = await fetch(`/hozma/employees/${employeeId}/get-image/`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
      });
  
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { employee_image } = await res.json();
  
      const defaultImage = '/static/HOZMA_FRONT/images/default-profile.png';
      const finalImage = employee_image
        ? (employee_image.startsWith('http') ? employee_image : `${window.location.origin}${employee_image}`)
        : defaultImage;
  
      // Set both image sources
      const img1 = document.getElementById('employee-profile-image');
      const img2 = document.getElementById('employee-profile-image-profile');
      if (img1) img1.src = finalImage;
      if (img2) img2.src = finalImage;
  
    } catch (err) {
      console.error('Error loading employee image:', err);
    }
  });

  document.getElementById("logout-btn").addEventListener("click", function (){
    logoutFunction();
  });

  function logoutFunction() {
    fetch(`/api/user/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        console.log("Logged out successfully");

        // Redirect to login page
        window.location.href = "/login";
      })
      .catch((error) => {
        console.error("Error logging out:", error);
      });
  }