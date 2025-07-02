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
function playNotificationSound() {
  const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
  audio.play().catch(e => console.warn('Audio play failed:', e));
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
document.getElementById('navbarCartIcon').addEventListener('keydown', function (e) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    toggleCart();
  }
});



function updateQtyFromOutside(pno, newValue) {
  const input = document.getElementById(`qty-${pno}`);
  if (input) {
    input.value = newValue;
    input.dispatchEvent(new Event('change')); // trigger change event if you listen for it
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
      <div class="cart-item d-flex justify-content-between align-items-center mb-3"
           id="cart-item-${item.pno}">

        <!-- 1) Image placeholder: we give it an <img> with a data-id and leave src blank for now -->
        <div class="d-flex align-items-center">
          <div class="cart-item-img me-2 bg-light d-flex align-items-center justify-content-center"
               style="width:50px; height:50px; position: relative;">
            <!-- Spinner (still show until image loads) -->
            <div class="spinner-border text-primary spinner-${item.pno}"
                 role="status"
                 style="width:1.5rem; height:1.5rem; position: absolute; top:50%; left:50%; transform: translate(-50%, -50%);">
              <span class="visually-hidden">Loading...</span>
            </div>
            <!-- Empty <img> that we will fill in asynchronously -->
            <img
              id="img-${item.pno}"
              alt="Image for ${item.pno}"
              style="width:50px; height:50px; object-fit: contain; border-radius:4px; display: none;"
            />
          </div>

          <div>
            <h6 class="mb-0">${item.name}</h6>
<small class="text-muted">| ${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} د.ل</small>
          </div>
        </div>

        <!-- 2) Quantity + remove buttons -->
        <div class="d-flex align-items-center">
          <div class="quantity-control d-flex align-items-center">
            <button class="btn btn-sm btn-outline-secondary quantity-btn"
                    onclick="decrementCartQuantity('${item.pno}')">
              -
            </button>
            <span class="mx-2">${item.quantity}</span>
            <button class="btn btn-sm btn-outline-secondary quantity-btn"
                    onclick="incrementCartQuantity('${item.pno}')">
              +
            </button>
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
  document.getElementById('cartTotalAmount').textContent = totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' د.ل';

  // 3) After inserting all items, trigger image fetches
  for (const item of cart) {
    fetchAndUpdateCartItemImage(item.pno);
  }
}


async function fetchAndUpdateCartItemImage(pno) {
  try {
    // 1) Fetch your list of images for this product
    const rawResponse = await fetch(`/hozma/api/products/${pno}/get-images`);
    if (!rawResponse.ok) {
      console.error(`Network error fetching images for ${pno}:`, rawResponse.status, rawResponse.statusText);
      return;
    }

    const data = await rawResponse.json();
    console.log("API JSON for", pno, "→", data);

    let imageUrl = '';
    if (Array.isArray(data) && data.length > 0 && data[0].image_obj) {
      // Build the full URL (make sure baseUrl is defined, with trailing slash if needed)
      imageUrl = `${data[0].image_obj}`;
    } else {
      console.warn(`No images returned for ${pno} (or 'image_obj' missing)`);
    }

    // 2) Grab the <img> we inserted by ID
    const imgEl = document.getElementById(`img-${pno}`);
    const spinnerEl = document.querySelector(`.spinner-${pno}`);

    if (!imgEl) {
      console.warn(`Could not find <img id="img-${pno}"> in DOM`);
      return;
    }
    if (!spinnerEl) {
      console.warn(`Could not find .spinner-${pno} (the loading spinner)`);
    }

    if (imageUrl) {
      // 3) Temporarily set src, and wait until it actually loads
      imgEl.src = imageUrl;

      // When the image successfully loads, hide the spinner and show the <img>
      imgEl.onload = () => {
        imgEl.style.display = 'block';
        if (spinnerEl) spinnerEl.style.display = 'none';
      };

      // If the image fails to load (404, CORS, etc.), show a “broken image” icon or placeholder:
      imgEl.onerror = () => {
        console.error(`Failed to load image for ${pno} at ${imageUrl}`);
        // Replace <img> with a fallback icon:
        imgEl.style.display = 'none';
        if (spinnerEl) spinnerEl.style.display = 'none';

        const parentDiv = imgEl.parentElement;
        if (parentDiv) {
          parentDiv.innerHTML = `
            <div class="d-flex align-items-center justify-content-center"
                 style="width:50px; height:50px;">
              <i class="bi bi-image text-muted"></i>
            </div>
          `;
        }
      };
    } else {
      // No image URL → immediately remove spinner and show placeholder
      if (imgEl) imgEl.style.display = 'none';
      if (spinnerEl) spinnerEl.style.display = 'none';

      const parentDiv = imgEl.parentElement;
      if (parentDiv) {
        parentDiv.innerHTML = `
          <div class="d-flex align-items-center justify-content-center"
               style="width:50px; height:50px;">
            <i class="bi bi-image text-muted"></i>
          </div>
        `;
      }
    }
  } catch (error) {
    console.error("Exception in fetchAndUpdateCartItemImage:", error);
  }
}





function addToCart(pno, fileid, itemno, name, price, image = '') {
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

function addToCartWithQuantity(pno, fileid, itemno, name, price, image = '', quantity = 1, stock,paired_pno = null,itemperbox = 1) {
  quantity = parseInt(quantity);

  // Ensure quantity is a valid number and greater than 0
  if (isNaN(quantity) || quantity <= 0) {
    Swal.fire({
      icon: 'error',
      title: 'خطأ',
      text: 'الرجاء إدخال كمية صحيحة أكبر من صفر.',
      confirmButtonText: 'حسناً'
    });
    return;
  }
  
  // Check if the quantity exceeds stock
  if (quantity > stock) {
    Swal.fire({
      icon: 'warning',
      title: 'تنبيه',
      text: `الكمية المتوفرة هي ${stock}. يمكنك شراء الكمية المتوفرة فقط.`,
      confirmButtonText: 'حسناً'
    });
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
      stock,
      paired_pno: paired_pno || null, // Store paired item PNO if exists
      itemperbox: itemperbox || 1 // Store item per box if exists
    });
  }

  updateCart();
  updateCartPageUI();
}

function removeFromCartRecursive(pno, visited = new Set()) {
  const normalizedPno = String(pno);
  if (visited.has(normalizedPno)) return; // prevent infinite loop
  visited.add(normalizedPno);

  const index = cart.findIndex(item => String(item.pno) === normalizedPno);
  if (index === -1) return;

  const mainItem = cart[index];
  cart.splice(index, 1);
  updateQtyFromOutside(normalizedPno, 0);

  if (mainItem.paired_pno) {
    removeFromCartRecursive(mainItem.paired_pno, visited);
  }

}

function removeFromCart(pno) {
  removeFromCartRecursive(pno);
  updateCart();
  updateCartPageUI();

}



function clearCart() {
  Swal.fire({
    title: 'هل أنت متأكد؟',
    text: 'هل تريد إفراغ سلة الطلبات؟',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'نعم، إفراغ السلة',
    cancelButtonText: 'إلغاء',
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      cart.length = 0;
      localStorage.removeItem('pair_add_alert_shown'); // Reset alert flag on removal
      localStorage.removeItem('box_add_alert_shown');  // Reset alert flag on removal

      updateCart();
      updateCartPageUI();

      document.querySelectorAll('.quantity-input').forEach(input => {
        input.value = 0;
      });

      Swal.fire({
        title: 'تم الإفراغ!',
        text: 'تم إفراغ سلة الطلبات بنجاح.',
        icon: 'success',
        timer: 2500,
        showConfirmButton: false
      });
    }
  });
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
  const item = cart.find(item => String(item.pno) === String(pno));
  if (!item) return;

  if (item.quantity >= item.stock) {
    alert(`الحد الأقصى المتاح هو ${item.stock}.`);
    return;
  }

  item.quantity += 1;
  updateQtyFromOutside(pno, item.quantity);

  // If item has a pair, increment it too
  if (item.paired_pno) {
    const pairedItem = cart.find(i => String(i.pno) === String(item.paired_pno));
    if (pairedItem) {
      pairedItem.quantity = item.quantity;
      updateQtyFromOutside(pairedItem.pno, pairedItem.quantity);
    }
  }

  updateCart();
  updateCartPageUI();
}



function incrementCartQuantity(pno) {
  const item = cart.find(item => String(item.pno) === String(pno));
  if (!item) return;

  const itemperbox = item.itemperbox || 1; // fallback to 1 if not a box type

  // Increment quantity by itemperbox units (e.g., 8 pieces)
  const newQty = item.quantity + itemperbox;

  if (newQty > item.stock) {
    alert(`الحد الأقصى المتاح هو ${item.stock} قطعة.`);
    return;
  }

  item.quantity = newQty;
  updateQtyFromOutside(pno, item.quantity);

  // If item has a pair, increment its quantity to match
  if (item.paired_pno) {
    const pairedItem = cart.find(i => String(i.pno) === String(item.paired_pno));
    if (pairedItem) {
      pairedItem.quantity = newQty;
      updateQtyFromOutside(pairedItem.pno, pairedItem.quantity);
    }
  }

  updateCart();
  updateCartPageUI();
}

function decrementCartQuantity(pno) {
  const item = cart.find(item => String(item.pno) === String(pno));
  if (!item) return;

  const itemperbox = item.itemperbox || 1; // fallback to 1 if not a box type

  // Decrement quantity by itemperbox units but don't go below 0
  let newQty = item.quantity - itemperbox;
  if (newQty < 0) newQty = 0;

  if (newQty === 0) {
    removeFromCart(pno); // will remove paired if exists
  } else {
    item.quantity = newQty;
    updateQtyFromOutside(pno, item.quantity);

    // Also update paired item quantity
    if (item.paired_pno) {
      const pairedItem = cart.find(i => String(i.pno) === String(item.paired_pno));
      if (pairedItem) {
        pairedItem.quantity = newQty;
        updateQtyFromOutside(pairedItem.pno, newQty);
      }
    }

    updateCart();
    updateCartPageUI();
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

// 1) Global map to store image URLs (or null if “no image”)
const imagesMap = {}; // { [pno]: "http://…/foo.jpg"  or  null }

// 2) Call this whenever the ‘cart’ array changes, or when the page first loads.
async function updateCartPageUI() {
  const cartContainer = document.getElementById('cartItems');
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (cart.length === 0) {
    cartContainer.innerHTML = `
      <div class="auto-cart-empty">
        <i class="bi bi-cart-x auto-cart-empty-icon"></i>
        <h5>سلة التسوق فارغة</h5>
        <p class="text-muted">لم تقم بإضافة أي قطع غيار بعد</p>
        <a href="/hozma/products" class="btn btn-outline-primary mt-2">
          <i class="bi bi-arrow-left"></i> متابعة التسوق
        </a>
      </div>
    `;

    document.getElementById('summaryItemsCount').textContent = (0).toLocaleString();
    document.getElementById('summarySubtotal').textContent = '0.00 د.ل';
    document.getElementById('summaryDelivery').textContent = '0.00 د.ل';
    document.getElementById('summaryDiscount').textContent = '0٪';
    document.getElementById('summaryTotalAmount').textContent = '0.00 د.ل';
    return;
  }

  let html = '';
  let subtotal = 0;

  // ✅ Sum subtotal
  cart.forEach(item => {
    subtotal += item.price * item.quantity;
  });

  // ✅ Fetch discount and delivery from API
  let discount = 0;
  let delivery = 0;
  try {
    const res = await fetch('/hozma/api/client-summary/', {
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      }
    });

    if (res.ok) {
      const data = await res.json();
      discount = parseFloat(data.discount) || 0;
      delivery = parseFloat(data.delivery) || 0;
    }
  } catch (err) {
    console.error('Failed to fetch client summary:', err);
  }

  const discountAmount = subtotal * discount;
  const totalAmount = subtotal + delivery - discountAmount;

  for (const item of cart) {
    const imgRecord = imagesMap[item.pno];
    let imageSection = '';

    if (imgRecord === undefined) {
      imageSection = `
        <div class="auto-cart-img cart-item-img me-2 d-flex align-items-center justify-content-center bg-light"
             style="width:50px; height:50px; position: relative;">
          <div class="spinner-border text-primary spinner-${item.pno}"
               role="status"
               style="width:1.5rem; height:1.5rem; position:absolute; top:50%; left:50%; transform:translate(-50%, -50%);">
            <span class="visually-hidden">Loading...</span>
          </div>
          <img
            id="img-${item.pno}"
            alt="الصورة لـ ${item.pno}"
            style="width:50px; height:50px; object-fit: contain; border-radius:4px; display: none;"
          />
        </div>
      `;
      fetchAndUpdateCartItemImage1(item.pno);
    } else if (imgRecord === null) {
      imageSection = `
        <div class="auto-cart-img cart-item-img me-2 d-flex align-items-center justify-content-center bg-light"
             style="width:50px; height:50px;">
          <i class="bi bi-image text-muted"></i>
        </div>
      `;
    } else {
      imageSection = `
        <div class="auto-cart-img cart-item-img me-2 d-flex align-items-center justify-content-center bg-light"
             style="width:50px; height:50px;">
          <img
            src="${imgRecord}"
            alt="الصورة لـ ${item.pno}"
            style="width:50px; height:50px; object-fit: contain; border-radius:4px; display: block;"
          />
        </div>
      `;
    }

    html += `
      <div class="auto-cart-item d-flex justify-content-between align-items-center mb-3"
           id="cart-item-${item.pno}">
        <div class="d-flex align-items-center" style="min-width: 0;">
          ${imageSection}
          <div class="auto-cart-info">
            <h6 class="auto-part-title mb-1">${item.name}</h6>
            <div class="auto-part-number">${item.pno}</div>
            ${item.compatibility ? `<div class="part-compatibility">
              <i class="bi bi-check-circle"></i> متوافق مع ${item.compatibility}
            </div>` : ''}
            <div class="auto-part-price">${item.price.toFixed(2)} د.ل للقطعة</div>
            ${item.origin ? `<div class="auto-part-origin">${item.origin}</div>` : ''}
          </div>
        </div>

        <div class="d-flex align-items-center">
          <button class="auto-remove-btn" onclick="removeFromCart('${item.pno}')">
            <i class="bi bi-trash"></i>
          </button>
          <div class="auto-qty-control d-flex align-items-center ms-3">
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
  }

  cartContainer.innerHTML = html;

  // Update summary fields
  document.getElementById('summaryItemsCount').textContent = totalItems.toLocaleString();
  document.getElementById('summarySubtotal').textContent = subtotal.toLocaleString(undefined, { minimumFractionDigits: 2 }) + ' د.ل';
  document.getElementById('summaryDelivery').textContent = delivery.toLocaleString(undefined, { minimumFractionDigits: 2 }) + ' د.ل';
  document.getElementById('summaryDiscount').textContent = (discount * 100).toFixed(0) + '٪';
  document.getElementById('summaryTotalAmount').textContent = totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2 }) + ' د.ل';
}



// 2) This function fetches once per pno and updates imagesMap[pno]. Then it re-renders:
async function fetchAndUpdateCartItemImage1(pno) {
  // If we already fetched once, do nothing:
  if (imagesMap[pno] !== undefined) {
    return;
  }

  try {
    const rawResponse = await fetch(`/hozma/api/products/${pno}/get-images`);
    if (!rawResponse.ok) {
      console.error(`Network error fetching images for ${pno}:`, rawResponse.status, rawResponse.statusText);
      imagesMap[pno] = null;
      updateCartPageUI();
      return;
    }

    const data = await rawResponse.json();
    console.log("API JSON for", pno, "→", data);

    if (Array.isArray(data) && data.length > 0 && data[0].image_obj) {
      // Build the full URL:
      const fullUrl = `${data[0].image_obj}`;
      imagesMap[pno] = fullUrl;
    } else {
      // No valid image returned
      imagesMap[pno] = null;
    }
  } catch (error) {
    console.error("Exception in fetchAndUpdateCartItemImage1:", error);
    imagesMap[pno] = null;
  }

  // Each time we get a response (either an image URL or null), re-render:
  updateCartPageUI();
}



async function checkout() {
  // Show loading alert
  Swal.fire({
    title: 'جاري المعالجة',
    html: 'الرجاء الانتظار أثناء معالجة طلبك...',
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading()
  });

  const cart = JSON.parse(localStorage.getItem('product_cart')) || [];

  if (cart.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'سلة التسوق فارغة',
      text: 'الرجاء إضافة قطع غيار قبل الدفع.',
      confirmButtonText: 'حسناً',
      confirmButtonColor: '#3085d6'
    });
    return;
  }

  const clientId = JSON.parse(localStorage.getItem("session_data@client_id"));

  if (!clientId) {
    Swal.fire({
      icon: 'error',
      title: 'غير مسجل دخول',
      text: 'الرجاء تسجيل الدخول للمتابعة.',
      confirmButtonText: 'حسناً',
      confirmButtonColor: '#3085d6'
    });
    return;
  }

  // Prepare data to match required JSON format
  const invoicePayload = {
    client: clientId,
    payment_status: "اجل",
    mobile: true,
    for_who: "",
    items: cart.map(item => ({
      pno: item.pno,
      fileid: item.fileid,
      itemvalue: item.quantity,
      sellprice: parseFloat(item.price).toFixed(2),
      available: item.stock || 0
    }))
  };

  try {
    const response = await customFetch('/hozma/api/preorder/create-with-item/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(invoicePayload),
      credentials: 'include'
    });

    const result = await response.json();

    if (!response.ok) {
      Swal.fire({
        icon: 'error',
        title: 'فشل في إتمام الطلب',
        html: result.error || result.message || 'حدث خطأ أثناء إنشاء الفاتورة. الرجاء المحاولة لاحقًا.',
        confirmButtonText: 'حسناً',
        confirmButtonColor: '#3085d6'
      });
      return;
    }
    // Success
    const invoiceNo = result.invoice_no;
    localStorage.removeItem('product_cart');
    localStorage.setItem('current_invoice_no', invoiceNo);

    Swal.fire({
      icon: 'success',
      title: 'تمت العملية بنجاح',
      html: `تم إنشاء الفاتورة رقم <strong>${invoiceNo}</strong> بنجاح.<br>سيتم توجيهك إلى صفحة الفاتورة الآن.`,
      showConfirmButton: true,
      confirmButtonText: 'حسناً',
      confirmButtonColor: '#3085d6',
      timer: 5000,
      timerProgressBar: true,
      willClose: () => {
        window.location.href = `/hozma/invoice/${invoiceNo}`;
      }
    }).then(() => {
      window.location.href = `/hozma/invoice/${invoiceNo}`;
    });

  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'خطأ غير متوقع',
      text: 'حدث خطأ أثناء معالجة الطلب. الرجاء المحاولة لاحقًا.',
      confirmButtonText: 'حسناً',
      confirmButtonColor: '#3085d6'
    });
  }
}


// Initialize cart on page load
document.addEventListener('DOMContentLoaded', function () {
  console.log("Page loaded. Initializing cart UI...");
  updateCartUI();
  updateCartPageUI(); // Update cart page UI as well
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
function incrementAndAddToCart(
  pno,
  fileid,
  itemno,
  itemname,
  price,
  stock,         // total pieces available
  quantityType,
  itemperbox,    // pieces per box
  pairedItemRaw
) {
  let pairedItem = null;
  if (pairedItemRaw && pairedItemRaw !== 'null') {
    try {
      pairedItem = JSON.parse(decodeURIComponent(pairedItemRaw));
    } catch (e) {
      console.error('خطأ في بيانات العنصر المزدوج:', e);
    }
  }

  const qtyInput = document.getElementById(`qty-${pno}`);
  const incrementBtn = document.getElementById(`increment-btn-${pno}`);
  let currentBoxes = parseInt(qtyInput.value, 10) || 0;

  let newBoxesQty = currentBoxes + 1;

  if (quantityType === 'box' && itemperbox) {
    // Calculate max boxes allowed based on total pieces stock and pieces per box
    const maxBoxes = Math.floor(stock / itemperbox);

    if (newBoxesQty > maxBoxes) {
      Swal.fire({
        icon: 'warning',
        title: 'تنبيه',
        text: 'وصلت إلى الحد الأقصى للصناديق المتاحة.',
        confirmButtonText: 'حسناً'
      });
      incrementBtn.disabled = true;
      return;
    }
    

    // Show alerts/toasts
    if (!localStorage.getItem('box_add_alert_shown')) {
      Swal.fire({
        title: 'صندوق مضاف!',
        text: `لقد أضفت صندوقًا إلى السلة. كل صندوق يحتوي على ${itemperbox} قطعة. لديك الآن ${newBoxesQty} صندوقًا في السلة. سيتم احتساب القطع حسب الصناديق وليس كل قطعة على حدة.`,
        icon: 'info',
        confirmButtonText: 'موافق',
        timer: 7000,
        timerProgressBar: true,
        didOpen: () => {
          playNotificationSound();
        }
      });
      localStorage.setItem('box_add_alert_shown', 'true');
    } else {
      Toastify({
        text: `📦 صندوق مضاف إلى السلة. المجموع الآن: ${newBoxesQty} صندوقًا.`,
        duration: 4000,
        close: false,
        gravity: "bottom",
        position: "center",
        backgroundColor: "#007bff",
        stopOnFocus: true,
      }).showToast();
    }

    // Update input to show boxes count
    qtyInput.value = newBoxesQty;

    // Calculate total pieces to add to cart
    const totalPieces = newBoxesQty * itemperbox;

    addToCartWithQuantity(
      pno,
      fileid,
      itemno,
      itemname,
      price,
      '',
      totalPieces,             // total pieces in cart for this item
      stock,                   // total pieces stock
      pairedItem ? String(pairedItem.pno) : null,
      itemperbox // pieces per box
    );

    incrementBtn.disabled = newBoxesQty >= maxBoxes;
    return;
  }

  // Pair and normal item handling below
  let maxAvailable;

  if (quantityType === 'pair' && pairedItem) {
    maxAvailable = Math.min(stock, pairedItem.showed);
    if (newBoxesQty > maxAvailable) {
      Swal.fire({
        icon: 'warning',
        title: 'تنبيه',
        text: 'وصلت إلى الحد الأقصى للكمية المتاحة للقطعتين المزدوجتين.',
        confirmButtonText: 'حسناً'
      });
      incrementBtn.disabled = true;
      return;
    }
  }
   else {
    maxAvailable = stock;
    if (newBoxesQty > maxAvailable) {
      Swal.fire({
        icon: 'warning',
        title: 'تنبيه',
        text: 'وصلت إلى الحد الأقصى للكمية المتاحة.',
        confirmButtonText: 'حسناً'
      });
      incrementBtn.disabled = true;
      return;
    }
  }    

  qtyInput.value = newBoxesQty;
  incrementBtn.disabled = newBoxesQty >= maxAvailable;

  addToCartWithQuantity(
    pno,
    fileid,
    itemno,
    itemname,
    price,
    '',
    newBoxesQty,
    stock,
    pairedItem ? String(pairedItem.pno) : null
  );

  if (quantityType === 'pair' && pairedItem) {
    if (!localStorage.getItem('pair_add_alert_shown')) {
      Swal.fire({
        title: 'منتج مزدوج!',
        text: 'هذا المنتج مرتبط بقطعة أخرى وستُضاف تلقائيًا إلى السلة.',
        icon: 'info',
        confirmButtonText: 'موافق',
        timer: 5000,
        timerProgressBar: false,
        didOpen: () => {
          playNotificationSound();
        }
      });
      localStorage.setItem('pair_add_alert_shown', 'true');
    }

    Toastify({
      text: "🔗 منتج مزدوج! العنصر الآخر تم إضافته تلقائيًا إلى السلة.",
      duration: 4000,
      close: false,
      gravity: "bottom",
      position: "center",
      backgroundColor: "#ff6d00",
      stopOnFocus: true,
    }).showToast();

    addToCartWithQuantity(
      pairedItem.pno,
      pairedItem.fileid,
      pairedItem.itemno,
      pairedItem.itemname,
      parseFloat(pairedItem.buyprice),
      '',
      newBoxesQty,
      pairedItem.showed,
      String(pno)
    );
  }
}


function decrementAndAddToCart(
  pno,
  fileid,
  itemno,
  itemname,
  price,
  stock,
  quantityType,
  itemperbox,
  pairedItemRaw
) {
  // Parse paired item JSON if provided
  let pairedItem = null;
  if (pairedItemRaw && pairedItemRaw !== 'null') {
    try {
      pairedItem = JSON.parse(decodeURIComponent(pairedItemRaw));
    } catch (e) {
      console.error('خطأ في قراءة بيانات العنصر المزدوج:', e);
    }
  }

  const qtyInput = document.getElementById(`qty-${pno}`);
  const incrementBtn = document.getElementById(`increment-btn-${pno}`);

  let currentQty = parseInt(qtyInput.value, 10) || 0;

  // Only stop if quantity is already 0 (can't go negative)
  if (currentQty === 0) return;

  let newQty = currentQty - 1;

  if (quantityType === 'box' && itemperbox) {
    // stock = number of boxes available
    const maxBoxes = stock;

    if (newQty < 0) newQty = 0;

    // Calculate total pieces for cart
    const totalItems = newQty * itemperbox;

    qtyInput.value = newQty;

    // Re-enable increment button if below max boxes
    incrementBtn.disabled = newQty >= maxBoxes ? true : false;

    if (newQty === 0) {
      // Optionally remove from cart if zero
      addToCartWithQuantity(pno, fileid, itemno, itemname, price, '', 0, maxBoxes * itemperbox);
    } else {
      addToCartWithQuantity(
        pno,
        fileid,
        itemno,
        itemname,
        price,
        '',
        totalItems,
        maxBoxes * itemperbox,
        pairedItem ? String(pairedItem.pno) : null
      );
    }
    return; // done for box type
  }

  // For pair and normal types
  let maxAvailable;

  if (quantityType === 'pair' && pairedItem) {
    maxAvailable = Math.min(stock, pairedItem.showed);
  } else {
    maxAvailable = stock;
  }

  qtyInput.value = newQty;

  // Re-enable increment button if qty less than max
  incrementBtn.disabled = newQty >= maxAvailable;

  // If quantity zero, consider removing or setting zero quantity in cart
  if (newQty === 0) {
    addToCartWithQuantity(pno, fileid, itemno, itemname, price, '', 0, stock);
  } else {
    addToCartWithQuantity(pno, fileid, itemno, itemname, price, '', newQty, stock, pairedItem ? String(pairedItem.pno) : null);
  }

  // Also update paired item quantity if applicable
  if (quantityType === 'pair' && pairedItem) {
    if (newQty === 0) {
      addToCartWithQuantity(pairedItem.pno, pairedItem.fileid, pairedItem.itemno, pairedItem.itemname, parseFloat(pairedItem.buyprice), '', 0, pairedItem.showed);
    } else {
      addToCartWithQuantity(
        pairedItem.pno,
        pairedItem.fileid,
        pairedItem.itemno,
        pairedItem.itemname,
        parseFloat(pairedItem.buyprice),
        '',
        newQty,
        pairedItem.showed,
        String(pno)
      );
    }
  }
}

function updateCartBadge(count) {
  const cartBadge = document.getElementById('cartBadge');

  if (count > 0) {
    cartBadge.textContent = count;
    cartBadge.classList.remove('d-none');
  } else {
    cartBadge.classList.add('d-none');
  }
}

// Example: Call this function whenever the cart count changes
updateCartBadge(0);     // Hides the badge
updateCartBadge(5);     // Shows the badge with "5"
updateCartBadge(9999);  // Shows the badge with "9999"
