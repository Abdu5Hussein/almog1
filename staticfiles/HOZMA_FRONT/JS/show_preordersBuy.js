/* ────────────────────────────────────────────────────────────────
     GLOBAL STATE
  ───────────────────────────────────────────────────────────────── */
let currentPage = 1;
let totalPages = 1;
let currentOrderDetails = null;

let statusFilter = 'all';      // pending | confirmed | all
let sentFilter = 'all';      // sent | not_sent | all
let dateFilter = 'all';      // all | today | week | month
let searchTerm = '';

/* ────────────────────────────────────────────────────────────────
   DOM READY
───────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const btnPrev = document.getElementById('prev-page');
  const btnNext = document.getElementById('next-page');
  const pageLabel = document.getElementById('page-label');

  /* -------- first load ---------- */
  fetchOrders();

  /* -------- search -------------- */
  let debounce;
  searchInput.addEventListener('input', e => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      searchTerm = e.target.value.trim();
      fetchOrders(1);
    }, 400);
  });

  /* -------- filter buttons ------ */
  window.filterOrders = function (type) {
    // Which filter changed?
    if (['pending', 'confirmed', 'all'].includes(type)) {
      statusFilter = type;
    } else if (['sent', 'not-sent', 'all'].includes(type)) {
      sentFilter = (type === 'not-sent') ? 'not_sent' : type;   // map to backend key
    }
    document.querySelectorAll('.filter-buttons .btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    fetchOrders(1);
  };

  /* -------- pagination ---------- */
  btnPrev.addEventListener('click', () => { if (currentPage > 1) fetchOrders(currentPage - 1); });
  btnNext.addEventListener('click', () => { if (currentPage < totalPages) fetchOrders(currentPage + 1); });
});

/* ──────────────────────────────────────────────────────────────
   MAIN FETCH
───────────────────────────────────────────────────────────── */
async function fetchOrders(page = 1) {
  currentPage = page;

  /* show spinner in table */
  const tbody = document.querySelector('#preordersTable');
  tbody.innerHTML = `
          <tr><td colspan="7" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">جار التحميل...</span>
              </div>
              <p class="mt-3 mb-0">جارٍ تحميل الطلبات...</p>
          </td></tr>`;

  try {
    const res = await fetch('/hozma/api/preorders-buy_v2/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: currentPage,
        page_size: 10,
        status_filter: statusFilter,
        sent_filter: sentFilter,
        date_filter: dateFilter,
        search_term: searchTerm,
        sort_by: 'date_desc'
      })
    });
    const data = await res.json();

    paintTable(data.preorders_buy || []);
    updatePagination(data.pagination || {});

  } catch (err) {
    console.error(err);
    tbody.innerHTML = `
              <tr><td colspan="7" class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle"></i>
                فشل تحميل الطلبات. حاول لاحقًا.
              </td></tr>`;
  }
}

/* ──────────────────────────────────────────────────────────────
   RENDER FUNCTIONS
───────────────────────────────────────────────────────────── */
function paintTable(orders) {
  const tbody = document.querySelector('#preordersTable');
  tbody.innerHTML = '';

  if (!orders.length) {
    tbody.innerHTML = `
              <tr><td colspan="7" class="text-center text-muted py-4">
                <i class="bi bi-inbox" style="font-size:2rem"></i>
                <p class="mt-2">لا توجد طلبات مبدئية لعرضها</p>
              </td></tr>`;
    return;
  }

  orders.forEach(order => {
    const tr = document.createElement('tr');
    tr.className = 'clickable-row';
    tr.dataset.status = order.confirmed ? 'confirmed' : 'pending';
    tr.dataset.sent = order.send ? 'sent' : 'not-sent';

    tr.innerHTML = `
              <td>${order.invoice_no}</td>
              <td>${formatDate(order.invoice_date)}</td>
              <td>${order.source || 'غير متوفر'}</td>
<td>${Number(order.net_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })} دينار</td>
               <td>
              <span class="badge ${order.send === true ? 'bg-info' : 'bg-danger'}">
  ${order.send === true ? 'تم الإرسال' : 'لم يتم الإرسال'}
</span>

              </td>
              <td>
                <span class="badge ${order.confirmed ? 'bg-success' : 'bg-warning'}">
                  ${order.confirmed ? 'تم التأكيد' : 'قيد الانتظار'}
                </span>
              </td>

                        <td class="action-buttons">
  <!-- View in Modal -->
  <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); viewOrderDetails('${order.invoice_no}')">
    <i class="bi bi-eye"></i> عرض
  </button>

  <!-- Navigate to Details Page -->
  <a href="/hozma/preorders-buy/${order.invoice_no}" class="btn btn-sm btn-outline-secondary" onclick="event.stopPropagation();">
    <i class="bi bi-list-ul"></i> تعديل
  </a>
</td>

            `;
    tr.addEventListener('click', () => viewOrderDetails(order.invoice_no));
    tbody.appendChild(tr);
  });
}

function updatePagination(pagination) {
  const btnPrev = document.getElementById('prev-page');
  const btnNext = document.getElementById('next-page');
  const pageLabel = document.getElementById('page-label');

  totalPages = pagination.total_pages || 1;
  currentPage = pagination.current_page || 1;

  pageLabel.textContent = `${currentPage} / ${totalPages}`;
  btnPrev.disabled = !pagination.has_previous;
  btnNext.disabled = !pagination.has_next;
}

function formatDate(dateString) {
  if (!dateString) return 'غير معروف';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-UK') + ' ' + date.toLocaleTimeString('en-UK');
}

/* ──────────────────────────────────────────────────────────────
   ORDER DETAILS FUNCTIONS
───────────────────────────────────────────────────────────── */
async function viewOrderDetails(invoiceNo) {
  try {
    const response = await customFetch(`/hozma/api/preorders-buy/?invoice_no=${invoiceNo}`);
    const data = await response.json();

    console.log("Fetched data:", data);

    const preorders = data.preorders_buy || [];
    const items = data.preorder_items_buy || [];

    if (preorders.length === 0) {
      showAlert('لا يوجد طلب لهذا الرقم.', 'warning');
      return;
    }

    const order = preorders[0];
    currentOrder = order;

    document.getElementById('modalInvoiceNo').textContent = order.invoice_no || 'غير متوفر';
    document.getElementById('modalCustomer').textContent = order.source || 'غير متوفر';
    document.getElementById('modalDate').textContent = order.invoice_date ? new Date(order.invoice_date).toLocaleDateString() : 'غير متوفر';
    document.getElementById('modalNotes').textContent = order.notes || 'لا توجد ملاحظات';
    document.getElementById('modalAmount').textContent = order.net_amount
    document.getElementById('modalAmount').textContent = order.net_amount
      ? Number(order.net_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })
      : '0.00';

    document.getElementById('modalStatus').innerHTML = order.confirmed ?
      '<span class="status-badge status-confirmed">تم التأكيد</span>' :
      '<span class="status-badge status-pending">قيد الانتظار</span>';

    document.getElementById('modalSentStatus').innerHTML = order.send ?
      '<span class="status-badge status-sent">تم الإرسال</span>' :
      '<span class="status-badge status-not-sent">لم يتم الإرسال</span>';

    const itemsBody = document.querySelector('#orderItemsTable');
    itemsBody.innerHTML = '';

    let totalAmount = 0;

    items.forEach(item => {
      const itemTotal = item.dinar_total_price ? parseFloat(item.dinar_total_price) : 0;
      totalAmount += itemTotal;

      const row = document.createElement('tr');
      row.innerHTML = `
            <td>${item.item_no || '--'}</td>
            <td>${item.name || '--'}</td>
            <td>${item.company || '--'}</td>
            <td>${item.confirmed_quantity != null ? item.confirmed_quantity : (item.Asked_quantity || '0')}</td>
<td>${item.cost_unit_price ? Number(item.cost_unit_price).toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'} دينار</td>
<td>${item.cost_total_price ? Number(item.cost_total_price).toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'} دينار</td>

          `;
      itemsBody.appendChild(row);
    });

    document.getElementById('modalTotalAmount').textContent =
      totalAmount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });

    // Update button states based on order status
    const confirmBtn = document.getElementById('confirmBtn');
    const markAsSentBtn = document.getElementById('markAsSentBtn');

    confirmBtn.disabled = order.confirmed;
    confirmBtn.innerHTML = order.confirmed ?
      '<i class="bi bi-check-circle-fill"></i> تم التأكيد' :
      '<i class="bi bi-check-circle"></i> تأكيد الطلب';

    markAsSentBtn.disabled = order.send;
    markAsSentBtn.innerHTML = order.send ?
      '<i class="bi bi-send-check-fill"></i> تم الإرسال' :
      '<i class="bi bi-send"></i> إرسال';

    const modal = new bootstrap.Modal(document.getElementById('orderDetailsModal'));
    modal.show();

  } catch (error) {
    console.error('Error loading order details:', error);
    showAlert('حدث خطأ أثناء تحميل تفاصيل الطلب.', 'danger');
  }
}


async function confirmOrder() {
  if (!currentOrder) return;

  if (!confirm('هل أنت متأكد من تأكيد هذا الطلب؟ لا يمكن التراجع عن هذا الإجراء.')) {
    return;
  }

  try {
    const response = await customFetch('/hozma/api/confirm-or-update-preorder-items-buy-source/', {
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
      showAlert("تم تأكيد الطلب بنجاح!", 'success');

      // Close the modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal'));
      modal.hide();

      // Refresh the preorders list
      fetchOrders(currentPage || 1);
    } else {
      throw new Error(result.message || "فشل في تأكيد الطلب");
    }
  } catch (error) {
    console.error('خطأ في تأكيد الطلب:', error);
    showAlert('فشل في تأكيد الطلب: ' + error.message, 'danger');
  }
}
async function markAsSent() {
  if (!currentOrder) return;

  if (!confirm('هل أنت متأكد من تمييز هذا الطلب كمرسل؟')) {
    return;
  }

  try {
    const response = await customFetch('/hozma/send_unsent_invoices/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        invoice_no: currentOrder.invoice_no,
        sent: true
      })
    });

    const result = await response.json();
    if (response.ok) {
      showAlert("تم تحديث حالة الإرسال بنجاح!", 'success');

      // Close the modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal'));
      modal.hide();

      // Refresh the preorders list
      fetchOrders(currentPage || 1);
    } else {
      throw new Error(result.message || "فشل في تحديث حالة الإرسال");
    }
  } catch (error) {
    console.error('خطأ في تحديث حالة الإرسال:', error);
    showAlert('فشل في تحديث حالة الإرسال: ' + error.message, 'danger');
  }
}

function showAlert(message, type) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.top = '20px';
  alertDiv.style.right = '20px';
  alertDiv.style.zIndex = '9999';
  alertDiv.style.minWidth = '300px';
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;

  document.body.appendChild(alertDiv);

  // Auto dismiss after 5 seconds
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alertDiv);
    bsAlert.close();
  }, 5000);
}
async function downloadPackingList() {
  if (!currentOrder) return;

  try {
    const btn = document.getElementById('downloadPackingListBtn');
    btn.innerHTML = '<i class="bi bi-hourglass"></i> جاري التحميل...';
    btn.disabled = true;

    const response = await customFetch('/hozma/api/download-excel/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        invoice_no: currentOrder.invoice_no
      })
    });

    if (!response.ok) {
      throw new Error("فشل في إنشاء الملف");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `قائمة_تعبئة_${currentOrder.invoice_no}.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();

  } catch (error) {
    console.error('خطأ في تحميل القائمة:', error);
    showAlert('فشل في تحميل القائمة: ' + error.message, 'danger');
  } finally {
    const btn = document.getElementById('downloadPackingListBtn');
    btn.innerHTML = '<i class="bi bi-file-earmark-excel"></i> تنزيل قائمة التعبئة';
    btn.disabled = false;
  }
}

async function downloadInvoice() {
  if (!currentOrder) return;

  try {
    const btn = document.getElementById('downloadInvoiceBtn');
    btn.innerHTML = '<i class="bi bi-hourglass"></i> جاري التحميل...';
    btn.disabled = true;

    const response = await customFetch('/hozma/api/dowmload_excel_for_preorder/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        invoice_no: currentOrder.invoice_no
      })
    });

    if (!response.ok) {
      throw new Error("فشل في إنشاء الفاتورة");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `فاتورة_${currentOrder.invoice_no}.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();

  } catch (error) {
    console.error('خطأ في تحميل الفاتورة:', error);
    showAlert('فشل في تحميل الفاتورة: ' + error.message, 'danger');
  } finally {
    const btn = document.getElementById('downloadInvoiceBtn');
    btn.innerHTML = '<i class="bi bi-file-earmark-excel"></i> تنزيل الفاتورة';
    btn.disabled = false;
  }
}

