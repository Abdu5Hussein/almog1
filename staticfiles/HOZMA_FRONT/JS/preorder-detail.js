const invoiceNo = window.location.pathname.split('/')[3];
document.getElementById('invoice-no').textContent = invoiceNo;

async function fetchPreOrderDetails() {
    try {
        const response = await customFetch(`/hozma/api/preorders/?invoice_no=${invoiceNo}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        const preorder = responseData.preorders[0];
        const preorderItems = responseData.preorder_items;
        
        const preorderItemsList = document.getElementById('preorder-items-list');
        const loadingState = document.getElementById('loading-state');
        
        preorderItemsList.innerHTML = '';
        
        // Update header info
        document.getElementById('client-name').textContent = preorder.client || 'N/A';
        document.getElementById('order-date').textContent = new Date(preorder.date || Date.now()).toLocaleDateString();
        
        loadingState.style.display = 'none';

        preorderItems.forEach(function (item) {
            const row = document.createElement('tr');
        
            const orderedQty = parseInt(item.quantity);
            const confirmQty = parseInt(item.confirm_quantity || item.quantity);
            const confirmedDeliveryQty = item.confirmed_delevery_quantity !== null && 
                                        item.confirmed_delevery_quantity !== undefined
                ? parseInt(item.confirmed_delevery_quantity)
                : confirmQty; // Default to confirmQty if not provided
            
            // Determine which row class to apply
            let rowClass = '';
            
            // First check if delivery quantity differs from confirmed quantity (blue)
            if (confirmedDeliveryQty !== confirmQty) {
                rowClass = 'row-blue';
            } 
            // Then check if ordered quantity differs from confirmed quantity (yellow)
            else if (orderedQty !== confirmQty) {
                rowClass = 'row-yellow';
            }
            
            row.className = rowClass;
            
            row.innerHTML = `
                <td>${item.pno}</td>
                <td>${item.name}</td>
                <td>${orderedQty}</td>
                <td>${confirmQty}</td>
                <td>
                    ${item.confirmed_delevery_quantity !== null && 
                     item.confirmed_delevery_quantity !== undefined
                        ? item.confirmed_delevery_quantity
                        : confirmQty}
                </td>
                <td>${Number(item.dinar_unit_price).toLocaleString(undefined, { minimumFractionDigits: 2 })} د.ل</td>
                <td>${Number(item.dinar_total_price).toLocaleString(undefined, { minimumFractionDigits: 2 })} د.ل</td>
                <td>
                    ${item.quantity_proccessed ? 
                        '<span class="badge bg-success">نعم</span>' : 
                        '<span class="badge bg-secondary">لا</span>'}
                </td>
            `;
        
            preorderItemsList.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching PreOrder details:', error);
        const loadingState = document.getElementById('loading-state');
        loadingState.innerHTML = `
            <td colspan="8" class="text-center py-4 text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <p>Failed to load order details. Please try again later.</p>
                <button class="btn btn-sm btn-primary" onclick="window.location.reload()">
                    <i class="fas fa-sync-alt me-1"></i> Retry
                </button>
            </td>
        `;
        loadingState.style.display = '';
    }
}

fetchPreOrderDetails();

async function sendPrintRequest(invoiceNo) {
    try {
        const payload = {
            label: "specific_sell_invoice",
            invoice_no: invoiceNo
        };

        const response = await fetch('/hozma/api/print', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Failed to send print request. Status: ${response.status}`);
        }

        const resultHtml = await response.text();
        const printWindow = window.open('', '_blank');
        printWindow.document.open();
        printWindow.document.write(resultHtml);
        printWindow.document.close();

    } catch (error) {
        console.error("Error sending print request:", error);
        alert("حدث خطأ أثناء محاولة الطباعة. يرجى المحاولة مرة أخرى.");
    }
}