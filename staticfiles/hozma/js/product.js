let currentPage = 1;
let lastPage = 1;
let isLoading = false;
let currentFilters = {};
let itemsPerPage = 10;
let datl = {};

// Main function to fetch filtered data
async function fetchFilteredData(page = 1) {
    console.debug("Fetching filtered data for page:", page);

    const filters = {
        pno: currentFilters.pno || '',
        companyno: currentFilters.companyno || '',
        oem: currentFilters.oem || '',
        itemname: currentFilters.itemname || '',
        companyproduct: currentFilters.companyproduct || '',
        availability: currentFilters.availability || '',
        itemmain: currentFilters.itemmain || '',
        page: page,
        size: itemsPerPage,
    };

    console.debug("Full filters being sent:", JSON.stringify(filters, null, 2));

    try {
        const response = await fetchWithAuth(`${baseUrl}/api/filter-items`, 'POST', filters);
        console.debug("Full API response:", response);
        
        if (!response) {
            throw new Error("Empty response from server");
        }

        return {
            data: response?.data || [],
            last_page: response?.last_page || 1,
            total: response?.total || 0
        };
    } catch (error) {
        console.error("API Error:", error);
        return {
            data: [],
            last_page: 1,
            total: 0
        };
    }
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
const stock = parseInt(item.itemvalue) || 0;
const cartItem = cart.find(ci => ci.pno === item.pno);
const cartQuantity = cartItem ? cartItem.quantity : 0;

row.innerHTML = `
<td class="clickable-cell" data-pno="${item.pno}">${item.pno ?? '-'}</td>
<td class="clickable-cell" data-pno="${item.pno}">${item.itemname ?? '-'}</td>

<td>${item.companyproduct ?? '-'}</td>
<td>
${stock > 10 ? `<span class="badge bg-success">متوفر</span>` :
stock > 0 && stock <= 9 ? `<span class="badge bg-warning text-dark">كمية محدودة</span>` :
`<span class="badge bg-danger">غير متوفر</span>`}
</td>
<td>${parseFloat(item.buyprice || 0).toFixed(2)} د.ل</td>
<td>
<div class="quantity-control">
<button class="btn btn-sm btn-outline-secondary quantity-btn" onclick="decrementQuantity('${item.pno}')">-</button>
<input type="number" class="form-control form-control-sm quantity-input"
id="qty-${item.pno}" value="${cartQuantity}" min="0"
onchange="updateQuantity('${item.pno}', this.value)">
<button class="btn btn-sm btn-outline-secondary quantity-btn" onclick="incrementQuantity('${item.pno}')">+</button>
</div>
</td>
<td>
<button class="btn btn-sm btn-success mb-1" onclick="addToCartWithQuantity('${item.pno}', '${item.fileid}', '${item.itemno}', '${item.itemname}', ${parseFloat(item.buyprice || 0).toFixed(2)}, '', document.getElementById('qty-${item.pno}').value, ${item.itemvalue})">
  شراء
</button>

</td>
<td>

<a href="/hozma/products/${item.pno}" class="btn btn-sm btn-primary mt-1">تفاصيل</a>
</td>
`;


row.querySelectorAll('.clickable-cell').forEach(cell => {
    cell.style.cursor = 'pointer';
    cell.addEventListener('click', (e) => {
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
            backdrop: 'static', // Changed to static to prevent multiple backdrops
            keyboard: true,
            focus: true
        });
        
        // Show modal before fetching images for better UX
        modal.show();

        // Fetch images
        const response = await fetchWithAuth(`${baseUrl}/api/products/${pno}/get-images`);
        
        // Process images response
        if (response && Array.isArray(response) && response.length > 0) {
            let imagesHTML = '';
            response.forEach((imgObj) => {
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
    // Debug code - add to your showProductImages function
console.log('Existing backdrops:', document.querySelectorAll('.modal-backdrop').length);
console.log('Existing modals:', document.querySelectorAll('.modal.show').length);
}

function changeItemMain(value) {
    // Set the hidden input value
    document.getElementById('itemmain').value = value;
    
    // Update active state visually
    document.querySelectorAll('.itemmain-icon').forEach(icon => {
        icon.classList.toggle('active', icon.dataset.value === value);
    });
    
    // Apply filters
    applyFilters();
}
// Apply filters from input fields
function applyFilters() {
    console.debug("Applying filters...");
  
    currentFilters = {
      pno: document.getElementById('pnoFilter').value.trim(),
      companyno: document.getElementById('companynoFilter').value.trim(),
      oem: document.getElementById('oemFilter').value.trim(),
      itemname: document.getElementById('itemnameFilter').value.trim(),
      companyproduct: document.getElementById('companyproductFilter').value.trim(),
      availability: document.getElementById('availabilityFilter').value, // Removed trim() as it's a select value
      itemmain: document.getElementById('itemmain') ? document.getElementById('itemmain').value : '',
    };
  
    console.debug("Current filters:", currentFilters);
  
    currentPage = 1;
    document.getElementById('pageInput').value = 1;
    document.getElementById('productList').innerHTML = "";
    document.getElementById('loading-spinner').style.display = 'block';
  
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
    
    // Reset itemmain
    document.getElementById('itemmain').value = '';
    document.querySelectorAll('.itemmain-icon').forEach(icon => {
        icon.classList.remove('active');
    });
    
    applyFilters();
}

// Load more items with pagination
async function loadMoreItems() {
if (isLoading) return;
isLoading = true;

console.debug("Loading more items for page:", currentPage);

const { data, last_page, total } = await fetchFilteredData(currentPage);

lastPage = last_page || 1;

await displayItems(data);
updatePaginationInfo(total);

document.getElementById('loading-spinner').style.display = 'none';
isLoading = false;
}

// Update pagination information
function updatePaginationInfo(totalItems) {
console.debug("Total items:", totalItems, "Current page:", currentPage, "Last page:", lastPage);
document.getElementById('pageInfo').textContent =
`الصفحة ${currentPage} من ${lastPage} | إجمالي العناصر: ${totalItems}`;
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
loadMoreItems();
} else {
pageInput.value = currentPage;
}
}

// Go to previous page
function prevPage() {
if (currentPage > 1) {
document.getElementById('pageInput').value = currentPage - 1;
changePage();
}
}

// Go to next page
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

loadMoreItems();
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
// Add event listeners for filter inputs
document.getElementById('pnoFilter').addEventListener('keyup', function(e) {
if (e.key === 'Enter') applyFilters();
});
document.getElementById('companynoFilter').addEventListener('keyup', function(e) {
if (e.key === 'Enter') applyFilters();
});
document.getElementById('oemFilter').addEventListener('keyup', function(e) {
if (e.key === 'Enter') applyFilters();
});
document.getElementById('itemnameFilter').addEventListener('keyup', function(e) {
if (e.key === 'Enter') applyFilters();
});
document.getElementById('companyproductFilter').addEventListener('keyup', function(e) {
if (e.key === 'Enter') applyFilters();
});
document.getElementById('availabilityFilter').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') applyFilters();
    });
    document.querySelectorAll('.itemmain-icon').forEach(icon => {
        icon.addEventListener('click', function() {
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

window.onload = function() {
// Call applyFilters on page load to load items with or without filters
applyFilters();
};



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




// Cleanup any existing modals when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Remove any existing backdrops
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    
    // Remove modal-open class from body
    document.body.classList.remove('modal-open');
    
    // Reset overflow
    document.body.style.overflow = '';
});
