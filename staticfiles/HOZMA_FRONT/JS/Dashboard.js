document.addEventListener('DOMContentLoaded', function() {
    // Retrieve customer data from localStorage
    const customerId = JSON.parse(localStorage.getItem("session_data@client_id"));
    
    if (customerId) {
        const customerIdNumber = customerId.replace(/^c-/, '');
        fetchCustomerDetails(customerIdNumber);
        fetchOrderHistory(customerIdNumber);
    } else {
        window.location.href = "/login";
    }
});

function fetchCustomerDetails(customerId) {
    customFetch(`/hozma/api/clients/${customerId}/`)
        .then(response => response.json())
        .then(data => {
            if (!data || !data.clients || data.clients.length === 0) {
                console.error("No client data found.");
                return;
            }

            const client = data.clients[0];
            displayClientData(client);
        })
        .catch(error => {
            console.error('Error fetching client data:', error);
        });
}

function displayClientData(clientData) {
    document.getElementById('customerName').textContent = clientData.name || 'زائر';
    document.getElementById('clientName').textContent = clientData.name || 'غير متوفر';
    document.getElementById('clientEmail').textContent = clientData.email || 'غير متوفر';
    document.getElementById('clientPhone').textContent = clientData.phone || 'غير متوفر';
    document.getElementById('clientAddress').textContent = clientData.address || 'غير متوفر';
}

function fetchOrderHistory(customerId) {
    customFetch(`/hozma/api/client-preorders/?client_id=${customerId}`)
        .then(response => response.json())
        .then(invoices => {
            const orderHistoryDiv = document.querySelector('#orderHistory tbody');
            
            if (!invoices || invoices.length === 0) {
                orderHistoryDiv.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-4">
                            <div class="alert alert-info" role="alert">
                                <h5 class="mb-3">لا توجد لديك أي طلبات سابقة</h5>
                                <p class="mb-3">ابدأ التسوق الآن واختر قطع الغيار المناسبة لسيارتك.</p>
                                <a href="/hozma/products/" class="btn btn-primary">
                                    <i class="fas fa-shopping-cart me-1"></i> انتقل إلى المتجر
                                </a>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }
            

            invoices.sort((a, b) => b.autoid - a.autoid);
            const recentInvoices = invoices.slice(0, 5);
            
            let html = '';
            recentInvoices.forEach(invoice => {
                const statusClass = getStatusClass(invoice.invoice_status);
                const statusBadge = (invoice.invoice_status === "لم تشتري")
  ? '<span class="badge bg-warning badge-order-status">قيد المعالجة</span>'
  : (invoice.invoice_status === "تم شراءهن المورد")
    ? '<span class="badge bg-success badge-order-status">جاري التحضير</span>'
    : `<span class="badge bg-secondary badge-order-status">${invoice.invoice_status}</span>`;

                html += `
<tr>
<td>#${invoice.invoice_no}</td>
<td>${new Date(invoice.date_time).toLocaleDateString('ar-LY')}</td>
<td>${parseFloat(invoice.net_amount).toFixed(2)} د.ل</td>
 <td>${statusBadge}</td>
<td>
    <button class="view-details-btn" onclick="viewOrderDetails('${invoice.invoice_no}')">
        <i class="fas fa-eye me-1"></i>التفاصيل
    </button>
</td>
</tr>
`;

            });
            
            orderHistoryDiv.innerHTML = html;
        })
        .catch(error => {
            console.error('Error fetching invoice history:', error);
            document.querySelector('#orderHistory tbody').innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4 text-danger">حدث خطأ أثناء تحميل سجل الفواتير</td>
                </tr>
            `;
        });
}

function getStatusClass(status) {
    if (status.includes('مكتمل') || status.includes('تم التوصيل')) {
        return 'status-completed';
    } else if (status.includes('قيد') || status.includes('معالجة')) {
        return 'status-processing';
    } else {
        return 'status-pending';
    }
}

function editProfile() {
    window.location.href = "/hozma/profile/edit";
}

function viewOrderDetails(orderId) {
    window.location.href = `/hozma/invoice/${orderId}`;
}