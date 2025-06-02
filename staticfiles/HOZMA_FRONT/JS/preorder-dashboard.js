
/* ------------------------------------------------------------------
   GLOBAL STATE
------------------------------------------------------------------ */
let currentPage   = 1;
let totalPages    = 1;
let lastPayload   = {};           // remember the last POST body so we can re-use it
let preorderCache = [];           // the page we just fetched

/* ------------------------------------------------------------------
   DOM REFERENCES
------------------------------------------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
    const sortSelect         = document.getElementById('sortSelect');
    const statusFilter       = document.getElementById('statusFilter');
    const dateFilter         = document.getElementById('dateFilter');
    const preorderList       = document.getElementById('preorder-list');
    const loadingState       = document.getElementById('loading-state');
    const emptyState         = document.getElementById('empty-state');
    const refreshBtn         = document.getElementById('refresh-btn');
    const resetFiltersBtn    = document.getElementById('reset-filters');
    const nextBtn            = document.getElementById('next-page');
    const prevBtn            = document.getElementById('prev-page');
    const pageLabel          = document.getElementById('page-label');

    /* ---------------- initial load ---------------- */
    fetchPreorders();        // page 1 with default filters

    /* ---------------- UI events ------------------- */
    [sortSelect, statusFilter, dateFilter].forEach(el => {
        el.addEventListener('change', () => fetchPreorders(1));     // go back to first page
    });

    refreshBtn.addEventListener('click', function() {
        this.querySelector('i').classList.add('refresh-animate');
        fetchPreorders(currentPage);
        setTimeout(() => {
            this.querySelector('i').classList.remove('refresh-animate');
        }, 800);
    });
    
    resetFiltersBtn.addEventListener('click', () => {
        sortSelect.value   = 'date_desc';
        statusFilter.value = 'all';
        dateFilter.value   = 'all';
        fetchPreorders(1);
    });

    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) fetchPreorders(currentPage + 1);
    });

    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) fetchPreorders(currentPage - 1);
    });

    /* ---------------------------------------------------------------
       MAIN FETCHER –– builds POST body from the three dropdowns
    ----------------------------------------------------------------*/
    function fetchPreorders(page = 1) {
        /* show loading */
        loadingState.style.display = '';
        emptyState.style.display   = 'none';
        preorderList.innerHTML     = '';
        preorderList.appendChild(loadingState);

        /* build payload */
        const payload = {
            page:        page,
            page_size:   10,                          // change if you want a different page size
            sort_by:     sortSelect.value,            // date_desc, amount_asc, …
            status_filter: statusFilter.value,        // all | confirmed | pending
            date_filter:   dateFilter.value           // all | today | week | month
        };

        /* remember it so "refresh" keeps last filters */
        lastPayload = payload;

        customFetch('http://45.13.59.226/hozma/api/preorders_v2/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            preorderCache = data.preorders || [];
            currentPage   = data.pagination.current_page;
            totalPages    = data.pagination.total_pages;

            /* summary cards & counts --------------------------------*/
            updateSummaryCards(data.summary);
            document.getElementById('showing-count').textContent = preorderCache.length;
            document.getElementById('total-count').textContent   = data.summary.total_orders;

            /* table + pagination UI --------------------------------*/
            renderTable(preorderCache);
            updatePaginationControls();

            /* empty / loading states -------------------------------*/
            loadingState.style.display = 'none';
            emptyState.style.display   = preorderCache.length ? 'none' : 'block';
        })
        .catch(err => {
            console.error('خطأ في جلب الطلبات المسبقة:', err);
            loadingState.innerHTML = `
               <td colspan="7" class="text-center py-4 text-danger">
                 <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                 <p>فشل تحميل الطلبات المسبقة. الرجاء المحاولة لاحقاً.</p>
                 <button class="btn btn-sm btn-primary action-btn" onclick="window.location.reload()">
                     <i class="fas fa-sync-alt me-1"></i> إعادة المحاولة
                 </button>
               </td>`;
        });
    }

    /* ----------------------------------------------------------------
       PAGINATION FOOTER (enable/disable & label)
    -----------------------------------------------------------------*/
    function updatePaginationControls() {
        nextBtn.disabled = currentPage >= totalPages;
        prevBtn.disabled = currentPage <= 1;
        pageLabel.textContent = `${currentPage} / ${totalPages}`;
        
        // Add/remove classes based on state
        if (nextBtn.disabled) {
            nextBtn.classList.add('disabled');
        } else {
            nextBtn.classList.remove('disabled');
        }
        
        if (prevBtn.disabled) {
            prevBtn.classList.add('disabled');
        } else {
            prevBtn.classList.remove('disabled');
        }
    }

    /* ----------------------------------------------------------------
       SUMMARY CARDS  –– uses `summary` block from backend
    -----------------------------------------------------------------*/
    function updateSummaryCards(summary) {
        document.getElementById('total-orders').textContent     = summary.total_orders;
        document.getElementById('orders-change').textContent    = '';   // remove hard-coded %
        document.getElementById('confirmed-orders').textContent = summary.confirmed_orders;
        document.getElementById('confirmed-change').textContent = '';
        document.getElementById('pending-orders').textContent   = summary.pending_orders;
        document.getElementById('pending-change').textContent   = '';
    }
});   // DOMContentLoaded end

/* ------------------------------------------------------------------
   RENDER FUNCTIONS
------------------------------------------------------------------*/
function renderTable(preorders) {
    const preorderList = document.getElementById('preorder-list');
    preorderList.innerHTML = '';

    preorders.forEach(preorder => {
        const row = document.createElement('tr');
        row.className = 'align-middle';

        /* Arabic date formatting --------------------- */
        const date   = new Date(preorder.date_time);
        const formattedDate = date.toLocaleDateString('en-UK', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });

        row.innerHTML = `
          <td>
              <span class="fw-bold d-flex align-items-center">
                  <i class="fas fa-receipt me-2 text-primary"></i>
                  ${preorder.invoice_no}
              </span>
          </td>
          <td>
              <span class="badge bg-success rounded-pill d-inline-flex align-items-center">
                  <i class="fas fa-dollar-sign me-1"></i>
                  ${parseFloat(preorder.amount).toFixed(2)}
              </span>
          </td>
          <td>
              <span class="status-badge ${getPaymentStatusClass(preorder.payment_status)}">
                  <i class="fas ${getPaymentStatusIcon(preorder.payment_status)}"></i>
                  ${preorder.payment_status || 'غير محدد'}
              </span>
          </td>
          <td>
              <span class="status-badge ${getInvoiceStatusClass(preorder.invoice_status)}">
                  <i class="fas ${getInvoiceStatusIcon(preorder.invoice_status)}"></i>
                  ${preorder.invoice_status || 'غير محدد'}
              </span>
          </td>
          <td>
              ${preorder.shop_confrim
                  ? '<span class="badge bg-success rounded-pill d-inline-flex align-items-center"><i class="fas fa-check-circle me-1"></i> تم التأكيد</span>'
                  : '<span class="badge bg-warning rounded-pill d-inline-flex align-items-center"><i class="fas fa-clock me-1"></i> قيد الانتظار</span>'
              }
          </td>
          <td>
              <small class="text-muted d-flex align-items-center">
                  <i class="far fa-calendar-alt me-2"></i>
                  ${formattedDate}
              </small>
          </td>
          <td>
              <button class="btn btn-sm btn-primary action-btn" onclick="viewPreOrderItems('${preorder.invoice_no}')">
                  <i class="fas fa-eye me-1"></i> عرض التفاصيل
              </button>
          </td>`;
        preorderList.appendChild(row);
    });
}

/* ------------------------------------------------------------------
   STATUS HELPERS
------------------------------------------------------------------*/
function getPaymentStatusClass(status) {
    if (!status) return 'bg-secondary';
    status = status.toLowerCase();
    if (status.includes('تم') || status.includes('اكتمل')) return 'bg-success';
    if (status.includes('انتظار') || status.includes('قيد')) return 'bg-warning text-dark';
    if (status.includes('فشل') || status.includes('رفض')) return 'bg-danger';
    return 'bg-info';
}

function getPaymentStatusIcon(status) {
    if (!status) return 'fa-question-circle';
    status = status.toLowerCase();
    if (status.includes('تم') || status.includes('اكتمل')) return 'fa-check-circle';
    if (status.includes('انتظار') || status.includes('قيد')) return 'fa-clock';
    if (status.includes('فشل') || status.includes('رفض')) return 'fa-times-circle';
    return 'fa-info-circle';
}

function getInvoiceStatusClass(status) {
    if (!status) return 'bg-secondary';
    status = status.toLowerCase();
    if (status.includes('تم') || status.includes('اكتمل')) return 'bg-success';
    if (status.includes('انتظار') || status.includes('قيد')) return 'bg-warning text-dark';
    if (status.includes('فشل') || status.includes('رفض')) return 'bg-danger';
    if (status.includes('شحن') || status.includes('توصيل')) return 'bg-primary';
    return 'bg-info';
}

function getInvoiceStatusIcon(status) {
    if (!status) return 'fa-question-circle';
    status = status.toLowerCase();
    if (status.includes('تم') || status.includes('اكتمل')) return 'fa-check-circle';
    if (status.includes('انتظار') || status.includes('قيد')) return 'fa-clock';
    if (status.includes('فشل') || status.includes('رفض')) return 'fa-times-circle';
    if (status.includes('شحن') || status.includes('توصيل')) return 'fa-truck';
    return 'fa-info-circle';
}

/* ------------------------------------------------------------------
   NAVIGATE TO DETAILS
------------------------------------------------------------------*/
function viewPreOrderItems(invoice_no) {
    window.location.href = `/hozma/preorder-detail/${invoice_no}/`;
}