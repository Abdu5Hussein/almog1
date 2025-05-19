let currentPage = 1;
let lastPage = 1;
let isLoading = false;
let currentFilters = {};
let itemsPerPage = 10;
let datl = {};
let pageCache = {}; 
let maxPrefetchedPage = 0;   // highest page we’ve ever prefetched
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
        companyno: currentFilters.companyno || '',
        oem: currentFilters.oem || '',
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
        const response = await customFetch(`${baseUrl}/hozma/api/producuts/`, {
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
function prefetchNextPages(distance = 5) {
    // Don’t compute until we know the true last page
    if (!lastPage) return;

    const start = maxPrefetchedPage + 1;
    const end   = Math.min(start + distance - 1, lastPage);

    for (let p = start; p <= end; p++) {
        if (!pageCache[p]) {
            fetchFilteredData(p).catch(err => console.error('Prefetch error:', err));
        }
    }

    // Remember how far ahead we’ve gone
    maxPrefetchedPage = Math.max(maxPrefetchedPage, end);
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
  
      const stock         = parseInt(item.showed) || 0;
      const cartItem      = cart.find(ci => ci.pno === item.pno);
      const cartQuantity  = cartItem ? cartItem.quantity : 0;
  
      /* ──────── ▸ price / discount logic ◂ ──────── */
      const discount  = item.discount ? parseFloat(item.discount) : 0;   // e.g. 0.10
      const finalPrice = parseFloat(item.buyprice || 0);                 // already discounted
      const originalPrice = discount ? finalPrice / (1 - discount) : finalPrice;
  
      const priceCellContent = discount
        ? `
          <span class="text-decoration-line-through text-muted me-1">
            ${originalPrice.toFixed(2)} د.ل
          </span>
          <span class="fw-bold text-danger">
            ${finalPrice.toFixed(2)} د.ل
          </span>
          <span class="badge bg-danger ms-1">
            خصم ${(discount * 100).toFixed(0)}%
          </span>`
        : `${finalPrice.toFixed(2)} د.ل`;
      /* ──────────────────────────────────────────── */
  
      row.innerHTML = `
  <td class="clickable-cell" data-pno="${item.pno}">${item.pno ?? '-'}</td>
  <td class="clickable-cell" data-pno="${item.pno}">${item.itemname ?? '-'}</td>
  
  <td>${item.companyproduct ?? '-'}</td>
  <td>
    ${stock > 10
        ? `<span class="badge bg-success">متوفر</span>`
        : stock > 0
          ? `<span class="badge bg-warning text-dark">كمية محدودة</span>`
          : `<span class="badge bg-danger">غير متوفر</span>`}
  </td>
  <td>${priceCellContent}</td>
  <td>
    <a href="/hozma/products/${item.pno}" class="btn btn-sm btn-primary mt-1">تفاصيل</a>
  </td>
  <td>
    <div class="quantity-control">
      <button class="btn btn-sm btn-outline-secondary quantity-btn"
              onclick="decrementQuantity('${item.pno}')">-</button>
  
      <input type="number" class="form-control form-control-sm quantity-input"
             id="qty-${item.pno}" value="${cartQuantity}" min="0"
             onchange="updateQuantity('${item.pno}', this.value)">
  
      <button class="btn btn-sm btn-outline-secondary quantity-btn"
              onclick="incrementQuantity('${item.pno}')">+</button>
    </div>
  </td>
  <td>
    <button class="btn btn-sm btn-success mb-1"
            onclick="addToCartWithQuantity(
              '${item.pno}',
              '${item.fileid}',
              '${item.itemno}',
              '${item.itemname}',
              ${finalPrice.toFixed(2)},
              '',
              document.getElementById('qty-${item.pno}').value,
              ${item.showed}
            )">
      شراء
    </button>
  </td>
  `;
  
      /* Allow pno & name cells to open the image dialog */
      row.querySelectorAll('.clickable-cell').forEach(cell => {
        cell.style.cursor = 'pointer';
        cell.addEventListener('click', e => {
          if (!e.target.classList.contains('quantity-btn') &&
              !e.target.classList.contains('quantity-input')) {
            showProductImages(item.pno);
          }
        });
      });
  
      productList.appendChild(row);
    }
  }
  
let currentImageModal = null;

async function showProductImages(pno) {
    console.debug("Fetching images for product with PNO:", pno);

    try {
        // Get modal elements
        const modalElement = document.getElementById('imageModal');
        const modalBody = modalElement.querySelector('.modal-body');

        // Remove any existing modal instances
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.hide();
            modalElement.addEventListener('hidden.bs.modal', () => {
                existingModal.dispose();
            }, { once: true });
        }

        // Show loading state
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border" role="status"></div>
                <p class="mt-2">جارٍ تحميل الصور...</p>
            </div>
        `;

        // Initialize new modal properly
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: 'static', // Prevent multiple backdrops
            keyboard: true,
            focus: true
        });

        // Show modal before fetching images
        modal.show();

        // Fetch images
        const response = await customFetch(`${baseUrl}/api/products/${pno}/get-images`);
        const data = await response.json();

        // Process images response
        if (data && Array.isArray(data) && data.length > 0) {
            let imagesHTML = '';
            data.forEach((imgObj) => {
                const imgUrl = `${baseUrl}${imgObj.image_obj}`;
                imagesHTML += `
                    <div class="mb-3">
                        <img src="${imgUrl}" class="img-fluid rounded mb-2" style="max-height: 60vh;">
                        <div class="text-center">
                            <a href="${imgUrl}" target="_blank" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-arrows-angle-expand"></i> فتح الصورة في نافذة جديدة
                            </a>
                        </div>
                    </div>
                `;
            });
            modalBody.innerHTML = imagesHTML;
        } else {
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-image text-muted" style="font-size: 3rem;"></i>
                    <p class="mt-3">لا توجد صور متاحة لهذا المنتج</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching product images:', error);
        const modalBody = document.querySelector('#imageModal .modal-body');
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-exclamation-triangle text-danger" style="font-size: 3rem;"></i>
                <p class="mt-3">حدث خطأ أثناء تحميل الصور</p>
            </div>
        `;
    }
    // Debug info
    console.log('Existing backdrops:', document.querySelectorAll('.modal-backdrop').length);
    console.log('Existing modals:', document.querySelectorAll('.modal.show').length);
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
        companyno: document.getElementById('companynoFilter').value.trim(),
        oem: document.getElementById('oemFilter').value.trim(),
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
  
    console.debug("Loading items for page:", currentPage);
  
    const { data, last_page, total_rows } = await fetchFilteredData(currentPage);
    lastPage = last_page || 1;
  
    await displayItems(data);
    
    updatePaginationInfo(total_rows);
  
    /* ----- NEW: always prefetch the next 5 pages ----- */
    prefetchNextPages(5);
  
    document.getElementById('loading-spinner').style.display = 'none';
    isLoading = false;
    
    // Scroll to top of the table after loading new items
    const tableContainer = document.querySelector('.scroll-table-container');
    if (tableContainer) {
        tableContainer.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Update pagination information
function updatePaginationInfo(total_rows) {
    console.debug("Total items:", total_rows, "Current page:", currentPage, "Last page:", lastPage);
    document.getElementById('pageInfo').textContent =
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

function nextPage() {
    if (currentPage < lastPage) {
        document.getElementById('pageInput').value = currentPage + 1;
        changePage();
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

    // Add click event for apply filters button
    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);

    // Add click event for reset filters button
    document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);

    // Pagination controls
    document.getElementById('prevPageBtn').addEventListener('click', prevPage);
    document.getElementById('nextPageBtn').addEventListener('click', nextPage);
    document.getElementById('pageInput').addEventListener('change', changePage);
    document.getElementById('itemsPerPage').addEventListener('change', changeItemsPerPage);

    // Initial load
    applyFilters();
});

window.onload = function () {
    // Call applyFilters on page load to load items with or without filters
    applyFilters();
};

// Additional event bindings (duplicate entries kept as in original)
document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);
document.getElementById('prevPageBtn').addEventListener('click', prevPage);
document.getElementById('nextPageBtn').addEventListener('click', nextPage);
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