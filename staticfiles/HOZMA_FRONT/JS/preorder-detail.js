const invoiceNo = window.location.pathname.split('/')[3];  // Get the invoice_no from the URL
console.log('Invoice No:', invoiceNo);  // Log the invoiceNo

document.getElementById('invoice-no').textContent = invoiceNo;

// Fetch the PreOrder and its items using customFetch
async function fetchPreOrderDetails() {
    try {
        const response = await customFetch(`http://45.13.59.226/hozma/api/preorders/?invoice_no=${invoiceNo}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        
        console.log('API Response:', responseData);  // Log the entire API response
        
        const preorder = responseData.preorders[0]; // Get the first preorder from the response
        const preorderItems = responseData.preorder_items;
        
        const preorderItemsList = document.getElementById('preorder-items-list');
        const loadingState = document.getElementById('loading-state');
        
        // Clear existing items
        preorderItemsList.innerHTML = '';
        
        // Update header info
        document.getElementById('client-name').textContent = preorder.client || 'N/A';
        document.getElementById('order-date').textContent = new Date(preorder.date || Date.now()).toLocaleDateString();
        
        loadingState.style.display = 'none';
        
        preorderItems.forEach(function (item) {
            const row = document.createElement('tr');
            const orderedQty = parseInt(item.quantity);
            const confirmQty = parseInt(item.confirm_quantity || item.quantity);
            const hasDifference = orderedQty !== confirmQty;
            
            row.innerHTML = `
    <td>${item.pno}</td>
    <td>${item.name}</td>
    <td class="${hasDifference ? 'diff-highlight' : ''}">${orderedQty}</td>
    <td>
        <input type="number" 
               id="confirm-quantity-${item.pno}" 
               class="quantity-input ${hasDifference ? 'diff-highlight' : ''}" 
               value="${confirmQty}" 
               min="0"
               onchange="highlightDifference('${item.pno}', ${orderedQty})">
    </td>
<td>${Number(item.dinar_unit_price).toLocaleString(undefined, { minimumFractionDigits: 2 })} د.ل</td>
<td>${Number(item.dinar_total_price).toLocaleString(undefined, { minimumFractionDigits: 2 })} د.ل</td>
    <td>
        ${item.quantity_proccessed ? 
            '<span class="badge bg-success">نعم</span>' : 
            '<span class="badge bg-secondary">لا</span>'
        }
    </td>
   
`;

            preorderItemsList.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching PreOrder details:', error);  // Use console.error for errors
        const loadingState = document.getElementById('loading-state');
        loadingState.innerHTML = `
            <td colspan="5" class="text-center py-4 text-danger">
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

fetchPreOrderDetails(); // Call to fetch the preorder details

function highlightDifference(itemNo, originalQty) {
    const confirmInput = document.getElementById(`confirm-quantity-${itemNo}`);
    const confirmQty = parseInt(confirmInput.value);
    const row = confirmInput.closest('tr');
    
    if (confirmQty !== originalQty) {
        confirmInput.classList.add('diff-highlight');
        row.querySelector('td:nth-child(3)').classList.add('diff-highlight');
    } else {
        confirmInput.classList.remove('diff-highlight');
        row.querySelector('td:nth-child(3)').classList.remove('diff-highlight');
    }
}


