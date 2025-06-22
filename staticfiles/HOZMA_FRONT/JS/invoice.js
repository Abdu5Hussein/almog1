const clientId = JSON.parse(localStorage.getItem("session_data@client_id"));
/* =============== helpers =============== */
const PLACEHOLDER_IMG = "{% static 'images/parts/default-part.jpg' %}";

/** extract the first numeric segment from the current URL */
const getInvoiceNoFromUrl = () => {
  return window.location.pathname.split('/').find(seg => /^\d+$/.test(seg)) || null;
};

const formatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/* =============== main =============== */
document.addEventListener('DOMContentLoaded', async () => {
  const invoiceNo = getInvoiceNoFromUrl();
  if (!invoiceNo) return console.error('Invoice number not found in URL.');

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
  } catch (err) {
    console.error('Error fetching invoice:', err);
  }
});

async function fillInvoice(data) {
  const PLACEHOLDER_IMG = '/img/placeholder.png'; // Define your placeholder path
  const baseURL = 'http://45.13.59.226'; // Define your backend base URL

  /* —— 1. status badge —— */
  const badge = document.getElementById('order-status-badge');
  const statusMap = {
    false: { label: 'قيد المعالجة', class: 'bg-warning' },
    true: { label: 'مكتمل', class: 'bg-success' }
  };
  const mapping = statusMap[data.shop_confrim] || { label: 'غير معروف', class: 'bg-secondary' };
  badge.textContent = mapping.label;
  badge.className = `badge badge-order-status ${mapping.class}`;

  /* —— 2. items table —— */
  const tbody = document.getElementById('invoice-items-tbody');
  tbody.innerHTML = ''; // clear
  let subtotal = 0;

  for (const item of data.preorderitems) {
    const unit = parseFloat(item.dinar_unit_price || 0);
    const originalQty = parseFloat(item.quantity || 0);
    const confirmQty = item.confirm_quantity ? parseFloat(item.confirm_quantity) : null;
    const qty = confirmQty !== null ? confirmQty : originalQty;
    const total = item.dinar_total_price ;
    subtotal += total;

    // Get image
    const imageURL = await getProductImageURL(item.pno, PLACEHOLDER_IMG, baseURL);

    // Conditional quantity display
    let quantityHtml = `<td>${qty}</td>`;

// Check if Confirm Qty is different from Original
if (confirmQty !== null && confirmQty !== originalQty) {
  let htmlContent = `
    <div>
      <span class="text-muted text-decoration-line-through small">${originalQty}</span><br>
      <span class="fw-bold text-dark">${confirmQty}</span><br>
      <span class="badge bg-warning text-dark mt-1">تم تعديل الكمية من المتجر</span>
    </div>
  `;

  // Check if Confirmed Delivery Qty exists and is different from Confirm Qty
  if (item.confirmed_delevery_quantity !== null &&
      item.confirmed_delevery_quantity !== undefined &&
      item.confirmed_delevery_quantity !== confirmQty) {

    htmlContent = `
      <div>
        <span class="text-muted text-decoration-line-through small">${originalQty}</span><br>
        <span class="text-muted text-decoration-line-through small">${confirmQty}</span><br>
        <span class="fw-bold text-dark">${item.confirmed_delevery_quantity}</span><br>
        <span class="badge bg-info text-dark mt-1">تم تعديل الكمية من العميل</span>
      </div>
    `;
  }

  quantityHtml = `<td>${htmlContent}</td>`;
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
              <div class="text-muted small">الشركة: ${item.oem_numbers}</div>

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
      <td>${formatter.format(parseFloat(discount))} د.ل</td>
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
    // Get order number from the page (corrected selector)
    const invoiceNoElem = document.querySelector('#order-summary-list li:nth-child(1)');
    const invoiceNo = invoiceNoElem ? invoiceNoElem.textContent.split(':')[1].trim() : 'N/A';

    // Get order date from the page (corrected selector)
    const orderDateElem = document.querySelector('#order-summary-list li:nth-child(2)');
    const orderDate = orderDateElem ? orderDateElem.textContent.split(':')[1].trim() : new Date().toLocaleDateString('ar-LY');

    // Get client details (corrected selectors)
    const clientNameElem = document.querySelector('#customer-details-list li:nth-child(1)');
    const clientName = clientNameElem ? clientNameElem.textContent.split(':')[1].trim() : 'N/A';

    const phoneElem = document.querySelector('#customer-details-list li:nth-child(3)');
    const phone = phoneElem ? phoneElem.textContent.split(':')[1].trim() : 'N/A';

    const addressElem = document.querySelector('#customer-details-list li:nth-child(4)');
    const address = addressElem ? addressElem.textContent.split(':')[1].trim() : 'N/A';

    // Get payment method (added this)
    const paymentMethodElem = document.querySelector('#order-summary-list li:nth-child(3)');
    const paymentMethod = paymentMethodElem ? paymentMethodElem.textContent.split(':')[1].trim() : 'N/A';

    // Get order status (added this)
    const orderStatusElem = document.querySelector('#order-summary-list li:nth-child(5)');
    const orderStatus = orderStatusElem ? orderStatusElem.textContent.split(':')[1].trim() : 'N/A';

    // Get items data
    const items = [];
    const itemRows = document.querySelectorAll('#invoice-items-tbody tr:not(.summary-row)');
    
    itemRows.forEach(row => {
        try {
            const name = row.querySelector('td div div.fw-bold')?.textContent || 'N/A';
            const pno = row.querySelector('td div div.small:nth-of-type(1)')?.textContent.replace('رقم القطعة:', '').trim() || 'N/A';
            const company = row.querySelector('td div div.small:nth-of-type(2)')?.textContent.replace('منشأ:', '').trim() || 'N/A';
            const price = row.querySelector('td:nth-child(2)')?.textContent.trim() || '0.00 د.ل';
            const qty = row.querySelector('td:nth-child(3)')?.textContent.trim() || '0';
            const total = row.querySelector('td:nth-child(4)')?.textContent.trim() || '0.00 د.ل';
            
            items.push({ name, pno, company, price, qty, total });
        } catch (e) {
            console.error('Error processing item row:', e);
        }
    });

    // Get summary data (corrected selectors)
    const summaryRows = document.querySelectorAll('#invoice-items-tbody tr.summary-row');
    const subtotal = summaryRows[0]?.querySelector('td:last-child')?.textContent.trim() || '0.00 د.ل';
    const shipping = summaryRows[1]?.querySelector('td:last-child')?.textContent.trim() || '0.00 د.ل';
    const discount = summaryRows[2]?.querySelector('td:last-child')?.textContent.trim() || '0.00 د.ل';
    const grandTotal = document.querySelector('#invoice-items-tbody tr.summary-row-total td:last-child')?.textContent.trim() || '0.00 د.ل';

    // Generate items HTML
    const itemsHtml = items.map(item => `
        <tr>
            <td>
                <div>
                    <strong>${item.name}</strong><br>
                    <small>رقم القطعة: ${item.pno}</small><br>
                    <small>الشركة: ${item.company}</small>
                </div>
            </td>
            <td>${item.price}</td>
            <td>${item.qty}</td>
            <td>${item.total}</td>
        </tr>
    `).join('');

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
                body { 
                    font-family: 'Arial', sans-serif; 
                    padding: 20px; 
                    line-height: 1.6;
                    color: #333;
                }
                .invoice-header { 
                    text-align: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 10px; 
                    border-bottom: 2px solid #000; 
                }
                .invoice-header h1 { 
                    margin: 0; 
                    font-size: 28px;
                    color: #0F1B2E;
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
                }
                .info-block { 
                    width: 48%; 
                    margin-bottom: 15px;
                }
                .info-block p {
                    margin: 5px 0;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0; 
                    font-size: 14px;
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 10px; 
                    text-align: right; 
                }
                th { 
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
                .summary-table { 
                    width: 50%; 
                    margin-left: auto; 
                    margin-top: 30px;
                }
                .total-row { 
                    font-weight: bold; 
                    font-size: 1.1em; 
                    background-color: #f9f9f9;
                }
                .footer {
                    margin-top: 50px;
                    text-align: center;
                    font-style: italic;
                    color: #666;
                    border-top: 1px solid #eee;
                    padding-top: 15px;
                }
                @media print {
                    body { 
                        padding: 0; 
                        font-size: 12px;
                    }
                    .no-print { 
                        display: none !important; 
                    }
                    .invoice-header {
                        margin-top: 0;
                    }
                }
            </style>
        </head>
        <body>
            <div class="invoice-header">
                <h1>فاتورة بيع</h1>
                <p>متجر حزمة لقطع غيار السيارات</p>
            </div>
            
            <div class="invoice-info">
                <div class="info-block">
                    <p><strong>رقم الفاتورة:</strong> ${invoiceNo}</p>
                    <p><strong>تاريخ الطلب:</strong> ${orderDate}</p>
                    <p><strong>طريقة الدفع:</strong> ${paymentMethod}</p>
                </div>
                <div class="info-block">
                    <p><strong>اسم العميل:</strong> ${clientName}</p>
                    <p><strong>رقم الهاتف:</strong> ${phone}</p>
                    <p><strong>حالة الطلب:</strong> ${orderStatus}</p>
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
                    ${itemsHtml}
                </tbody>
            </table>
            
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
                    <td>${grandTotal}</td>
                </tr>
            </table>
            
            <div class="footer">
                <p>شكراً لثقتكم بنا</p>
                <p>للاستفسار: 0914262604 | البريد الإلكتروني: info@marin.com</p>
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
            <\/script>
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
    return d.toLocaleDateString('ar-LY', {year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'});
  } catch { return iso; }
}
