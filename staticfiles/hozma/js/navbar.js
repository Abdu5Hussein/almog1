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
  document.addEventListener('DOMContentLoaded', function() {
    // Navbar search form submit handler
    const navbarSearchForm = document.getElementById('navbarSearchForm');
    const navbarSearchInput = document.getElementById('navbarSearchInput');
    if (navbarSearchForm) { // Check if the element exists
      navbarSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const searchTerm = navbarSearchInput.value.trim();
        currentFilters.itemno = searchTerm;
        currentFilters.itemmain = '';
        currentFilters.itemsubmain = '';
        currentFilters.engine_no = '';
        currentPage = 1;
        document.getElementById('pageInput').value = 1;
        document.getElementById('productList').innerHTML = "";
        document.getElementById('loading-spinner').style.display = 'block';
        loadMoreItems();
      });
    } else {
      console.error("Element with ID 'navbarSearchForm' not found.");
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    // Check if user session data is available in localStorage
    const username = JSON.parse(localStorage.getItem("session_data@username"));
    const userNamePlaceholder = document.getElementById('userNamePlaceholder');
    
    if (username) {
        // If the user is logged in, update the account button text with the username
        userNamePlaceholder.textContent = `مرحبًا, ${username}`;
        document.getElementById('accountButton').href = "/my-account"; // Ensure it's pointing to the user's account page
    } else {
        // If no username is found, ensure it's showing the default "حسابي"
        userNamePlaceholder.textContent = "حسابي";
        document.getElementById('accountButton').href = "/login"; // Redirect to login if not logged in
    }

    // Rest of your navbar functionality like highlighting current page...
});
