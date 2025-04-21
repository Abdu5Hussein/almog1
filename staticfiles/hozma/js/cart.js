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


  
  
  function updateCartUI() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartBadge').textContent = totalItems;
    
    const cartContainer = document.getElementById('cartItemsContainer');
    
    if (cart.length === 0) {
      cartContainer.innerHTML = '<p class="text-muted text-center py-4">السلة فارغة</p>';
      document.getElementById('cartItemsCount').textContent = '0';
      document.getElementById('cartTotalAmount').textContent = '0.00 د.أ';
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
              <small class="text-muted">${item.itemno} | ${item.price.toFixed(2)} د.أ</small>
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
      console.log(`Fetching image for product number: ${pno}`);
  
      const response = await fetchWithAuth(`${baseUrl}/api/products/${pno}/get-images`);
      console.log('Raw response from API:', response);
  
      let imageUrl = '';
      if (response && Array.isArray(response) && response.length > 0) {
        imageUrl = `${baseUrl}${response[0].image_obj}`;
        console.log('Image URL constructed:', imageUrl);
      } else {
        console.log('No images found in response');
      }
  
      const cartItemDiv = document.getElementById(`cart-item-${pno}`);
      if (!cartItemDiv) {
        console.warn(`No cart item found for pno: ${pno}`);
        return;
      }
  
      const imgDiv = cartItemDiv.querySelector('.cart-item-img');
      if (!imgDiv) {
        console.warn(`No image div found inside cart item for pno: ${pno}`);
        return;
      }
  
      if (imageUrl) {
        imgDiv.innerHTML = `<img src="${imageUrl}" class="cart-item-img me-2" alt="Image for ${pno}" style="width:50px; height:50px; object-fit: contain; border-radius: 4px;">`;
        console.log(`Image tag updated for pno: ${pno}`);
      } else {
        imgDiv.innerHTML = `<div class="cart-item-img me-2 bg-light d-flex align-items-center justify-content-center" style="width:50px; height:50px;">
          <i class="bi bi-image text-muted"></i>
        </div>`;
        console.log(`Placeholder image shown for pno: ${pno}`);
      }
  
    } catch (error) {
      console.error('Error fetching cart item image:', error);
    }
  }
  
  
  
  function addToCart(pno, itemno, name, price, image = '') {
    const existingItem = cart.find(item => item.pno === pno);
    
    if (existingItem) {
      existingItem.quantity += 1;
    } else {
      cart.push({
        pno,
        itemno,
        name,
        price: parseFloat(price),
        quantity: 1,
        image
      });
    }
    
    updateCartUI();
    updateCartPageUI(); 

  }
  
  function addToCartWithQuantity(pno, itemno, name, price, image = '', quantity = 1) {
    quantity = parseInt(quantity);
    if (isNaN(quantity) || quantity <= 0) {
      alert('الرجاء إدخال كمية صحيحة أكبر من صفر.');
      return;
    }
    
    const existingItem = cart.find(item => item.pno === pno);
    
    if (existingItem) {
      existingItem.quantity = quantity;
    } else {
      cart.push({
        pno,
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
  
  function removeFromCart(pno) {
    const index = cart.findIndex(item => item.pno === pno);
    if (index !== -1) {
      cart.splice(index, 1);
      updateCart();
      updateCartPageUI(); 
    }
    
    const qtyInput = document.getElementById(`qty-${pno}`);
    if (qtyInput) {
      qtyInput.value = 0;
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
        itemno,
        name,
        price,
        quantity,
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
      item.quantity += 1;
      updateCart();
      updateCartPageUI(); 
      
      const qtyInput = document.getElementById(`qty-${pno}`);
      if (qtyInput) {
        qtyInput.value = item.quantity;
      }
    }
  }
  
  function decrementCartQuantity(pno) {
    const item = cart.find(item => item.pno === pno);
    if (item) {
      item.quantity = Math.max(0, item.quantity - 1);
      
      if (item.quantity === 0) {
        removeFromCart(pno);
      } else {
        updateCart();
        updateCartPageUI(); 
        
        const qtyInput = document.getElementById(`qty-${pno}`);
        if (qtyInput) {
          qtyInput.value = item.quantity;
        }
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
    window.location.href = "/hozmaCart"; // Update this to your actual cart page URL
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


function checkout() {
    if (cart.length === 0) {
        alert('سلة التسوق فارغة. الرجاء إضافة قطع غيار قبل الدفع.');
        return;
    }
    // Implement your checkout logic here
    window.location.href = '/checkout';
}

// Initialize cart on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartPageUI();

});