const clientId = JSON.parse(localStorage.getItem("session_data@client_id"));
const PLACEHOLDER_IMG = "{% static 'images/parts/default-part.jpg' %}";

const formatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

// Track navigation state
let navigationStack = [];

document.addEventListener('DOMContentLoaded', async () => {
  const invoiceNo = getInvoiceNoFromURL();

  if (window.location.pathname.includes('/orders/') && invoiceNo) {
    // You are deep-linked to a detail view
    navigationStack.push('list');
    navigationStack.push('detail');

    // Push state for list and detail manually
    history.replaceState({ view: 'list' }, '', '/hozma/orders/');
    history.pushState({ view: 'detail' }, '', `/hozma/orders/${invoiceNo}`);

    await loadInvoiceDetails(invoiceNo);
  } else {
    navigationStack.push('list');
    history.replaceState({ view: 'list' }, '', '/hozma/orders/');
    await loadClientInvoices();
  }

  // Handle browser back/forward buttons
  window.addEventListener('popstate', (event) => {
    const view = event.state?.view;

    if (view === 'list') {
      // Show list view
      navigationStack = ['list']; // reset
      showInvoiceListView();
    } else if (view === 'detail') {
      navigationStack = ['list', 'detail'];
      showInvoiceDetailView();
    } else {
      // Unknown or initial state, go back
      window.history.back();
    }
  });

  // Back to list button logic
  document.getElementById('back-to-list-btn').addEventListener('click', () => {
    history.back(); // Triggers popstate
  });
});

function getInvoiceNoFromURL() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 1];
}

function showInvoiceListView() {
  document.getElementById('invoice-list-container').style.display = 'block';
  document.getElementById('invoice-detail-container').style.display = 'none';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showInvoiceDetailView() {
  document.getElementById('invoice-list-container').style.display = 'none';
  document.getElementById('invoice-detail-container').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadClientInvoices() {
  try {
    const res = await customFetch(`/hozma/api/client-preorders/?client_id=${clientId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!res.ok) throw new Error(`API responded ${res.status}`);

    const data = await res.json();
    renderInvoiceList(data);
  } catch (err) {
    console.error('Error fetching invoices:', err);
    document.getElementById('invoice-list-container').innerHTML = `
      <div class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        حدث خطأ أثناء جلب بيانات الفواتير. يرجى المحاولة مرة أخرى.
      </div>
    `;
  }
}

function renderInvoiceList(invoices) {
  if (!invoices || invoices.length === 0) {
    document.getElementById('invoice-list-container').innerHTML = `
      <div class="alert alert-info text-center py-5" style="border-radius: 1rem;">
        <i class="bi bi-info-circle-fill fs-3 mb-3 d-block text-primary"></i>
        <h5 class="mb-3">لا توجد فواتير مسجلة لحسابك</h5>
        <p class="mb-3">ابدأ التسوق الآن واحصل على قطع الغيار التي تحتاجها لسيارتك.</p>
        <a href="/hozma/products/" class="btn btn-primary px-4">
          <i class="bi bi-cart-plus me-1"></i> الذهاب إلى المتجر
        </a>
      </div>
    `;
    return;
  }


  // Sort invoices from newest to oldest by date_time
  invoices.sort((a, b) => new Date(b.date_time) - new Date(a.date_time));

  let html = `
    <div class="invoice-card">
      <div class="invoice-card-header">
        <i class="bi bi-list-ul me-2"></i>قائمة الفواتير
      </div>
      <div class="invoice-card-body">
        <div class="table-responsive">
          <table class="invoice-table table align-middle">
            <thead class="table-light">
              <tr>
                <th>رقم الفاتورة</th>
                <th>التاريخ</th>
                <th>المبلغ</th>
                <th>الحالة</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
  `;

  invoices.forEach(invoice => {
    let statusBadge = '';

    switch (invoice.invoice_status) {
      case "لم تشتري":
        statusBadge = '<span class="badge bg-warning text-dark badge-order-status"><i class="bi bi-hourglass-split me-1"></i>قيد المعالجة</span>';
        break;
      case "تم شراءهن المورد":
        statusBadge = '<span class="badge bg-success badge-order-status"><i class="bi bi-check2-circle me-1"></i>تمت المعالجة</span>';
        break;
      case "جاري التوصيل":
        statusBadge = '<span class="badge bg-primary badge-order-status"><i class="bi bi-box-seam me-1"></i>جاري التوصيل</span>';
        break;
      case "في الطريق":
        statusBadge = '<span class="badge bg-info text-dark badge-order-status"><i class="bi bi-truck me-1"></i>في الطريق</span>';
        break;
      case "تم التوصيل":
        statusBadge = '<span class="badge bg-success badge-order-status"><i class="bi bi-check-lg me-1"></i>تم التوصيل</span>';
        break;
      default:
        statusBadge = `<span class="badge bg-secondary badge-order-status"><i class="bi bi-question-circle me-1"></i>${invoice.invoice_status}</span>`;
    }

    html += `
      <tr class="invoice-list-item" data-invoice-no="${invoice.invoice_no}">
        <td>#${invoice.invoice_no}</td>
        <td>${formatDate(invoice.date_time)}</td>
        <td>${parseFloat(invoice.net_amount).toFixed(2)} د.ل</td>
        <td>${statusBadge}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-primary view-invoice-btn" data-invoice-no="${invoice.invoice_no}">
            <i class="bi bi-eye me-1"></i>عرض التفاصيل
          </button>
        </td>
      </tr>
    `;
  });

  html += `
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  document.getElementById('invoice-list-container').innerHTML = html;

  // Add event listeners to view buttons
  document.querySelectorAll('.view-invoice-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const invoiceNo = btn.dataset.invoiceNo;
      navigationStack.push('detail');
      history.pushState({ view: 'detail' }, '', `/hozma/invoice/${invoiceNo}`);
      loadInvoiceDetails(invoiceNo);
    });
  });
}

// Add event listeners to entire row
document.querySelectorAll('.invoice-list-item').forEach(row => {
  row.addEventListener('click', () => {
    const invoiceNo = row.dataset.invoiceNo;
    // Update navigation stack and history
    navigationStack.push('detail');
    history.pushState({ view: 'detail' }, '', `/hozma/invoice/${invoiceNo}/`);
    loadInvoiceDetails(invoiceNo);

  });
});


async function loadInvoiceDetails(invoiceNo) {
  try {
    const res = await customFetch(`/hozma/api/preorder/${invoiceNo}/?client_id=${clientId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!res.ok) throw new Error(`API responded ${res.status}`);

    const data = await res.json();
    fillInvoice(data);

    // Show detail view
    showInvoiceDetailView();
  } catch (err) {
    console.error('Error fetching invoice details:', err);
    alert('حدث خطأ أثناء جلب تفاصيل الفاتورة. يرجى المحاولة مرة أخرى.');
  }
}

async function fillInvoice(data) {
  const PLACEHOLDER_IMG = '/img/placeholder.png'; // Define your placeholder path
  const baseURL = ''; // Define your backend base URL

  /* —— 1. status badge —— */
  const badge = document.getElementById('order-status-badge');
  let statusBadge = '';

  switch (data.invoice_status) {
    case "لم تشتري":
      statusBadge = '<span class="badge bg-warning text-dark badge-order-status"><i class="bi bi-hourglass-split me-1"></i>قيد المعالجة</span>';
      break;
    case "تم شراءهن المورد":
      statusBadge = '<span class="badge bg-success badge-order-status"><i class="bi bi-check2-circle me-1"></i>تمت المعالجة</span>';
      break;
    case "جاري التوصيل":
      statusBadge = '<span class="badge bg-primary badge-order-status"><i class="bi bi-box-seam me-1"></i>جاري التوصيل</span>';
      break;
    case "في الطريق":
      statusBadge = '<span class="badge bg-info text-dark badge-order-status"><i class="bi bi-truck me-1"></i>في الطريق</span>';
      break;
    case "تم التوصيل":
      statusBadge = '<span class="badge bg-success badge-order-status"><i class="bi bi-check-lg me-1"></i>تم التوصيل</span>';
      break;
    default:
      statusBadge = `<span class="badge bg-secondary badge-order-status"><i class="bi bi-question-circle me-1"></i>${data.invoice_status}</span>`;
      break;
  }

  badge.innerHTML = statusBadge;

  /* —— 2. items table —— */
  const tbody = document.getElementById('invoice-items-tbody');
  tbody.innerHTML = ''; // clear
  let subtotal = 0;

  for (const item of data.preorderitems) {
    const unit = parseFloat(item.dinar_unit_price || 0);
    const originalQty = parseFloat(item.quantity || 0);
    const confirmQty = item.confirm_quantity ? parseFloat(item.confirm_quantity) : null;
    const qty = confirmQty !== null ? confirmQty : originalQty;
    const total = item.dinar_total_price;
    subtotal += total;

    // Get image
    const imageURL = await getProductImageURL(item.pno, PLACEHOLDER_IMG, baseURL);

    // Conditional quantity display
    let quantityHtml = `<td>${qty}</td>`;

    // Modified by shop
    if (confirmQty !== null && confirmQty !== originalQty) {
      quantityHtml = `
        <td>
          <div>
            <span class="text-danger text-decoration-line-through small">${originalQty}</span><br>
            <span class="fw-bold text-dark">${confirmQty}</span><br>
            <span class="badge bg-warning text-dark mt-1">تم تعديل الكمية من المتجر</span>
          </div>
        </td>
      `;
    }

    // Modified by client after shop
    if (
      item.confirmed_delevery_quantity !== null &&
      item.confirmed_delevery_quantity !== undefined &&
      item.confirmed_delevery_quantity !== confirmQty
    ) {
      quantityHtml = `
        <td>
          <div>
            ${confirmQty !== originalQty
          ? `<span class="text-danger text-decoration-line-through small">${originalQty}</span><br>
                 <span class="text-danger text-decoration-line-through small">${confirmQty}</span><br>`
          : `<span class="text-danger text-decoration-line-through small">${originalQty}</span><br>`}
            <span class="fw-bold text-dark">${item.confirmed_delevery_quantity}</span><br>
            <span class="badge bg-info text-dark mt-1">تم تعديل الكمية من العميل</span>
          </div>
        </td>
      `;
    }




    tbody.insertAdjacentHTML('beforeend', `
      <tr>
        <td>
          <div class="d-flex align-items-center">
            <img src="${imageURL}" class="part-img-invoice me-3" alt="part">
            <div>
              <div class="fw-bold">${item.name}</div>
              <div class="text-muted small">رقم القطعة: ${item.pno}</div>
              <div class="text-muted small">الشركة: ${item.company}</div>
              <div class="text-muted small">رقم الاصلي: ${item.item_no}</div>

            </div>
          </div>
        </td>
        <td>${formatter.format(unit)} د.ل</td>
        ${quantityHtml}
        <td>${formatter.format(total)} د.ل</td>
      </tr>
    `);
  }

  /* —— summary rows —— */
  const shipping = data.client.delivery_price || 0;
  const discount = data.client.discount || 0;
  const total = data.net_amount || 0;
  const subtotals = data.amount || 0;
  const discountPercent = (parseFloat(discount) * 100).toFixed(0) + '%';


  tbody.insertAdjacentHTML('beforeend', `
    <tr class="summary-row">
      <td colspan="3" class="text-end">المجموع الجزئي:</td>
      <td>${formatter.format(parseFloat(subtotals))} د.ل</td>
    </tr>
    <tr class="summary-row">
      <td colspan="3" class="text-end">رسوم الشحن:</td>
      <td>${formatter.format(parseFloat(shipping))} د.ل</td>
    </tr>
    <tr class="summary-row">
      <td colspan="3" class="text-end">الخصم:</td>
      <td>${discountPercent} </td>
    </tr>
    <tr class="summary-row summary-row-total">
      <td colspan="3" class="text-end">المجموع الكلي:</td>
      <td>${formatter.format(parseFloat(total))} د.ل</td>
    </tr>
  `);

  /* —— 3. order summary list —— */
  document.getElementById('order-summary-list').innerHTML = `
    <li class="mb-2"><span class="fw-semibold">رقم الطلب:</span> #ORD-${data.invoice_no}</li>
    <li class="mb-2"><span class="fw-semibold">تاريخ الطلب:</span> ${formatDate(data.date_time)}</li>
    <li class="mb-2"><span class="fw-semibold">تاريخ الاستلام:</span> ${formatDate(data.delivery_end_time)}</li>
    <li class="mb-2"><span class="fw-semibold">طريقة الدفع:</span> ${data.payment_status === 'اجل' ? 'الدفع عند الاستلام' : 'بطاقة ائتمان'}</li>
    <li class="mb-2"><span class="fw-semibold">حالة الدفع:</span>
      <span class="${data.payment_status === 'اجل' ? 'text-warning' : 'text-success'}">
        ${data.payment_status === 'اجل' ? 'غير مدفوع' : 'تم الدفع'}
      </span>
    </li>
    <li><span class="fw-semibold">حالة الطلب:</span> ${data.shop_confrim ? 'تمت معالجة الطلب' : 'قيد المعالجة'}</li>
  `;

  /* —— 4. customer details —— */
  document.getElementById('customer-details-list').innerHTML = `
    <li class="mb-2"><span class="fw-semibold">الاسم:</span> ${data.client_name}</li>
    <li class="mb-2"><span class="fw-semibold">البريد الإلكتروني:</span> ${data.client.email || 'غير متوفر'}</li>
    <li class="mb-2"><span class="fw-semibold">رقم الهاتف:</span> ${data.client.phone || data.client.mobile || 'غير متوفر'}</li>
    <li><span class="fw-semibold">العنوان:</span> ${data.client.address || 'غير متوفر'}</li>
  `;

  /* —— 5. shipping details —— */
  document.getElementById('shipping-details-list').innerHTML = `
    <li class="mb-2"><span class="fw-semibold">طريقة الشحن:</span> ${data.shipping_method || 'الشحن السريع'}</li>
    <li class="mb-2"><span class="fw-semibold">عنوان التسليم:</span> ${data.client.address || '—'}</li>
    ${data.client.geo_location ? `
      <li class="mb-2">
        <span class="fw-semibold">الموقع الجغرافي:</span>
        <div class="mt-2">
          <div id="map-container" style="height: 200px; width: 100%; border-radius: 8px; overflow: hidden;">
            <iframe
              width="100%"
              height="100%"
              frameborder="0"
              scrolling="no"
              marginheight="0"
              marginwidth="0"
              src="https://maps.google.com/maps?q=${data.client.geo_location}&z=15&output=embed">
            </iframe>
          </div>
          <small class="text-muted d-block mt-1">يمكنك النقر على الخريطة للتكبير</small>
        </div>
      </li>
    ` : ''}
  `;
}



async function getProductImageURL(pno, placeholder, baseURL) {
  try {
    const response = await fetch(`/hozma/api/products/${pno}/get-images`);
    const images = await response.json();
    if (images.length > 0 && images[0].image_obj) {
      return `${baseURL}${images[0].image_obj}`;
    }
  } catch (err) {
    console.warn(`Image fetch failed for PNO: ${pno}`, err);
  }
  return placeholder;
}


function printInvoice() {
  try {
    // Get order number from the page
    const invoiceNoElem = document.querySelector('#order-summary-list li:nth-child(1)');
    const invoiceNo = invoiceNoElem ? invoiceNoElem.textContent.split(':')[1].trim() : 'N/A';

    // Get order date from the page
    const orderDateElem = document.querySelector('#order-summary-list li:nth-child(2)');
    const orderDate = orderDateElem ? orderDateElem.textContent.split(':')[1].trim() : new Date().toLocaleDateString('ar-LY');

    // Get client details
    const clientNameElem = document.querySelector('#customer-details-list li:nth-child(1)');
    const clientName = clientNameElem ? clientNameElem.textContent.split(':')[1].trim() : 'N/A';

    const phoneElem = document.querySelector('#customer-details-list li:nth-child(3)');
    const phone = phoneElem ? phoneElem.textContent.split(':')[1].trim() : 'N/A';

    const addressElem = document.querySelector('#customer-details-list li:nth-child(4)');
    const address = addressElem ? addressElem.textContent.split(':')[1].trim() : 'N/A';

    // Get payment method and status
    const paymentMethodElem = document.querySelector('#order-summary-list li:nth-child(4)');
    const paymentMethod = paymentMethodElem ? paymentMethodElem.textContent.split(':')[1].trim() : 'N/A';

    const paymentStatusElem = document.querySelector('#order-summary-list li:nth-child(5)');
    const paymentStatus = paymentStatusElem ? paymentStatusElem.textContent.split(':')[1].trim() : 'N/A';

    // Get order status from badge
    const orderStatusBadge = document.querySelector('#order-status-badge .badge');
    const orderStatus = orderStatusBadge ? orderStatusBadge.textContent.trim() : 'N/A';

    // Get items data with proper quantity display
    const items = [];
    const itemRows = document.querySelectorAll('#invoice-items-tbody tr:not(.summary-row)');

    itemRows.forEach(row => {
      try {
        const cells = row.querySelectorAll('td');
        if (cells.length < 4) return;

        // 1. Product Info Cell
        const productCell = cells[0];
        const productText = productCell.textContent;

        // Extract product name (first line that doesn't contain metadata)
        const name = productText.split('\n')
          .find(line => line.trim() &&
            !line.includes('رقم القطعة') &&
            !line.includes('الشركة') &&
            !line.includes('رقم الاصلي'))
          ?.trim() || 'N/A';

        // Extract part number
        const pnoMatch = productText.match(/رقم القطعة:\s*([^\n]+)/);
        const pno = pnoMatch ? pnoMatch[1].trim() : 'N/A';

        // Extract company
        const companyMatch = productText.match(/الشركة:\s*([^\n]+)/);
        const company = companyMatch ? companyMatch[1].trim() : 'N/A';

        // Extract original part number - THIS IS THE CRUCIAL FIX
        const itemNoMatch = productText.match(/رقم الاصلي:\s*([^\n]+)/);
        const itemNo = itemNoMatch ? itemNoMatch[1].trim() : '';

        // 2. Price Cell
        const price = cells[1]?.textContent.trim() || '0.00 د.ل';

        // 3. Quantity Cell - handle modifications
        const qtyCell = cells[2];
        let qtyDisplay = '0';
        let modificationType = '';

        // Check for modification badges
        const modificationBadge = qtyCell.querySelector('.badge');
        if (modificationBadge) {
          modificationType = modificationBadge.textContent.trim();
          const quantityValues = Array.from(qtyCell.querySelectorAll('span:not(.badge), div > span'))
            .map(el => el.textContent.trim())
            .filter(text => /^\d+$/.test(text));

          const originalQty = quantityValues[0] || '0';
          const modifiedQty = quantityValues[1] || originalQty;

          if (modificationType.includes('المتجر')) {
            qtyDisplay = `
              <div>
                <span style="color: #dc3545; text-decoration: line-through;">${originalQty}</span><br>
                <strong style="color: #28a745;">${modifiedQty}</strong><br>
                <span class="badge bg-warning text-dark">${modificationType}</span>
              </div>
            `;
          } else if (modificationType.includes('العميل')) {
            const clientModifiedQty = quantityValues[2] || modifiedQty;
            qtyDisplay = `
              <div>
                <span style="color: #dc3545; text-decoration: line-through;">${originalQty}</span><br>
                ${modifiedQty !== originalQty ?
                `<span style="color: #dc3545; text-decoration: line-through;">${modifiedQty}</span><br>` : ''}
                <strong style="color: #28a745;">${clientModifiedQty}</strong><br>
                <span class="badge bg-info text-dark">${modificationType}</span>
              </div>
            `;
          }
        } else {
          qtyDisplay = qtyCell.textContent.trim() || '0';
        }

        // 4. Total Cell
        const total = cells[3]?.textContent.trim() || '0.00 د.ل';

        // ALWAYS include original part number if it exists in the source
        const additionalInfo = itemNo ?
          `<br><small class="text-muted">رقم الأصلي: ${itemNo}</small>` : '';

        items.push({
          name,
          pno,
          company,
          price,
          qty: qtyDisplay,
          total,
          additionalInfo,
          itemNo // Store separately for reference
        });

      } catch (e) {
        console.error('Error processing item row:', e);
        items.push({
          name: 'N/A',
          pno: 'N/A',
          company: 'N/A',
          price: '0.00 د.ل',
          qty: '0',
          total: '0.00 د.ل',
          additionalInfo: '',
          itemNo: ''
        });
      }
    });

    // Get summary data
    const summaryRows = document.querySelectorAll('#invoice-items-tbody tr.summary-row');
    const subtotal = summaryRows[0]?.querySelector('td:last-child')?.textContent.trim() || '0.00 د.ل';
    const shipping = summaryRows[1]?.querySelector('td:last-child')?.textContent.trim() || '0.00 د.ل';
    const discount = summaryRows[2]?.querySelector('td:last-child')?.textContent.trim() || '0%';
    const grandTotal = document.querySelector('#invoice-items-tbody tr.summary-row-total td:last-child')?.textContent.trim() || '0.00 د.ل';

    // Generate QR code for invoice reference
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(`Invoice: ${invoiceNo}\nClient: ${clientName}\nTotal: ${grandTotal}`)}`;

    // Create print window
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('يُرجى السماح بالنوافذ المنبثقة لطباعة الفاتورة');
      return;
    }

    printWindow.document.write(`
      <!DOCTYPE html>
      <html dir="rtl" lang="ar">
      <head>
        <meta charset="UTF-8">
        <title>فاتورة #${invoiceNo}</title>
        <style>
          @font-face {
            font-family: 'Tajawal';
            src: url('{% static "fonts/Tajawal-Regular.ttf" %}') format('truetype');
          }

          body {
            font-family: 'Tajawal', 'Arial', sans-serif;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
          }

          .invoice-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 1000px;
            margin: 0 auto;
          }

          .invoice-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
            position: relative;
          }

          .logo {
            height: 80px;
            margin-bottom: 15px;
          }

          .invoice-header h1 {
            margin: 0;
            font-size: 28px;
            color: #0F1B2E;
            font-weight: 700;
          }

          .invoice-header p {
            margin-top: 5px;
            color: #666;
          }

          .invoice-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 20px;
          }

          .info-block {
            flex: 1;
            min-width: 250px;
            background: #f5f7fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #0F1B2E;
          }

          .info-block h3 {
            margin-top: 0;
            color: #0F1B2E;
            font-size: 18px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
          }

          .info-block p {
            margin: 8px 0;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
          }

          th {
            background-color: #0F1B2E;
            color: white;
            padding: 12px;
            text-align: right;
          }

          td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: right;
            vertical-align: top;
          }

          tr:nth-child(even) {
            background-color: #f9f9f9;
          }

          .summary-table {
            width: 300px;
            margin-left: auto;
            margin-top: 30px;
            float: left;
          }

          .summary-table td {
            padding: 12px 15px;
          }

          .total-row {
            font-weight: bold;
            font-size: 1.1em;
            background-color: #f5f7fa;
          }

          .footer {
            margin-top: 50px;
            text-align: center;
            font-style: italic;
            color: #666;
            border-top: 1px solid #eee;
            padding-top: 20px;
            clear: both;
          }

          .qr-code {
            float: left;
            margin-top: 30px;
            text-align: center;
            width: 150px;
          }

          .qr-code img {
            width: 120px;
            height: 120px;
            border: 1px solid #ddd;
            padding: 5px;
            background: white;
          }

          .qr-code p {
            margin-top: 5px;
            font-size: 12px;
          }

          .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-left: 10px;
          }

          .status-processing {
            background-color: #ffc107;
            color: #000;
          }

          .status-completed {
            background-color: #28a745;
            color: white;
          }

          .status-delivered {
            background-color: #17a2b8;
            color: white;
          }

          .status-pending {
            background-color: #6c757d;
            color: white;
          }

          @media print {
            body {
              padding: 0;
              background: white;
            }

            .invoice-container {
              box-shadow: none;
              padding: 0;
            }

            .no-print {
              display: none !important;
            }

            .logo {
              height: 70px;
            }
          }
        </style>
      </head>
      <body>
        <div class="invoice-container">
          <div class="invoice-header">
            <img src="{% static 'images/log_hozma.png' %}" alt="Company Logo" class="logo">
            <h1>فاتورة بيع</h1>
            <p>متجر حزمة لقطع غيار السيارات | هاتف: 0914262604</p>
          </div>

          <div class="invoice-info">
            <div class="info-block">
              <h3>معلومات الفاتورة</h3>
              <p><strong>رقم الفاتورة:</strong> #${invoiceNo}</p>
              <p><strong>تاريخ الطلب:</strong> ${orderDate}</p>
              <p><strong>حالة الطلب:</strong>
                <span class="status-badge ${orderStatus.includes('تمت') ? 'status-completed' :
        orderStatus.includes('جاري') ? 'status-processing' :
          orderStatus.includes('تم') ? 'status-delivered' : 'status-pending'}">
                  ${orderStatus}
                </span>
              </p>
            </div>

            <div class="info-block">
              <h3>معلومات العميل</h3>
              <p><strong>اسم العميل:</strong> ${clientName}</p>
              <p><strong>رقم الهاتف:</strong> ${phone}</p>
              <p><strong>العنوان:</strong> ${address || '—'}</p>
            </div>

            <div class="info-block">
              <h3>معلومات الدفع</h3>
              <p><strong>طريقة الدفع:</strong> ${paymentMethod}</p>
              <p><strong>حالة الدفع:</strong>
                <span style="color: ${paymentStatus.includes('تم') ? '#28a745' : '#dc3545'}; font-weight: bold;">
                  ${paymentStatus}
                </span>
              </p>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th>القطعة</th>
                <th>السعر</th>
                <th>الكمية</th>
                <th>المجموع</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(item => `
                <tr>
                  <td>
                    <div>
                      <strong>${item.name}</strong><br>
                      <small style="color: #6c757d;">رقم القطعة: ${item.pno}</small><br>
                      <small style="color: #6c757d;">الشركة: ${item.company}</small>
                      ${item.additionalInfo}
                    </div>
                  </td>
                  <td>${item.price}</td>
                  <td>${item.qty}</td>
                  <td>${item.total}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div class="qr-code">
            <img src="${qrCodeUrl}" alt="Invoice QR Code">
            <p>مرجع الفاتورة</p>
          </div>

          <table class="summary-table">
            <tr>
              <td><strong>المجموع الجزئي:</strong></td>
              <td>${subtotal}</td>
            </tr>
            <tr>
              <td><strong>رسوم الشحن:</strong></td>
              <td>${shipping}</td>
            </tr>
            <tr>
              <td><strong>الخصم:</strong></td>
              <td>${discount}</td>
            </tr>
            <tr class="total-row">
              <td><strong>المجموع الكلي:</strong></td>
              <td style="color: #28a745; font-size: 1.2em;">${grandTotal}</td>
            </tr>
          </table>

          <div class="footer">
            <p>شكراً لثقتكم بنا - نرحب باستفساراتكم في أي وقت</p>
            <p>هاتف: 0914262604 | البريد الإلكتروني: info@hozma.com</p>
            <p>جميع الحقوق محفوظة © متجر حزمة ${new Date().getFullYear()}</p>
          </div>
        </div>

        <script>
          window.onload = function() {
            setTimeout(function() {
              window.print();
              setTimeout(function() {
                window.close();
              }, 500);
            }, 200);
          };
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();

  } catch (error) {
    console.error('Error in printInvoice:', error);
    alert('حدث خطأ أثناء محاولة طباعة الفاتورة. يُرجى المحاولة مرة أخرى.');
  }
}
/* helper: format ISO date to Arabic locale */
function formatDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('ar-LY', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch { return iso; }
}