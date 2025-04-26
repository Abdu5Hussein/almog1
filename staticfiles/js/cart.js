const baseUrl = "http://45.13.59.226:8000/api/v1/";

// Function to fetch products from the API
async function fetchProducts() {
  try {
    const response = await fetch(baseUrl + "products/");
    if (!response.ok) {
      throw new Error("Failed to fetch products");
    }
    const products = await response.json();
    return products;
  } catch (error) {
    console.error("Error fetching products:", error);
    return [];
  }
}

// Cart functionality
let cart = [];

// Save cart to local storage
function saveCartToLocalStorage() {
  localStorage.setItem('cart', JSON.stringify(cart));
}

// Load cart from local storage
function loadCartFromLocalStorage() {
  const storedCart = localStorage.getItem('cart');
  if (storedCart) {
    cart = JSON.parse(storedCart);
  }
}

// Function to render products on the page
function renderProducts(products) {
  const productList = document.getElementById("product-list");
  productList.innerHTML = "";

  products.forEach((product) => {
    const productCard = document.createElement("div");
    productCard.classList.add("product-card");

    const productImage = document.createElement("img");
    productImage.src = product.image;
    productImage.alt = product.name;
    productCard.appendChild(productImage);

    const productName = document.createElement("h3");
    productName.textContent = product.name;
    productCard.appendChild(productName);

    const productPrice = document.createElement("p");
    productPrice.textContent = "$" + product.price.toFixed(2);
    productCard.appendChild(productPrice);

    const addToCartButton = document.createElement("button");
    addToCartButton.textContent = "Add to Cart";
    addToCartButton.addEventListener("click", () => {
      addToCart(product);
    });
    productCard.appendChild(addToCartButton);

    productList.appendChild(productCard);
  });
}

// Function to add item to cart
function addToCart(product) {
  const existingItem = cart.find((item) => item.id === product.id);
  if (existingItem) {
    existingItem.quantity++;
  } else {
    cart.push({ ...product, quantity: 1 });
  }
  saveCartToLocalStorage();
  updateCartUI();
}

// Function to remove item from cart
function removeFromCart(productId) {
  const index = cart.findIndex((item) => item.id === productId);
  if (index !== -1) {
    cart.splice(index, 1);
  }
  saveCartToLocalStorage();
  updateCartUI();
}

// Function to update cart UI
function updateCartUI() {
  const cartItemsList = document.getElementById("cart-items");
  const cartCount = document.getElementById("cart-count");
  if (!cartItemsList || !cartCount) return;

  cartItemsList.innerHTML = "";

  cart.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.name} x${item.quantity}`;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => {
      removeFromCart(item.id);
    });

    li.appendChild(removeBtn);
    cartItemsList.appendChild(li);
  });

  cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);
}

// Cart sidebar toggle
document.addEventListener("DOMContentLoaded", () => {
  const cartIcon = document.getElementById("cart-icon");
  const cartSidebar = document.getElementById("cart-sidebar");
  const overlay = document.getElementById("overlay");
  const closeCartBtn = document.getElementById("close-cart");

  function toggleCart() {
    cartSidebar.classList.toggle("open");
    if (cartSidebar.classList.contains("open")) {
      overlay.style.display = "block";
    } else {
      overlay.style.display = "none";
    }
  }

  cartIcon.addEventListener("click", (e) => {
    e.preventDefault();
    toggleCart();
  });

  closeCartBtn.addEventListener("click", () => {
    toggleCart();
  });

  overlay.addEventListener("click", () => {
    toggleCart();
  });

  // Load cart from local storage and update UI
  loadCartFromLocalStorage();
  updateCartUI();

  // Initial fetch and render of products
  fetchProducts().then(renderProducts);
});
