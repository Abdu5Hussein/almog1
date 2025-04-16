let currentPage = 1;
let lastPage = 1;
let isLoading = false;
let currentFilters = {};
let itemsPerPage = 10;

async function fetchFilteredData(page = 1) {
  const filters = {
    itemno: currentFilters.itemno || '',
    itemmain: currentFilters.itemmain || '',
    itemsubmain: currentFilters.itemsubmain || '',
    engine_no: currentFilters.engine_no || '',
    itemthird: currentFilters.itemthird || '',
    page: page,
    size: itemsPerPage,
  };

  const response = await fetchWithAuth(`${baseUrl}/api/filter-items`, 'POST', filters);
  return {
    data: response?.data || [],
    last_page: response?.last_page || 1,
    total: response?.total || 0
  };
}

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
      <td class="clickable-cell" data-pno="${item.pno}">${item.itemno ?? '-'}</td>
      <td class="maintype-col clickable-cell" data-pno="${item.pno}">${item.itemmain ?? '-'}</td>
      <td class="subtype-col clickable-cell" data-pno="${item.pno}">${item.itemsubmain ?? '-'}</td>
      <td class="engine-col clickable-cell" data-pno="${item.pno}">${item.engine_no ?? '-'}</td>
      <td class="location-col clickable-cell" data-pno="${item.pno}">${item.itemthird ?? '-'}</td>
      <td class="clickable-cell" data-pno="${item.pno}">${item.itemname ?? '-'}</td>
      <td>${parseFloat(item.buyprice || 0).toFixed(2)} د.أ</td>
      <td class="company-col">${item.companyproduct ?? '-'}</td>
      <td>
        ${stock > 5 ? `<span class="badge bg-success">متوفر</span>` : 
          stock > 0 ? `<span class="badge bg-warning text-dark">كمية محدودة</span>` : 
          `<span class="badge bg-danger">غير متوفر</span>`}
      </td>
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
        <button class="btn btn-sm btn-success" onclick="addToCartWithQuantity('${item.pno}', '${item.itemno}', '${item.itemname}', ${parseFloat(item.buyprice || 0).toFixed(2)}, '', document.getElementById('qty-${item.pno}').value)">
          شراء
        </button>
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

async function showProductImages(pno) {
  try {
    const modalBody = document.querySelector('#imageModal .modal-body');
    modalBody.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border" role="status"></div>
        <p class="mt-2">جارٍ تحميل الصور...</p>
      </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();

    const response = await fetchWithAuth(`${baseUrl}/api/products/${pno}/get-images`);
    
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
}

function applyFilters() {
    // Collecting filter values
    currentFilters = {
      itemno: document.getElementById('modelFilter').value.trim(),
      engine_no: document.getElementById('engineFilter').value.trim(),
      itemmain: document.getElementById('mainTypeFilter').value.trim(),
      itemsubmain: document.getElementById('subTypeFilter').value.trim(),
    };
  
    // Debug print for filter values
    console.log("Current Filters:", currentFilters);
  
    // Resetting page number to 1 and updating the input field
    currentPage = 1;
    document.getElementById('pageInput').value = 1;
  
    // Debug print for currentPage and pageInput value
    console.log("Current Page:", currentPage);
    console.log("Page Input Value:", document.getElementById('pageInput').value);
  
    // Clearing product list and showing loading spinner
    document.getElementById('productList').innerHTML = "";
    document.getElementById('loading-spinner').style.display = 'block';
  
    // Debug print to confirm that the loading spinner is displayed
    console.log("Loading spinner displayed");
  
    // Call to load more items
    loadMoreItems();
  }
  

function resetFilters() {
  document.getElementById('modelFilter').value = '';
  document.getElementById('engineFilter').value = '';
  document.getElementById('mainTypeFilter').value = '';
  document.getElementById('subTypeFilter').value = '';
  applyFilters();
}

async function loadMoreItems() {
  if (isLoading) return;
  isLoading = true;

  const { data, last_page, total } = await fetchFilteredData(currentPage);
  lastPage = last_page;
  
  await displayItems(data);
  updatePaginationInfo(total);
  
  document.getElementById('loading-spinner').style.display = 'none';
  isLoading = false;
}

function updatePaginationInfo(totalItems) {
  document.getElementById('pageInfo').textContent = 
    `الصفحة ${currentPage} من ${lastPage} | إجمالي العناصر: ${totalItems}`;
}

function changePage() {
  const pageInput = document.getElementById('pageInput');
  const newPage = parseInt(pageInput.value, 10);
  if (newPage > 0 && newPage <= lastPage && newPage !== currentPage) {
    currentPage = newPage;
    document.getElementById('productList').innerHTML = "";
    document.getElementById('loading-spinner').style.display = 'block';
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

function changeItemsPerPage() {
  itemsPerPage = parseInt(document.getElementById('itemsPerPage').value);
  currentPage = 1;
  document.getElementById('pageInput').value = 1;
  document.getElementById('productList').innerHTML = "";
  document.getElementById('loading-spinner').style.display = 'block';
  loadMoreItems();
}

async function populateMainTypes() {
  try {
    const response = await fetchWithAuth(`http://45.13.59.226/api/main-types/`);
    const mainTypes = await response?.main_types || [];

    const select = document.getElementById('mainTypeFilter');
    select.innerHTML = `<option value="">كل الأصناف الرئيسية</option>`;

    mainTypes.forEach(main => {
      const option = document.createElement('option');
      option.value = main.typename;  // Set value to typename
      option.textContent = main.typename || `رئيسي ${main.fileid}`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error("خطأ في تحميل الأصناف الرئيسية:", error);
  }
}


async function populateSubTypes(mainTypeId) {
  try {
    const response = await fetchWithAuth(`http://45.13.59.226/api/sub-types/`);
    const subTypes = await response?.sub_types || [];

    const select = document.getElementById('subTypeFilter');
    select.innerHTML = `<option value="">كل الأصناف الفرعية</option>`;

    subTypes
      .filter(sub => sub.maintype_fk == mainTypeId)
      .forEach(sub => {
        const option = document.createElement('option');
        option.value = sub.fileid;
        option.textContent = sub.subtypename || `فرعي ${sub.fileid}`;
        select.appendChild(option);
      });

    document.getElementById('modelFilter').innerHTML = `<option value="">كل الموديلات</option>`;
  } catch (error) {
    console.error("خطأ في تحميل الأصناف الفرعية:", error);
  }
}

async function populateModels(subTypeId) {
  try {
    const response = await fetchWithAuth(`http://45.13.59.226/api/models/`);
    const models = await response?.models || [];

    const select = document.getElementById('modelFilter');
    select.innerHTML = `<option value="">كل الموديلات</option>`;

    models
      .filter(model => model.subtype_fk == subTypeId)
      .forEach(model => {
        const option = document.createElement('option');
        option.value = model.fileid;
        option.textContent = model.model_name || `موديل ${model.fileid}`;
        select.appendChild(option);
      });
  } catch (error) {
    console.error("خطأ في تحميل الموديلات:", error);
  }
}

// Initial load
window.addEventListener('DOMContentLoaded', () => {
  populateMainTypes();
  loadMoreItems();

  document.getElementById('mainTypeFilter').addEventListener('change', (e) => {
    const selectedMain = e.target.value;
    populateSubTypes(selectedMain);
  });

  document.getElementById('subTypeFilter').addEventListener('change', (e) => {
    const selectedSub = e.target.value;
    populateModels(selectedSub);
  });

  document.getElementById('filterBtn').addEventListener('click', applyFilters);
  document.getElementById('resetBtn').addEventListener('click', resetFilters);
  document.getElementById('itemsPerPage').addEventListener('change', changeItemsPerPage);
  document.getElementById('prevPageBtn').addEventListener('click', prevPage);
  document.getElementById('nextPageBtn').addEventListener('click', nextPage);
  document.getElementById('pageInput').addEventListener('change', changePage);
});
