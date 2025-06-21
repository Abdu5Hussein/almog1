document.addEventListener('DOMContentLoaded', function () {
    const pathParts = window.location.pathname.split('/');
    const invoiceNo = pathParts[pathParts.length - 2] || pathParts[pathParts.length - 1];
    let currentOrder = null;
    let originalQuantities = {};

    // Set print date
    document.getElementById('printDate').textContent = new Date().toLocaleDateString('en-GB');

    // Initialize modals
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    const rejectModal = new bootstrap.Modal(document.getElementById('rejectModal'));

    // Event listeners
    document.getElementById('confirmBtn').addEventListener('click', () => confirmModal.show());
    document.getElementById('rejectBtn').addEventListener('click', () => rejectModal.show());
    document.getElementById('editBtn').addEventListener('click', enterEditMode);
    document.getElementById('cancelEditBtn').addEventListener('click', cancelEditMode);
    document.getElementById('saveChangesBtn').addEventListener('click', saveChanges);
    document.getElementById('confirmOrderBtn').addEventListener('click', confirmOrder);
    document.getElementById('rejectOrderBtn').addEventListener('click', rejectOrder);

    // Load order details
    if (invoiceNo && !isNaN(invoiceNo)) {
loadOrderDetails(invoiceNo);
loadRelatedOrders(invoiceNo); // Add this line
} else {
console.error("رقم الطلب غير صالح.");
}

    async function loadOrderDetails(invoiceNo) {
      try {
        const response = await customFetch(`http://45.13.59.226/hozma/api/preorders-buy/?invoice_no=${invoiceNo}`);
        const data = await response.json();

        if (data.preorders_buy.length > 0) {
          currentOrder = data.preorders_buy[0];
          document.getElementById('invoiceNo').textContent = currentOrder.invoice_no;
          document.getElementById('orderDate').textContent = new Date(currentOrder.invoice_date).toLocaleDateString('en-GB');
          document.getElementById('customerName').textContent = currentOrder.source || 'غير معروف';

          // Update status badges
          updateStatusBadges();

          // Load order items
          const itemsBody = document.getElementById('orderItemsTable');
          itemsBody.innerHTML = '';
          let totalAmount = 0;

          data.preorder_items_buy.forEach(item => {
            const itemTotal = parseFloat(item.cost_total_price) || 0;
            totalAmount += itemTotal;
            originalQuantities[item.item_no] = item.Confirmed_quantity || item.Asked_quantity;

            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${item.pno}</td>
              <td>${item.name}</td>
              <td>${item.company || 'غير محدد'}</td>
              <td class="asked-quantity">${item.Asked_quantity}</td>
              <td class="no-print">
                <span class="confirmed-quantity quantity-display">${item.Confirmed_quantity || item.Asked_quantity}</span>
                <input type="number" min="0" class="form-control quantity-input d-none" 
                       value="${item.Confirmed_quantity || item.Asked_quantity}" 
                       data-item-no="${item.pno}"
                       data-original="${item.Asked_quantity}">
              </td>
<td>${Number(item.cost_unit_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
<td>${itemTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>

            `;
            itemsBody.appendChild(row);
          });

          document.getElementById('orderTotal').textContent = totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2 }) + ' دينار';
        } else {
          alert("لم يتم العثور على الطلب.");
        }
      } catch (error) {
        console.error('خطأ في تحميل التفاصيل:', error);
        alert('فشل في تحميل تفاصيل الطلب. حاول مرة أخرى.');
      }
    }

    function updateStatusBadges() {
      const statusBadge = document.getElementById('orderStatus');
      const sendBadge = document.getElementById('sendStatus');
      
      if (currentOrder.confirmed) {
        statusBadge.className = 'status-badge status-confirmed';
        statusBadge.textContent = 'تم التأكيد';
        document.getElementById('editBtn').disabled = true;
        document.getElementById('confirmBtn').disabled = true;
      } else {
        statusBadge.className = 'status-badge status-pending';
        statusBadge.textContent = 'قيد الانتظار';
      }

      if (currentOrder.send) {
        sendBadge.className = 'status-badge status-sent';
        sendBadge.textContent = 'تم الإرسال';
      } else {
        sendBadge.className = 'status-badge status-not-sent';
        sendBadge.textContent = 'لم يتم الإرسال';
      }
    }

    function enterEditMode() {
      if (confirm("هل تريد الدخول إلى وضع التعديل لتغيير الكميات المؤكدة؟")) {
        document.querySelector('.order-items').classList.add('edit-mode-active');
        document.getElementById('editBtn').disabled = true;
        document.getElementById('confirmBtn').disabled = true;
        document.getElementById('rejectBtn').disabled = true;
      }
    }

    function cancelEditMode() {
      if (confirm("هل أنت متأكد أنك تريد إلغاء التعديلات؟ سيتم فقدان جميع التغييرات غير المحفوظة.")) {
        // Reset all inputs to original values
        document.querySelectorAll('.quantity-input').forEach(input => {
          const itemNo = input.dataset.itemNo;
          input.value = originalQuantities[itemNo];
          input.classList.add('d-none');
        });
        
        // Show display values
        document.querySelectorAll('.quantity-display').forEach(el => {
          el.classList.remove('d-none');
        });
        
        // Exit edit mode
        exitEditMode();
      }
    }

    function exitEditMode() {
      document.querySelector('.order-items').classList.remove('edit-mode-active');
      document.getElementById('editBtn').disabled = false;
      document.getElementById('confirmBtn').disabled = false;
      document.getElementById('rejectBtn').disabled = false;
    }

    async function saveChanges() {
      const itemQuantities = [];
      let hasChanges = false;
      
      // Collect all changed quantities
      document.querySelectorAll('.quantity-input').forEach(input => {
        const itemNo = input.dataset.itemNo;
        const newQuantity = parseInt(input.value);
        const originalQuantity = parseInt(input.dataset.original);
        
        // Only include items with actual changes
        if (newQuantity !== originalQuantity) {
            itemQuantities.push({
                item_no: itemNo.toString(),  // Ensure string type
                new_quantity: newQuantity
            });
            hasChanges = true;
        }
      });

      if (!hasChanges) {
        alert("لم تقم بإجراء أي تغييرات على الكميات.");
        exitEditMode();
        return;
      }

      // Prepare the complete request payload
      const payload = {
        invoice_no: currentOrder.invoice_no.toString(),
        action_type: "update",
        item_quantities: itemQuantities
      };

      console.log("Sending update payload:", payload); // For debugging

      try {
        const response = await customFetch('http://45.13.59.226/hozma/api/confirm-or-update-preorder-items-buy-source/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "فشل في تحديث الكميات");
        }

        const result = await response.json();
        console.log("Update successful:", result); // For debugging
        
        alert("تم تحديث الكميات بنجاح!");
        loadOrderDetails(currentOrder.invoice_no);
        exitEditMode();
        
      } catch (error) {
        console.error('خطأ في تحديث الكميات:', error);
        
        // More detailed error message
        let errorMessage = 'فشل في تحديث الكميات';
        if (error.message.includes("Failed to fetch")) {
          errorMessage += " - تعذر الاتصال بالخادم";
        } else if (error.message) {
          errorMessage += `: ${error.message}`;
        }
        
        alert(errorMessage);
      }
    }

    async function confirmOrder() {
      confirmModal.hide();
      try {
        const response = await customFetch('http://45.13.59.226/hozma/api/confirm-or-update-preorder-items-buy-source/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            invoice_no: currentOrder.invoice_no,
            action_type: "confirm"
          })
        });

        const result = await response.json();
        if (response.ok) {
          alert("تم تأكيد الطلب بنجاح!");
          loadOrderDetails(currentOrder.invoice_no);
        } else {
          throw new Error(result.message || "فشل في تأكيد الطلب");
        }
      } catch (error) {
        console.error('خطأ في تأكيد الطلب:', error);
        alert('فشل في تأكيد الطلب: ' + error.message);
      }
    }

    async function rejectOrder() {
      rejectModal.hide();
      try {
        // Replace with your actual reject API endpoint
        const response = await customFetch('YOUR_REJECT_API_ENDPOINT', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            invoice_no: currentOrder.invoice_no,
            action: "reject"
          })
        });

        if (response.ok) {
          alert("تم رفض الطلب بنجاح!");
          window.location.href = "/hozma/preorders-buy/"; // Redirect to orders list
        } else {
          throw new Error("فشل في رفض الطلب");
        }
      } catch (error) {
        console.error('خطأ في رفض الطلب:', error);
        alert('فشل في رفض الطلب: ' + error.message);
      }
    }

    // Warn about unsaved changes
    window.addEventListener('beforeunload', function(e) {
      if (document.querySelector('.order-items').classList.contains('edit-mode-active')) {
        e.preventDefault();
        e.returnValue = 'لديك تغييرات غير محفوظة. هل أنت متأكد أنك تريد المغادرة؟';
        return e.returnValue;
      }
    });
  });


  async function loadRelatedOrders(invoiceNo) {
try {
  const response = await customFetch(`http://45.13.59.226/hozma/check-preorder-related/${invoiceNo}/`);
  const data = await response.json();
  console.log("Related orders data:", data); // For debugging
  if (data.related_preorders && data.related_preorders.length > 0) {
    const tbody = document.querySelector('#relatedOrdersTable tbody');
    tbody.innerHTML = '';
    
    data.related_preorders.forEach(order => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${order.invoice_no}</td>
        <td>${order.client_name}</td>
        <td>${order.client_rate} (${order.client_category || 'غير محدد'})</td>
<td>${Number(order.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
        <td>${order.payment_status}</td>
        <td>${order.invoice_status}</td>
        <td>${order.date_time ? new Date(order.date_time).toLocaleDateString('en-GB') : 'غير محدد'}</td>
      `;
      tbody.appendChild(row);
    });
  } else {
    document.querySelector('.related-orders').innerHTML = `
      <div class="alert alert-info m-3">
        لا توجد طلبات عملاء مرتبطة بهذا الطلب
      </div>
    `;
  }
} catch (error) {
  console.error('Error loading related orders:', error);
  document.querySelector('.related-orders').innerHTML = `
    <div class="alert alert-danger m-3">
      فشل في تحميل طلبات العملاء المرتبطة: ${error.message}
    </div>
  `;
}
}