let currentPage = 1;
let lastPage = 1;
let isLoading = false;
let currentFilters = {};
let itemsPerPage = 10;
let datl = {};

async function fetchFilteredData(page = 1) {
  console.debug("Fetching filtered data for page:", page);
  
  const filters = {
    itemno: currentFilters.itemno || '',
    itemmain: currentFilters.itemmain || '',
    itemsubmain: currentFilters.itemsubmain || '',
    engine_no: currentFilters.engine_no || '',
    itemthird: currentFilters.itemthird || '',
    page: page,
    size: itemsPerPage,
  };

  console.debug("Filters applied:", filters);

  const response = await fetchWithAuth(`${baseUrl}/api/filter-items`, 'POST', filters);
  
  console.debug("Response data:", response);
  
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
    console.debug("Displaying item:", item);
    
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
  console.debug("Fetching images for product with PNO:", pno);
  
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
    
    console.debug("Image fetch response:", response);
    
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
  console.debug("Applying filters...");
  
  currentFilters = {
    itemno: document.getElementById('modelFilter').value.trim(),
    engine_no: document.getElementById('engineFilter').value.trim(),
    itemmain: document.getElementById('mainTypeFilter').value.trim(),
    itemsubmain: document.getElementById('subTypeFilter').value.trim(),
  };
  
  console.debug("Current filters:", currentFilters);
  
  currentPage = 1;
  document.getElementById('pageInput').value = 1;
  document.getElementById('productList').innerHTML = "";
  document.getElementById('loading-spinner').style.display = 'block';
  
  loadMoreItems();
}

function resetFilters() {
  console.debug("Resetting filters...");
  
  document.getElementById('modelFilter').value = '';
  document.getElementById('engineFilter').value = '';
  document.getElementById('mainTypeFilter').value = '';
  document.getElementById('subTypeFilter').value = '';
  
  applyFilters();
}

async function loadMoreItems() {
  if (isLoading) return;
  isLoading = true;

  console.debug("Loading more items for page:", currentPage);
  
  const { data, last_page, total } = await fetchFilteredData(currentPage);
  lastPage = last_page;
  
  await displayItems(data);
  updatePaginationInfo(total);
  
  document.getElementById('loading-spinner').style.display = 'none';
  isLoading = false;
}

function updatePaginationInfo(totalItems) {
  console.debug("Total items:", totalItems, "Current page:", currentPage, "Last page:", lastPage);
  document.getElementById('pageInfo').textContent = 
    `الصفحة ${currentPage} من ${lastPage} | إجمالي العناصر: ${totalItems}`;
}

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
  console.debug("Changing items per page to:", itemsPerPage);
  
  currentPage = 1;
  document.getElementById('pageInput').value = 1;
  document.getElementById('productList').innerHTML = "";
  document.getElementById('loading-spinner').style.display = 'block';
  
  loadMoreItems();
}

// 1. Fetch data and start chain
fetch('http://45.13.59.226/api/get-drop-lists')
  .then(res => res.json())
  .then(json => {
    datl = json;
    console.debug("Filter data received:", datl);
    populateMainTypes(json.main_types);
  });

// 2. Populate Main Types
function populateMainTypes(mainTypes) {
  const mainSelect = document.getElementById("mainTypeFilter");
  mainSelect.innerHTML = '<option value="">اختر النوع الرئيسي</option>';

  mainTypes.forEach(main => {
    const option = document.createElement("option");
    option.value = main.typename;
    option.textContent = main.typename;
    mainSelect.appendChild(option);
  });

  mainSelect.addEventListener('change', () => {
    const selectedName = mainSelect.value;
    const selectedMain = mainTypes.find(main => main.typename === selectedName);
    if (!selectedMain) return;

    const selectedMainId = parseInt(selectedMain.fileid);
    console.debug("Selected main type ID:", selectedMainId);

    populateSubTypes(selectedMainId);
    document.getElementById("engineFilter").innerHTML = '';
    document.getElementById("modelkFilter").innerHTML = '<option value="">اختر سنة الصنع</option>';
  });
}

// 3. Populate Sub Types
function populateSubTypes(mainId) {
  const subTypes = datl.sub_types.filter(sub => sub.maintype_fk === mainId);
  const subSelect = document.getElementById("subTypeFilter");
  subSelect.innerHTML = '<option value="">اختر النوع الفرعي</option>';

  subTypes.forEach(sub => {
    const option = document.createElement("option");
    option.value = sub.subtypename;
    option.textContent = sub.subtypename;
    subSelect.appendChild(option);
  });

  subSelect.addEventListener('change', () => {
    const selectedName = subSelect.value;
    const selectedSub = subTypes.find(sub => sub.subtypename === selectedName);
    if (!selectedSub) return;

    const selectedSubId = parseInt(selectedSub.fileid);
    console.debug("Selected sub type ID:", selectedSubId);

    populateModel(selectedSubId);
    populateEngine(selectedName); // <-- ✅ added here
  });
}


// 4. Populate Models
function populateModel(subId) {
  const models = datl.models.filter(mod => mod.subtype_fk === subId);
  const modelSelect = document.getElementById("modelkFilter");
  modelSelect.innerHTML = '<option value="">اختر سنة الصنع</option>';

  models.forEach(mod => {
    const option = document.createElement("option");
    option.value = mod.model_name;
    option.textContent = mod.model_name;
    modelSelect.appendChild(option);
  });

  modelSelect.addEventListener('change', () => {
    const selectedName = modelSelect.value;
    const selectedModel = models.find(mod => mod.model_name === selectedName);
    if (selectedModel) {
      console.debug("Selected model ID:", selectedModel.fileid);
      // Do something with selectedModel.fileid...
    }
  });
}

function populateEngine(subTypeName) {
  console.debug("🚀 populateEngine called with subtype name:", subTypeName);

  const engines = datl.engines.filter(mod => {
    if (!mod.subtype_str) return false;
    const subtypes = mod.subtype_str.split(';').map(s => s.trim());
    return subtypes.includes(subTypeName);
  });

  console.debug("🔍 Filtered engines matching subtype_str:", engines);

  const engineSelect = document.getElementById("engineFilter");
  engineSelect.innerHTML = '<option value="">اختر المحرك</option>';

  engines.forEach(mod => {
    console.debug("➕ Adding engine option:", mod.engine_name);
    const option = document.createElement("option");
    option.value = mod.engine_name;
    option.textContent = mod.engine_name;
    engineSelect.appendChild(option);
  });

  engineSelect.addEventListener('change', () => {
    const selectedEngine = engineSelect.value;
    const selectedModel = engines.find(mod => mod.engine_name === selectedEngine);
    if (selectedModel) {
      console.debug("✅ Selected engine:", selectedModel.engine_name);
      console.debug("📦 Corresponding model object:", selectedModel);
      console.debug("🆔 File ID of selected model:", selectedModel.fileid);
    } else {
      console.debug("⚠️ Engine not found in filtered list.");
    }
  });
}


