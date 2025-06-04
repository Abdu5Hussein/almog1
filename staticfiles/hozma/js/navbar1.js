// Change navbar style on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
  
  // Highlight current page in navbar
  // Highlight current page in navbar
document.addEventListener('DOMContentLoaded', function() {
  const navLinks = document.querySelectorAll('.nav-link-auto');
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  
  navLinks.forEach(link => {
    const linkPage = link.getAttribute('href').split('/').pop();
    
    // Special handling for dropdown parent items
    if (link.classList.contains('dropdown-toggle')) {
      const dropdownItems = link.nextElementSibling.querySelectorAll('.dropdown-item');
      let shouldActivateParent = false;
      
      dropdownItems.forEach(item => {
        const itemHref = item.getAttribute('href').split('/').pop();
        if (itemHref === currentPage) {
          shouldActivateParent = true;
        }
      });
      
      if (shouldActivateParent) {
        link.classList.add('active');
      }
    }
    // Regular links
    else if (linkPage === currentPage) {
      link.classList.add('active');
    }
  });
});
  
  // Navbar search form submit handler
  // In navbar.js
  

  document.addEventListener('DOMContentLoaded', function () {
    try {
        const username = localStorage.getItem("session_data@name");
        const userNamePlaceholder = document.getElementById('userNamePlaceholder');

        if (username) {
            userNamePlaceholder.textContent = `مرحبًا, ${username}`;
            document.getElementById('accountButton').href = "/hozma/hozmaDashbord/";
        } else {
            userNamePlaceholder.textContent = "حسابي";
            document.getElementById('accountButton').href = "/hozma/login";
            alert("No user data found. Please log in.");
        }
    } catch (e) {
        console.error('Error accessing localStorage:', e);
    }
});



  function toggleFilters() {
    const filterDiv = document.getElementById('filterContainer');
    const button = document.getElementById('toggleFilterBtn');
    
    if (filterDiv.classList.contains('show')) {
      filterDiv.classList.remove('show');
      filterDiv.classList.add('collapse');
      button.innerHTML = '<i class="bi bi-funnel"></i> إظهار الفلاتر';
    } else {
      filterDiv.classList.remove('collapse');
      filterDiv.classList.add('show');
      button.innerHTML = '<i class="bi bi-funnel"></i> إخفاء الفلاتر';
    }
  }

  window.addEventListener('scroll', function() {
    if (window.scrollY > 10) {
      document.querySelector('.navbar').classList.add('scrolled');
    } else {
      document.querySelector('.navbar').classList.remove('scrolled');
    }
  });
  
  // Cart badge animation
  function animateCart() {
    const badge = document.getElementById('cartBadge');
    badge.classList.add('pulse');
    setTimeout(() => badge.classList.remove('pulse'), 500);
  }

  async function signOutClient() {
    const sessionData = JSON.parse(localStorage.getItem("session_data@username"));
    const role = JSON.parse(localStorage.getItem("session_data@role"));
    const payload = { username: sessionData, role: role };
  
    const res = await fetch("/mobile/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });
  
    if (res.ok) {
      localStorage.clear();
      window.location.href = "/hozma/hozmalogin/";
    } else {
      const err = await res.json();
      console.error("Logout error:", err);
      alert("حدث خطأ أثناء تسجيل الخروج. حاول مرة أخرى.");
    }
  }
  