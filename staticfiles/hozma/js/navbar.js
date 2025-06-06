
  
  // Highlight current page in navbar
  // Highlight current page in navbar
// Highlight current page in navbar
document.addEventListener('DOMContentLoaded', function() {
  const navLinks = document.querySelectorAll('.hozma-nav-link');
  const currentPage = window.location.pathname.split('/').filter(Boolean).pop() || 'index.html';

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;

    const linkPage = href.split('/').filter(Boolean).pop();

    if (link.classList.contains('hozma-dropdown-toggle')) {
      const dropdownMenu = link.nextElementSibling;
      if (dropdownMenu) {
        const dropdownItems = dropdownMenu.querySelectorAll('.hozma-dropdown-item');
        dropdownItems.forEach(item => {
          const itemHref = item.getAttribute('href').split('/').filter(Boolean).pop();
          if (itemHref === currentPage) {
            link.classList.add('active');
          }
        });
      }
    } else if (linkPage === currentPage) {
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


  // Cart badge animation
// Cart badge animation
function animateCart() {
  const badge = document.getElementById('hozmaCartBadge');
  if (badge) {
    badge.classList.add('pulse');
    setTimeout(() => badge.classList.remove('pulse'), 500);
  }
}
