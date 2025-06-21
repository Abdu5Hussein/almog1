let currentPage = 1;
let lastPage = 1;
let isLoading = false;
let currentFilters = {};
let itemsPerPage = 12;
let datl = {};
let pageCache = {}; 
let prefetchQueue = []; 
let isNavigating = false; // Prevents rapid clicks
let maxPrefetchedPage = 0; // { pageNum: { data, last_page, total_rows } }
let loadingPages = new Set(); // Pages currently being fetched
let lastVisiblePage = 1; // Last page the user actually viewed
   // highest page we’ve ever prefetched
// *** simple in-memory cache ***

// Main function to fetch filtered data
async function fetchFilteredData(page = 1) {
    // Serve from cache if present
    if (pageCache[page]) {
        return Promise.resolve(pageCache[page]);
    }

    console.debug("Fetching filtered data for page:", page);

    const filters = {
        pno: currentFilters.pno || '',
        item_type: currentFilters.item_type || '',
        oem_combined: currentFilters.oem_combined || '',
        itemname: currentFilters.itemname || '',
        companyproduct: currentFilters.companyproduct || '',
        availability: currentFilters.availability || '',
        category: currentFilters.category || '',
        discount: currentFilters.discount || '',
        
        page: page,
        size: itemsPerPage,
    };

    console.debug("Full filters being sent:", JSON.stringify(filters, null, 2));

    try {
        const response = await customFetch(`/hozma/api/producuts/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });

        if (!response) {
            throw new Error("Empty response from server");
        }

        const data = await response.json();

        const formatted = {
            data: data?.data || [],
            last_page: data?.last_page || 1,
            total_rows: data?.total_rows || 0
        };

        // Cache the result
        pageCache[page] = formatted;
        return formatted;

    } catch (error) {
        console.error("API Error:", error);
        return {
            data: [],
            last_page: 1,
            total_rows: 0
        };
    }
}

// Prefetch next pages (up to four pages ahead)
function prefetchNextPages() {
  // Don’t prefetch beyond known limits
  if (!lastPage || lastVisiblePage >= lastPage) return;

  // Prefetch 3 pages ahead (adjust based on your needs)
  const pagesToPrefetch = [lastVisiblePage + 1, lastVisiblePage + 2, lastVisiblePage + 3];

  pagesToPrefetch.forEach((page) => {
      if (page <= lastPage && !pageCache[page] && !loadingPages.has(page)) {
          loadingPages.add(page);
          fetchFilteredData(page)
              .then((data) => {
                  pageCache[page] = data;
              })
              .finally(() => loadingPages.delete(page));
      }
  });
}
// Display items in the table
async function displayItems(items) {
  const productList = document.getElementById('productList');
  productList.innerHTML = '';

  if (items.length === 0) {
    document.getElementById('noResults').style.display = 'block';
    document.getElementById('loading-spinner').style.display = 'none';
    return;
  }

  document.getElementById('noResults').style.display = 'none';

  for (const item of items) {
    const row = document.createElement('tr');

    const stock = parseInt(item.showed) || 0;
    const cartItem = cart.find(ci => ci.pno === item.pno);
    const cartQuantity = cartItem ? cartItem.quantity : 0;

    /* Price/discount logic */
    const discount = item.discount ? parseFloat(item.discount) : 0;
    const finalPrice = parseFloat(item.buyprice || 0);
    const originalPrice = discount ? finalPrice / (1 - discount) : finalPrice;

    const priceCellContent = discount
      ? `
        <span class="text-decoration-line-through text-muted me-1 d-none d-md-inline">
          ${originalPrice.toFixed(2)} د.ل
        </span>
        <span class="fw-bold text-danger">
          ${finalPrice.toFixed(2)} د.ل
        </span>
        <span class="badge bg-danger ms-1 d-none d-md-inline-block">
          خصم ${(discount * 100).toFixed(0)}%
        </span>`
      : `${finalPrice.toFixed(2)} د.ل`;

    row.innerHTML = `
      <td class="clickable-cell d-none d-md-table-cell" data-pno="${item.pno}" data-label="رقم القطعة">${item.pno ?? '-'}</td>
<td data-label="اسم القطعة">
${item.itemname ?? '-'}
<i class="fas fa-circle-question text-primary ms-2 faq-icon"
   style="cursor: pointer;"
   title="عرض التفاصيل"
   onclick="showItemDetail('${item.pno}')"></i>
</td>
      <td data-label="الشركة">${item.companyproduct ?? '-'}</td>
      <td class="d-none d-md-table-cell" data-label="المخزون">
        ${stock > 10
          ? `<span class="badge bg-success">متوفر</span>`
          : stock > 0
            ? `<span class="badge bg-warning text-dark">كمية محدودة</span>`
            : `<span class="badge bg-danger">غير متوفر</span>`}
      </td>
      <td data-label="السعر">${priceCellContent}</td>
    
      <td data-label="الكمية">
<div class="quantity-control">
  <button class="btn btn-sm btn-outline-secondary quantity-btn"
          onclick="decrementAndAddToCart('${item.pno}', '${item.fileid}', '${item.itemno}', '${item.itemname}', ${finalPrice.toFixed(2)}, ${item.showed})">-</button>
  <input type="number" class="form-control form-control-sm quantity-input"
         id="qty-${item.pno}" value="${cartQuantity}" min="0" readonly>
<button class="btn btn-sm btn-outline-secondary quantity-btn"
        id="increment-btn-${item.pno}"
        onclick="incrementAndAddToCart('${item.pno}', '${item.fileid}', '${item.itemno}', '${item.itemname}', ${finalPrice.toFixed(2)}, ${item.showed})"
        ${cartQuantity >= item.showed ? 'disabled' : ''}>
  +
</button>
</div>
</td>

    `;

    /* Allow pno & name cells to open the image dialog */
    row.querySelectorAll('.clickable-cell').forEach(cell => {
      cell.style.cursor = 'pointer';
      cell.addEventListener('click', e => {
        if (!e.target.classList.contains('quantity-btn') &&
            !e.target.classList.contains('quantity-input')) {
              showItemDetail(item.pno);
        }
      });
    });

    productList.appendChild(row);
  }
}

  
  
  
let currentImageModal = null;
/**
 * عرض تفاصيل قطعة + صورها داخل الـ Modal
 * @param {string|number} pno  رقم القطعة
 */
async function showItemDetail(pno) {
    console.debug("Fetching item detail for PNO:", pno);
  
    /* عناصر الـ Modal */
    const modalEl   = document.getElementById("imageModal");
    const modalBody = modalEl.querySelector(".modal-body");
  
    /* تخلّص من نسخة Modal قديمة إن وُجِدت */
    const oldModal = bootstrap.Modal.getInstance(modalEl);
    if (oldModal) {
      oldModal.hide();
      modalEl.addEventListener(
        "hidden.bs.modal",
        () => oldModal.dispose(),
        { once: true }
      );
    }
  
    /* Spinner أثناء التحميل */
    modalBody.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border" role="status"></div>
        <p class="mt-3">جارٍ تحميل بيانات المنتج…</p>
      </div>
    `;
  
    /* أنشئ Modal جديدًا وأظهره */
    const modal = new bootstrap.Modal(modalEl, {
      backdrop: "static",
      keyboard: true,
      focus: true,
    });
    modal.show();
  
    try {
      /* اجلب التفاصيل والصور في وقتٍ واحد */
      const [detailRes, imgRes] = await Promise.all([
        customFetch(`${baseUrl}/hozma/api/item/${pno}/details/`),              // تفاصيل
        customFetch(`${baseUrl}/api/products/${pno}/get-images`),   // صور
      ]);
  
      const item   = await detailRes.json();  // يُتوقَّع أن يُعيد JSON بالمفاتيح الموجودة في دالة Django
      const images = await imgRes.json();     // مصفوفة صور
  
      /* HTML مكتمل */
      modalBody.innerHTML = buildItemHtml(item, images);
    } catch (err) {
      console.error("Error fetching item detail:", err);
      modalBody.innerHTML = `
        <div class="text-center py-5">
          <i class="bi bi-exclamation-triangle text-danger" style="font-size: 3rem;"></i>
          <p class="mt-3">حدث خطأ أثناء تحميل بيانات المنتج</p>
        </div>
      `;
    }
  }
  
  /* توليد الـ HTML من البيانات */
  function buildItemHtml(item, images) {
    const firstImgTag =
    images?.length
      ? `<a href="${baseUrl}${images[0].image_obj}" target="_blank">
           <img src="${baseUrl}${images[0].image_obj}"
                class="img-fluid rounded product-image"
                alt="الصورة الرئيسية للقطعة">
         </a>`
      : `<div class="product-image-placeholder py-5 text-center bg-light rounded">
           <i class="fas fa-car-parts fa-4x opacity-50"></i>
         </div>`;

  const otherImgs =
    images?.slice(1).map(imgObj => `
      <div class="mb-3">
        <img src="${baseUrl}${imgObj.image_obj}"
             class="img-fluid rounded mb-2 product-image"
             alt="صورة إضافية للقطعة">
        <div class="text-center">
          <a href="${baseUrl}${imgObj.image_obj}" target="_blank"
             class="btn btn-sm btn-outline-primary">
            <i class="bi bi-arrows-angle-expand"></i> فتح الصورة في نافذة جديدة
          </a>
        </div>
      </div>
    `).join("") || "";
  
    return `
  <div class="container">
    <div class="row">
      <!-- الصور + التفاصيل -->
      <div class="col-lg-8">
        <div class="product-container">
<div class="product-image-wrapper mb-4 text-center">
  ${firstImgTag}
</div>



  
          <div class="specs-card mt-4">
            <h3><i class="fas fa-file-alt technical-icon"></i> وصف المنتج</h3>
            <p>${item.memo ? item.memo : '<span class="text-muted">لا يوجد وصف إضافي متاح.</span>'}</p>
          </div>
  
          <div class="specs-card mt-4">
            <h3><i class="fas fa-cogs technical-icon"></i> المواصفات الفنية</h3>
            ${buildSpecsTable(item.json_description)}
          </div>
  
          <!-- صور إضافية (إن وُجِدت) -->
          ${otherImgs}
        </div>
      </div>
  
      <!-- السعر والطلب -->
      <div class="col-lg-4">
      <div class="detail-card">
  <h3><i class="fas fa-info-circle technical-icon"></i> معلومات أساسية</h3>
  <div class="detail-item"><span class="detail-label">رقم القطعة:</span><span class="detail-value">${item.pno}</span></div>
  <div class="detail-item"><span class="detail-label">الشركة المصنعة:</span><span class="detail-value">${item.companyproduct}</span></div>
  <div class="detail-item">
    <span class="detail-label">تصنيف السيارة:</span>
    <ul class="detail-value list-unstyled mb-0">
      <li><strong>النوع:</strong> ${item.itemmain}</li>
      <li><strong>الموديل:</strong> ${item.itemsubmain}</li>
      <li><strong>سنة الصنع:</strong> ${item.itemthird}</li>
    </ul>
  </div>
  <div class="detail-item"><span class="detail-label">البلد المنتج:</span><span class="detail-value">${item.itemsize}</span></div>
  <div class="detail-item"><span class="detail-label">رقم المحرك:</span><span class="detail-value">${item.engine_no}</span></div>
</div>  
  
        <div class="specs-card mt-4">
          <h3><i class="fas fa-headset technical-icon"></i> هل تحتاج مساعدة؟</h3>
          <p>متخصصو قطع الغيار لدينا مستعدون لمساعدتك في أي استفسار حول هذا المنتج.</p>
          <button class="btn btn-outline-primary w-100" onclick="contactSupport()">
            <i class="fas fa-phone-alt me-2"></i> اتصل بالدعم
          </button>
        </div>
      </div>
    </div>
  </div>`;
  }
  
  /* جدول المواصفات الفنية */
  function buildSpecsTable(jsonDesc) {
    if (!jsonDesc || Object.keys(jsonDesc).length === 0) {
      return '<p class="text-muted mb-0">لا توجد مواصفات فنية متاحة.</p>';
    }
    return `
      <table class="table table-bordered table-striped mt-3">
        <thead><tr><th>العنصر</th><th>الوصف</th></tr></thead>
        <tbody>
          ${Object.entries(jsonDesc)
            .map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`)
            .join("")}
        </tbody>
      </table>`;
  }
  function contactSupport() {
    window.location.href = "tel:+218914262604";
  }
  /* مساعد لتعديل كمية الطلب */
  function changeQty(delta) {
    const qtyInput = document.getElementById("quantity");
    const newVal = Math.max(1, parseInt(qtyInput.value || 1, 10) + delta);
    qtyInput.value = newVal;
  }
  
  
function changeItemMain(value) {
    // Update the hidden input
    document.getElementById('category').value = value;
    
    // Remove active class from all icons
    document.querySelectorAll('.category-icon').forEach(icon => {
        icon.classList.toggle('active', icon.dataset.value === value);
    });
    
    // Move the highlight to the selected icon
    const selectedIcon = document.querySelector(`.category-icon[data-value="${value}"]`);
    if (selectedIcon) {
        moveHighlight(selectedIcon);
    }

    applyFilters();
}

// New helper function for smooth highlight movement
function moveHighlight(selectedElement) {
    const highlight = document.querySelector('.brand-highlight');
    if (!highlight) return;
    
    const elementRect = selectedElement.getBoundingClientRect();
    const containerRect = selectedElement.parentElement.getBoundingClientRect();
    
    highlight.style.width = `${elementRect.width}px`;
    highlight.style.height = `${elementRect.height}px`;
    highlight.style.left = `${elementRect.left - containerRect.left}px`;
    highlight.style.top = `${elementRect.top - containerRect.top}px`;
}

// Initialize highlight on page load
document.addEventListener('DOMContentLoaded', function() {
    // Create highlight element if it doesn't exist
    if (!document.querySelector('.brand-highlight')) {
        const highlight = document.createElement('div');
        highlight.className = 'brand-highlight';
        document.querySelector('.brand-selector').prepend(highlight);
    }
    
    // Position highlight on initially active icon
    const activeIcon = document.querySelector('.category-icon.active');
    if (activeIcon) {
        moveHighlight(activeIcon);
    }
});

// Apply filters from input fields
function applyFilters() {
    console.debug("Applying filters...");

    const availabilityRaw = document.getElementById('availabilityFilter').value;
    let availability = '';
    let discount = '';

    if (availabilityRaw.includes(':')) {
        const [key, value] = availabilityRaw.split(':');
        if (key === 'availability') {
            availability = value;
        } else if (key === 'discount') {
            discount = value;
        }
    }

    currentFilters = {
        pno: document.getElementById('pnoFilter').value.trim(),
        item_type: document.getElementById('companynoFilter').value.trim(),
        oem_combined: document.getElementById('oemFilter').value.trim(),
        itemname: document.getElementById('itemnameFilter').value.trim(),
        companyproduct: document.getElementById('companyproductFilter').value.trim(),
        availability: availability,
        discount: discount,
        category: document.getElementById('category') ? document.getElementById('category').value : '',
    };

    console.debug("Current filters:", currentFilters);

    currentPage = 1;
    document.getElementById('pageInput').value = 1;
    document.getElementById('productList').innerHTML = "";
    document.getElementById('loading-spinner').style.display = 'block';

    pageCache = {}; // Clear cache
    loadMoreItems();
}


// Reset all filters
function resetFilters() {
    console.debug("Resetting filters...");

    document.getElementById('pnoFilter').value = '';
    document.getElementById('companynoFilter').value = '';
    document.getElementById('oemFilter').value = '';
    document.getElementById('itemnameFilter').value = '';
    document.getElementById('companyproductFilter').value = '';
    document.getElementById('availabilityFilter').value = '';

    // Reset category
    document.getElementById('category').value = '';
    document.querySelectorAll('.category-icon').forEach(icon => {
        icon.classList.remove('active');
    });

    applyFilters();
}

// Load more items with pagination
async function loadMoreItems() {
  if (isLoading) return;
  isLoading = true;

  const { data, last_page, total_rows } = await fetchFilteredData(currentPage);
  lastPage = last_page || 1;

  // Cache the result
  pageCache[currentPage] = { data, last_page, total_rows };

  await displayItems(data);
  updatePaginationInfo(total_rows);

  isLoading = false;
  document.getElementById('loading-spinner').style.display = 'none';
}

// Update pagination information
function updatePaginationInfo(total_rows) {
    console.debug("Total items:", total_rows, "Current page:", currentPage, "Last page:", lastPage);
    document.getElementById('pageInfo').textContent =
        `الصفحة ${currentPage} من ${lastPage} | إجمالي العناصر: ${total_rows}`;
    document.getElementById('pageInfo1').textContent =
        `الصفحة ${currentPage} من ${lastPage} | إجمالي العناصر: ${total_rows}`;
}

// Change page based on input
function changePage() {
    const pageInput = document.getElementById('pageInput');
    const newPage = parseInt(pageInput.value, 10);

    console.debug("Changing page to:", newPage);

    if (newPage > 0 && newPage <= lastPage && newPage !== currentPage) {
        currentPage = newPage;
        document.getElementById('productList').innerHTML = "";
        document.getElementById('loading-spinner').style.display = 'block';
        
        // Scroll to top before loading new items
        const tableContainer = document.querySelector('.scroll-table-container');
        if (tableContainer) {
            tableContainer.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        loadMoreItems();
    } else {
        pageInput.value = currentPage;
    }
}

function prevPage() {
    if (currentPage > 1) {
        document.getElementById('pageInput').value = currentPage - 1;
        changePage();
    }
}
async function nextPage() {
  if (currentPage >= lastPage) return;

  const nextPageNum = currentPage + 1;

  // If cached, render instantly and scroll up
  if (pageCache[nextPageNum]) {
      currentPage = nextPageNum;
      displayItems(pageCache[nextPageNum].data);
      updatePaginationInfo(pageCache[nextPageNum].total_rows);
      smoothScrollToTop(); // 👈 Added back (but smooth)
  } 
  // If not cached, load with spinner, then scroll
  else {
      document.getElementById('loading-spinner').style.display = 'block';
      await loadMoreItems();
      smoothScrollToTop(); // 👈 Scroll after loading
  }

  lastVisiblePage = currentPage;
  prefetchNextPages();
}
function smoothScrollToTop() {
  const tableContainer = document.querySelector('.scroll-table-container');
  if (tableContainer) {
      tableContainer.scrollTo({
          top: 0,
          behavior: 'smooth' // Smooth animation
      });
  }
}

// Change items per page
function changeItemsPerPage() {
    itemsPerPage = parseInt(document.getElementById('itemsPerPage').value);
    console.debug("Changing items per page to:", itemsPerPage);

    currentPage = 1;
    document.getElementById('pageInput').value = 1;
    document.getElementById('productList').innerHTML = "";
    document.getElementById('loading-spinner').style.display = 'block';

    // Clear cache on size change
    pageCache = {};

    loadMoreItems();
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners for filter inputs
    document.getElementById('pnoFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.getElementById('companynoFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.getElementById('oemFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.getElementById('itemnameFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.getElementById('companyproductFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.getElementById('availabilityFilter').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') applyFilters();
    });
    document.querySelectorAll('.category-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            changeItemMain(this.dataset.value);
        });
    });





    document.getElementById('pageInput').addEventListener('change', changePage);
    document.getElementById('itemsPerPage').addEventListener('change', changeItemsPerPage);

    // Initial load
    applyFilters();
        setTimeout(() => prefetchNextPages(), 500); // Prefetch page 2 after a short delay

});

window.onload = function () {
    // Call applyFilters on page load to load items with or without filters
    applyFilters();
};

// Additional event bindings (duplicate entries kept as in original)

document.getElementById('pageInput').addEventListener('change', changePage);
document.getElementById('itemsPerPage').addEventListener('change', changeItemsPerPage);
applyFilters();

// Cleanup any existing modals when page loads
document.addEventListener('DOMContentLoaded', function () {
    // Remove any existing backdrops
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());

    // Remove modal-open class from body
    document.body.classList.remove('modal-open');

    // Reset overflow
    document.body.style.overflow = '';
});
pageCache = {};
maxPrefetchedPage = 0;   // <-- add this line anywhere you clear pageCache
function toggleFilters() {
    const filtersContent = document.getElementById('filtersContent');
    filtersContent.style.display = filtersContent.style.display === 'none' ? 'block' : 'none';
  }


  function filterByDiscount() {
    const availabilityFilter = document.getElementById('availabilityFilter');
    if (availabilityFilter) {
      availabilityFilter.value = 'discount:available'; // Simulate "تخفيض" option
      applyFilters(); // Trigger the actual filter logic
    }
  }

