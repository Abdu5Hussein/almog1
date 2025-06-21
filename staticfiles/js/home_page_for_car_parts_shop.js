document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById("sidebar-toggler");
    const sidebar = document.getElementById("sidebar");
    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("show");
    });

    document.querySelectorAll(".toggle-submenu").forEach((item) => {
        item.addEventListener("click", (event) => {
            event.preventDefault();
            const submenu = item.nextElementSibling;
            document.querySelectorAll(".sub-menu").forEach((sub) => {
                if (sub !== submenu) {
                    sub.style.display = "none";
                }
            });
            submenu.style.display =
                submenu.style.display === "block" ? "none" : "block";
        });
    });

    document.getElementById("logout-btn").addEventListener("click", function () {
        logoutFunction();
    });

    function logoutFunction() {
        const access_token = localStorage.getItem("session_data@access_token").replace(/"/g, '');
        const refresh_token = localStorage.getItem("session_data@refresh_token").replace(/"/g, '');
        const data = {
            "refresh": refresh_token,
            "access": access_token,
        };
        customFetch(`/api/user/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((result) => {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = "/login";
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }

});