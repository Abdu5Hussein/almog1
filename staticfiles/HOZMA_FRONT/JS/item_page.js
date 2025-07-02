document.addEventListener('DOMContentLoaded', () => {
    customFetch('/hozma/api/company-products/')
      .then(response => response.json())
      .then(data => {
        const select = document.getElementById('companyproductFilter');
        data.forEach(product => {
          const option = document.createElement('option');
          option.value = product;
          option.textContent = product;  // You can replace this with Arabic translation if needed
          select.appendChild(option);
        });
      })
      .catch(error => {
        console.error('Error fetching company products:', error);
      });
  });

  document.addEventListener('DOMContentLoaded', () => {
  customFetch('/hozma/api/item-categories/')
    .then(response => response.json())
    .then(payload => {
      const categories = payload.categories || [];
      const select = document.getElementById('companynoFilter');

      categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.name; // 👈 استخدم الاسم كقيمة
        option.textContent = `${cat.name} (${cat.item_count})`; // 👈 يعرض الاسم والعدد
        select.appendChild(option);
      });
    })
    .catch(err => console.error('خطأ في جلب فئات الأصناف:', err));
});