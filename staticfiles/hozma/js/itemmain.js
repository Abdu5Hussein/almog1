const baseUrl = "http://45.13.59.226";
const jwtToken_access = localStorage.getItem("session_data@access_token")?.replace(/"/g, '');
let cart = JSON.parse(localStorage.getItem('product_cart')) || [];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
  updateCartUI();
  applyFilters();
  
  // Add event listener for Enter key in filter inputs
  const filterInputs = document.querySelectorAll('.filters input');
  filterInputs.forEach(input => {
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        applyFilters();
      }
    });
  });
});

async function fetchWithAuth(url, method = 'GET', body = null) {
  const headers = {
    'Authorization': `Bearer ${jwtToken_access}`,
    'Content-Type': 'application/json'
  };
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      if (response.status === 401) {
        alert("تم تسجيل الخروج بسبب انتهاء الجلسة.");
        localStorage.clear();
        window.location.href = "/hozmalogin/";
      }
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
}

async function postWithAuth(url, data) {
  const headers = {
    'Authorization': `Bearer ${jwtToken_access}`,
    'Content-Type': 'application/json'
  };
  const options = {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  };

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      if (response.status === 401) {
        alert("تم تسجيل الخروج بسبب انتهاء الجلسة.");
        localStorage.clear();
        window.location.href = "/hozmalogin/";
      }
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
}


function updateCart() {
  localStorage.setItem('product_cart', JSON.stringify(cart));
  updateCartUI();
}