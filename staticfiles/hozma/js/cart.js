// Toggle cart visibility
function toggleCart() {
  const cartSidebar = document.getElementById('cartSidebar');
  const cartOverlay = document.getElementById('cartOverlay');
  const navbarCartIcon = document.getElementById('navbarCartIcon');

  const isOpen = cartSidebar.classList.toggle('open');
  cartOverlay.classList.toggle('open', isOpen);
  navbarCartIcon.setAttribute('aria-expanded', isOpen);

  if (isOpen) {
    window.lastFocusedElement = document.activeElement;
    cartSidebar.setAttribute('tabindex', '-1');
    cartSidebar.focus();
    document.body.style.overflow = 'hidden';
  } else {
    if (window.lastFocusedElement) {
      window.lastFocusedElement.focus();
    }
    document.body.style.overflow = '';
  }
}

// Close cart if clicked outside (on overlay)
document.getElementById('cartOverlay').addEventListener('click', function () {
  const cartSidebar = document.getElementById('cartSidebar');
  const cartOverlay = document.getElementById('cartOverlay');
  const navbarCartIcon = document.getElementById('navbarCartIcon');

  cartSidebar.classList.remove('open');
  cartOverlay.classList.remove('open');
  navbarCartIcon.setAttribute('aria-expanded', 'false');

  if (window.lastFocusedElement) {
    window.lastFocusedElement.focus();
  }
  document.body.style.overflow = '';
});

// Keyboard accessibility for cart icon
document.getElementById('navbarCartIcon').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    toggleCart();
  }
});



function updateQtyFromOutside(pno, newValue) {
  const input = document.getElementById(`qty-${pno}`);
  if (input) {
    input.value = newValue;
    console.log(`Quantity updated for ${pno} → ${newValue}`);
  } else {
    console.warn(`Input not found for pno: ${pno}`);
  }
}

function updateCartUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  document.getElementById('cartBadge').textContent = totalItems;
  document.getElementById('cartBadge1').textContent = totalItems;
  
  const cartContainer = document.getElementById('cartItemsContainer');
  
  if (cart.length === 0) {
    cartContainer.innerHTML = '<p class="text-muted text-center py-4">السلة فارغة</p>';
    document.getElementById('cartItemsCount').textContent = '0';
    document.getElementById('cartTotalAmount').textContent = '0.00 د٫ل';
    return;
  }
  
  let html = '';
  let totalAmount = 0;
  
  cart.forEach(item => {
    const itemTotal = item.price * item.quantity;
    totalAmount += itemTotal;
    
    html += `
      <div class="cart-item" id="cart-item-${item.pno}">
        <div class="d-flex align-items-center">
          <div class="cart-item-img me-2 bg-light d-flex align-items-center justify-content-center" style="width:50px; height:50px;">
            <div class="spinner-border text-primary" role="status" style="width:1.5rem; height:1.5rem;">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div>
            <h6 class="mb-0">${item.name}</h6>
            <small class="text-muted">| ${item.price.toFixed(2)} د.ل</small>
          </div>
        </div>
        <div class="d-flex align-items-center">
          <div class="quantity-control">
            <button class="btn btn-sm btn-outline-secondary quantity-btn" 
              onclick="decrementCartQuantity('${item.pno}')">-</button>
            <span class="mx-2">${item.quantity}</span>
            <button class="btn btn-sm btn-outline-secondary quantity-btn" 
              onclick="incrementCartQuantity('${item.pno}')">+</button>
          </div>
          <button class="btn btn-sm btn-outline-danger ms-2" 
            onclick="removeFromCart('${item.pno}')">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    `;
  });
  
  cartContainer.innerHTML = html;
  document.getElementById('cartItemsCount').textContent = cart.length;
  document.getElementById('cartTotalAmount').textContent = totalAmount.toFixed(2) + ' د.أ';

  // Fetch images asynchronously
  for (const item of cart) {
    fetchAndUpdateCartItemImage(item.pno);
  }
}

async function fetchAndUpdateCartItemImage(pno) {
  try {
    const response = await customFetch(`${baseUrl}/api/products/${pno}/get-images`);

    let imageUrl = '';
    if (response && Array.isArray(response) && response.length > 0) {
      imageUrl = `${baseUrl}${response[0].image_obj}`;
    }

    const cartItemDiv = document.getElementById(`cart-item-${pno}`);
    if (!cartItemDiv) {
      
      return;
    }

    const imgDiv = cartItemDiv.querySelector('.cart-item-img');
    if (!imgDiv) {
     
      return;
    }

    if (imageUrl) {
      imgDiv.innerHTML = `<img src="${imageUrl}" class="cart-item-img me-2" alt="Image for ${pno}" style="width:50px; height:50px; object-fit: contain; border-radius: 4px;">`;
    } else {
      imgDiv.innerHTML = `<div class="cart-item-img me-2 bg-light d-flex align-items-center justify-content-center" style="width:50px; height:50px;">
        <i class="bi bi-image text-muted"></i>
      </div>`;
     
    }

  } catch (error) {
    
  }
}




function addToCart(pno,fileid, itemno, name, price, image = '') {
  const existingItem = cart.find(item => item.pno === pno);
  
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      pno,
      fileid,
      itemno,
      name,
      price: parseFloat(price),
      quantity: quantity,
      image
    });
  }
  
  updateCartUI();
  updateCartPageUI(); 

}

function addToCartWithQuantity(pno, fileid, itemno, name, price, image = '', quantity = 1, stock) {
  quantity = parseInt(quantity);

  // Ensure quantity is a valid number and greater than 0
  if (isNaN(quantity) || quantity <= 0) {
    alert('الرجاء إدخال كمية صحيحة أكبر من صفر.');
    return;
  }

  // Check if the quantity exceeds stock
  if (quantity > stock) {
    alert(`الكمية المتوفرة هي ${stock}. يمكنك شراء الكمية المتوفرة فقط.`);
    return;
  }

  const existingItem = cart.find(item => item.pno === pno);

  // Update the quantity if item already exists in the cart
  if (existingItem) {
    existingItem.quantity = quantity;
    existingItem.stock = stock;

  } else {
    // Add new item to the cart if it doesn't exist
    cart.push({
      pno,
      fileid,
      itemno,
      name,
      price: parseFloat(price),
      quantity: quantity,
      image,
      stock
    });
  }

  updateCart();
  updateCartPageUI();
}


function removeFromCart(pno) {
  const index = cart.findIndex(item => item.pno === pno);
  if (index !== -1) {
    cart.splice(index, 1);
    updateQtyFromOutside(pno, 0);
    updateCart();
    updateCartPageUI(); 
  }
  
  
}

function clearCart() {
  if (confirm('هل أنت متأكد أنك تريد إفراغ سلة الطلبات؟')) {
    cart.length = 0;
    updateCart();
    updateCartPageUI(); 
    
    document.querySelectorAll('.quantity-input').forEach(input => {
      input.value = 0;
    });
  }
}

function updateQuantity(pno, quantity) {
  quantity = parseInt(quantity) || 0;
  
  if (quantity < 0) {
    quantity = 0;
    document.getElementById(`qty-${pno}`).value = 0;
  }
  
  const productRow = document.querySelector(`tr[data-pno="${pno}"]`);
  if (!productRow) return;
  
  const itemno = productRow.querySelector('td:first-child').textContent;
  const name = productRow.querySelector('td:nth-child(6)').textContent;
  const price = parseFloat(productRow.querySelector('td:nth-child(7)').textContent);
  const image = productRow.querySelector('img')?.src || '';
  
  const existingItem = cart.find(item => item.pno === pno);
  
  if (quantity === 0) {
    if (existingItem) {
      removeFromCart(pno);
    }
    return;
  }
  
  if (existingItem) {
    existingItem.quantity = quantity;
  } else {
    cart.push({
      pno,
      fileid,
      itemno,
      name,
      price: parseFloat(price),
      quantity: quantity,
      image
    });
  }
  
  updateCart();
  updateCartPageUI(); 
}

function incrementQuantity(pno) {
  const input = document.getElementById(`qty-${pno}`);
  input.value = parseInt(input.value) + 1;
  updateQuantity(pno, input.value);
}

function decrementQuantity(pno) {
  const input = document.getElementById(`qty-${pno}`);
  const newValue = Math.max(0, parseInt(input.value) - 1);
  input.value = newValue;
  updateQuantity(pno, newValue);
}
function incrementCartQuantity(pno) {
  const item = cart.find(item => item.pno === pno);
  if (item) {
    if (item.quantity >= item.stock) {
      alert(`الحد الأقصى المتاح هو ${item.stock}.`);
      return;
    }

    item.quantity += 1;
    updateQtyFromOutside(pno, item.quantity);  // This is enough

    updateCart();
    updateCartPageUI();
  }
}



function decrementCartQuantity(pno) {
  const item = cart.find(item => item.pno === pno);
  if (item) {
    item.quantity = Math.max(0, item.quantity - 1);

    if (item.quantity === 0) {
      removeFromCart(pno);
    } else {
      updateQtyFromOutside(pno, item.quantity);  // This is enough

      updateCart();
      updateCartPageUI();
    }
  }
}

async function submitOrder() {
  if (cart.length === 0) {
    alert('السلة فارغة. الرجاء إضافة منتجات قبل إرسال الطلب.');
    return;
  }
  
  const orderData = {
    items: cart.map(item => ({
      pno: item.pno,
      itemno: item.itemno,
      name: item.name,
      quantity: item.quantity,
      price: item.price
    })),
    total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
    notes: ''
  };
  
  try {
    const orderNumber = Math.floor(Math.random() * 1000000);
    document.getElementById('orderNumber').textContent = `ORD-${orderNumber}`;
    
    const modal = new bootstrap.Modal(document.getElementById('orderSuccessModal'));
    modal.show();
    
    clearCart();
  } catch (error) {
    console.error('Order submission failed:', error);
    alert('حدث خطأ أثناء إرسال الطلب. الرجاء المحاولة مرة أخرى.');
  }
}

function printCartItems() {
  const cartSidebar = document.getElementById('cartSidebar');
  const originalContents = document.body.innerHTML;
  const printContents = cartSidebar.innerHTML;

  document.body.innerHTML = `<div class="print-section">${printContents}</div>`;
  window.print();
  document.body.innerHTML = originalContents;
  location.reload();
}
function openCartPage() {
  window.location.href = "/hozma/hozmaCart"; // Update this to your actual cart page URL
}

  
function updateCartPageUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const cartContainer = document.getElementById('cartItems');
  
  if (cart.length === 0) {
      cartContainer.innerHTML = `
      <div class="auto-cart-empty">
          <i class="bi bi-cart-x auto-cart-empty-icon"></i>
          <h5>سلة التسوق فارغة</h5>
          <p class="text-muted">لم تقم بإضافة أي قطع غيار بعد</p>
          <a href="/products" class="btn btn-outline-primary mt-2">
          <i class="bi bi-arrow-left"></i> متابعة التسوق
          </a>
      </div>
      `;
      
      document.getElementById('summaryItemsCount').textContent = '0';
      document.getElementById('summarySubtotal').textContent = '0.00 د.أ';
      document.getElementById('summaryTotalAmount').textContent = '0.00 د.أ';
      return;
  }
  
  let html = '';
  let totalAmount = 0;

  cart.forEach(item => {
      const itemTotal = item.price * item.quantity;
      totalAmount += itemTotal;
      
      html += `
      <div class="auto-cart-item" id="cart-item-${item.pno}">
          <div class="d-flex align-items-center" style="min-width:0;">
              <div class="auto-cart-img cart-item-img me-2 d-flex align-items-center justify-content-center bg-light"
                   style="width:50px; height:50px;">
                  <i class="bi bi-image text-muted"></i>
              </div>
              <div class="auto-cart-info">
                  <h6 class="auto-part-title mb-1">${item.name}</h6>
                  <div class="auto-part-number">${item.pno}</div>
                  ${item.compatibility ? `<div class="part-compatibility"><i class="bi bi-check-circle"></i> متوافق مع ${item.compatibility}</div>` : ''}
                  <div class="auto-part-price">${item.price.toFixed(2)} د.ل للقطعة</div>
                  ${item.origin ? `<div class="auto-part-origin">${item.origin}</div>` : ''}
              </div>
          </div>
          <div class="d-flex align-items-center">
              <button class="auto-remove-btn" onclick="removeFromCart('${item.pno}')">
                  <i class="bi bi-trash"></i>
              </button>
              <div class="auto-qty-control">
                  <button class="btn btn-sm btn-outline-secondary auto-qty-btn" 
                          onclick="decrementCartQuantity('${item.pno}')">-</button>
                  <input type="text" class="auto-qty-value mx-2" id="qty-${item.pno}" 
                         value="${item.quantity}" readonly>
                  <button class="btn btn-sm btn-outline-secondary auto-qty-btn" 
                          onclick="incrementCartQuantity('${item.pno}')">+</button>
              </div>
          </div>
      </div>
      `;

      
  });

  cartContainer.innerHTML = html;
  document.getElementById('summaryItemsCount').textContent = totalItems;
  document.getElementById('summarySubtotal').textContent = totalAmount.toFixed(2) + ' د.ل ';
  document.getElementById('summaryTotalAmount').textContent = totalAmount.toFixed(2) + ' د.ل ';
  for (const item of cart) {
    fetchAndUpdateCartItemImage(item.pno);
  }
}


async function checkout() {
  let cart = JSON.parse(localStorage.getItem('product_cart')) || [];
  console.log("Loaded cart:", cart);

  if (cart.length === 0) {
    alert('سلة التسوق فارغة. الرجاء إضافة قطع غيار قبل الدفع.');
    return;
  }

  const clientId = JSON.parse(localStorage.getItem("session_data@user_id"));
  console.log("Client ID:", clientId);

  if (!clientId) {
    alert("رقم العميل غير موجود. الرجاء تسجيل الدخول.");
    return;
  }

  const data = {
    client: clientId,
    client_rate: "",
    client_category: "",
    client_limit: "",
    client_balance: "",
    invoice_date: "",
    invoice_status: "لم تحضر",
    payment_status: "اجل",
    mobile: true,
    for_who: ""
  };
  console.log("Invoice data to send:", data);

  let invoiceNo;

  try {
    const response = await customFetch('http://45.13.59.226/hozma/preorder/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include'
    });
  
    if (response) {
      const result = await response.json();
  
      if (response.ok && result.invoice_no) {
        console.log("Invoice record created successfully:", result);
        invoiceNo = result.invoice_no;
      } else {
        console.error("Failed to create invoice record:", result);
        alert(result.message || "فشل في إنشاء سجل الفاتورة.");
        return;
      }
    } else {
      console.error("No response from server.");
      alert("حدث خطأ في الاتصال بالخادم. الرجاء المحاولة لاحقًا.");
    }
  } catch (error) {
    console.error("Error while creating invoice record:", error);
    alert("حدث خطأ أثناء إنشاء سجل الفاتورة. الرجاء المحاولة لاحقًا.");
  }

  console.log("Invoice number:", invoiceNo);
  window.invoiceAutoId = invoiceNo;

  // Send each item one by one
  for (let item of cart) {
    const itemData = {
      pno: item.pno,
      fileid: item.fileid,
      invoice_id: invoiceNo,
      itemvalue: item.quantity,
      sellprice: parseFloat(item.price).toFixed(2)
    };

    console.log("Sending item data:", itemData);

    try {
      const itemResponse = await customFetch('http://45.13.59.226/hozma/api/full_Sell_invoice_create_item/', {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(itemData),
        credentials: 'include'
      });
    
      if (itemResponse) {
        const itemResult = await itemResponse.json();
        console.log("Server response for item:", itemResult);
    
        if (!itemResponse.ok) {
          console.error("Failed to add item:", itemResult);
          alert(`فشل في إضافة عنصر ${itemData.pno} إلى الفاتورة.`);
          return;
        }
      } else {
        console.error("No response from server.");
        alert("حدث خطأ في الاتصال بالخادم. الرجاء المحاولة لاحقًا.");
      }
    } catch (error) {
      console.error("Error while adding item:", error);
      alert(`حدث خطأ أثناء إضافة عنصر ${itemData.pno}. الرجاء المحاولة لاحقًا.`);
    }
  }  

  // Clear cart
  // Clear cart
localStorage.removeItem('product_cart');

// Store the invoice number for the invoice page to fetch
localStorage.setItem('current_invoice_no', invoiceNo);

// Redirect to the invoice page with the invoice number in the URL
window.location.href = `/hozma/invoice/${invoiceNo}`;


}


// Initialize cart on page load
document.addEventListener('DOMContentLoaded', function () {
  console.log("Page loaded. Initializing cart UI...");
  updateCartPageUI();
});

(() => {
  const cart = document.getElementById('floatingCartIcon');
  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  // Set starting position (right side)
  function setInitialPosition() {
    const x = window.innerWidth - cart.offsetWidth - 20;
    const y = window.innerHeight / 2 - cart.offsetHeight / 2;
    cart.style.left = `${x}px`;
    cart.style.top = `${y}px`;
    cart.style.right = 'unset'; // Remove 'right' so left/right movement works
  }

  setInitialPosition();

  function setPosition(x, y) {
    const maxX = window.innerWidth - cart.offsetWidth;
    const maxY = window.innerHeight - cart.offsetHeight;

    cart.style.left = `${Math.min(Math.max(0, x), maxX)}px`;
    cart.style.top = `${Math.min(Math.max(0, y), maxY)}px`;
  }

  // Mouse events
  cart.addEventListener('mousedown', (e) => {
    isDragging = true;
    offsetX = e.clientX - cart.getBoundingClientRect().left;
    offsetY = e.clientY - cart.getBoundingClientRect().top;
    cart.classList.add('dragging');
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    setPosition(e.clientX - offsetX, e.clientY - offsetY);
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    cart.classList.remove('dragging');
  });

  // Touch events
  cart.addEventListener('touchstart', (e) => {
    isDragging = true;
    const touch = e.touches[0];
    offsetX = touch.clientX - cart.getBoundingClientRect().left;
    offsetY = touch.clientY - cart.getBoundingClientRect().top;
  });

  document.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
    const touch = e.touches[0];
    setPosition(touch.clientX - offsetX, touch.clientY - offsetY);
  });

  document.addEventListener('touchend', () => {
    isDragging = false;
  });

  // Optional: re-center on window resize
  window.addEventListener('resize', setInitialPosition);
})();


// TEST - Simulate a cart update
function incrementAndAddToCart(pno, fileid, itemno, itemname, price, stock) {
  // First increment the quantity
  incrementQuantity(pno);

  // Then get the new value after increment
  const qtyInput = document.getElementById(`qty-${pno}`);
  const newQty = parseInt(qtyInput.value, 10) || 1;

  // Add to cart with the updated quantity
  addToCartWithQuantity(pno, fileid, itemno, itemname, price, '', newQty, stock);
}
function decrementAndAddToCart(pno, fileid, itemno, itemname, price, stock) {
  // First increment the quantity
  decrementQuantity(pno);

  // Then get the new value after increment
  const qtyInput = document.getElementById(`qty-${pno}`);
  const newQty = parseInt(qtyInput.value, 10) || 1;

  // Add to cart with the updated quantity
  addToCartWithQuantity(pno, fileid, itemno, itemname, price, '', newQty, stock);
}