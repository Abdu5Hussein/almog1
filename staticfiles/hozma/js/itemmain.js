const jwtToken_access = localStorage.getItem("session_data@access_token")?.replace(/"/g, '');
let cart = JSON.parse(localStorage.getItem('product_cart')) || [];

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
  updateCartUI();


  // Add event listener for Enter key in filter inputs

});


function updateCart() {
  localStorage.setItem('product_cart', JSON.stringify(cart));
  updateCartUI();
}