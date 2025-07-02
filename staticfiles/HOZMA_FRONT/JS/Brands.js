const container = document.getElementById('brands-container');
const apiUrl = '/hozma/api/companies/'; // updated endpoint

fetch(apiUrl)
  .then(response => response.json())
  .then(data => {
    const brands = data.main_types;  // still uses same key for compatibility

    brands.forEach(brand => {
      const col = document.createElement('div');
      col.className = 'col-lg-3 col-md-4 col-6';

      col.innerHTML = `
        <div class="brand-card h-100">
          <div class="card-body text-center">
            <img src="${brand.logo_obj}" class="img-fluid mb-3" alt="${brand.typename} Logo">
            <h5 class="card-title">${brand.typename}</h5>
            <p class="text-muted small mb-3">قطع غيار متنوعة</p>
            <a href="/hozma/brand/${encodeURIComponent(brand.typename)}/" class="btn">
              <i class="bi bi-eye me-1"></i> تصفح المنتجات
            </a>
          </div>
        </div>
      `;

      container.appendChild(col);
    });
  })
  .catch(error => {
    console.error('Error fetching brand data:', error);
    container.innerHTML = '<p class="text-danger text-center">فشل في تحميل البيانات.</p>';
  });
