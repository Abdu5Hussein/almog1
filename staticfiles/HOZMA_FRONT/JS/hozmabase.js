// static/js/base.js

// ———————————————————————————————————————————————————————————————
// 1) Update notification counts, shop-confirmed status, etc.
// ———————————————————————————————————————————————————————————————
document.addEventListener("DOMContentLoaded", function () {
    // Fetch invoice‐related stats (new orders today, shop‐confirmed this month, total invoices, % increase)
    customFetch('http://45.13.59.226/hozma/api/invoice-stats/')
        .then(res => res.json())
        .then(data => {
            // Update the number of new orders badges (in navbar and sidebar)
            const newOrdersSidebar = document.getElementById('new-orders-count1');
            const newOrdersNav     = document.getElementById('new-orders-count');
            if (newOrdersSidebar) newOrdersSidebar.textContent = data.new_unconfirmed_orders_today;
            if (newOrdersNav)     newOrdersNav.textContent     = data.new_unconfirmed_orders_today;

            // Update the shop-confirmed‐this‐month text and class
            const shopConfirmedEl = document.getElementById('shop-confirmed-count');
            if (shopConfirmedEl) {
                shopConfirmedEl.textContent = 'تم تأكيدها من قبل المتجر: ' + data.shop_confirmed_this_month;
                if (data.shop_confirmed_this_month > 0) {
                    shopConfirmedEl.classList.remove('text-danger');
                    shopConfirmedEl.classList.add('text-success'); // أخضر إذا في تأكيد
                } else {
                    shopConfirmedEl.classList.remove('text-success');
                    shopConfirmedEl.classList.add('text-danger');  // أحمر إذا ما في تأكيد
                }
            }

            // Update the total‐invoices‐this‐month text
            const totalInvEl = document.getElementById('current-month-invoice-count');
            if (totalInvEl) {
                totalInvEl.textContent = 'إجمالي الفواتير: ' + data.current_month_invoice_count;
            }

            // Update the percentage‐increase badge
            const pctIncEl = document.getElementById('percentage-increase');
            if (pctIncEl) {
                pctIncEl.textContent = data.percentage_increase + '%';
            }
        })
        .catch(err => console.error("Error loading stats:", err));
});


// ———————————————————————————————————————————————————————————————
// 2) Read session_data@EMPname / session_data@EMPusername and fill sidebar
// ———————————————————————————————————————————————————————————————
document.addEventListener("DOMContentLoaded", function () {
    try {
        const username = localStorage.getItem("session_data@EMPname");
        const email    = localStorage.getItem("session_data@EMPusername");

        const nameEl  = document.getElementById('userNamePlaceholder');
        const emailEl = document.getElementById('userEmailPlaceholder');

        if (username) {
            if (nameEl)  nameEl.textContent  = username;
            if (email && emailEl) emailEl.textContent = email;
        } else {
            // If nothing is in localStorage, use defaults
            if (nameEl)  nameEl.textContent  = "حسابي";
            if (emailEl) emailEl.textContent = "غير معروف";
            console.warn("No user data found in localStorage. Sidebar will show default text.");
        }
    } catch (e) {
        console.error('Error accessing localStorage for user info:', e);
    }
});


// ———————————————————————————————————————————————————————————————
// 3) Fetch employee image and inject into both navbar & sidebar
// ———————————————————————————————————————————————————————————————
document.addEventListener("DOMContentLoaded", async () => {
    const rawId = localStorage.getItem('session_data@emp_id');
    if (!rawId) return;

    const employeeId = rawId.replace(/"/g, '');
    try {
        const res = await fetch(`/hozma/employees/${employeeId}/get-image/`, {
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const { employee_image } = await res.json();

        // If API returned a URL, use it; otherwise fallback to default static
        const defaultImage = '/static/HOZMA_FRONT/images/default-profile.png';
        const finalImage   = employee_image
            ? (employee_image.startsWith('http') ? employee_image : `${window.location.origin}${employee_image}`)
            : defaultImage;

        // Apply to both <img> tags: #employee-profile-image (navbar) & #employee-profile-image-profile (sidebar)
        const imgNavbar  = document.getElementById('employee-profile-image');
        const imgSidebar = document.getElementById('employee-profile-image-profile');

        if (imgNavbar)  imgNavbar.src  = finalImage;
        if (imgSidebar) imgSidebar.src = finalImage;
    } catch (err) {
        console.error('Error loading employee image:', err);
    }
});


// ———————————————————————————————————————————————————————————————
// 4) Logout button handler
// ———————————————————————————————————————————————————————————————
document.addEventListener("DOMContentLoaded", function () {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (e) {
            e.preventDefault();
            logoutFunction();
        });
    }
});

function logoutFunction() {
    fetch(`/api/user/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(result => {
        console.log("Logged out successfully:", result);
        // Redirect to login page
        window.location.href = "/login";
    })
    .catch(error => {
        console.error("Error logging out:", error);
    });
}
