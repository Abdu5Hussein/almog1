let allOrders = [];
        
document.addEventListener('DOMContentLoaded', function() {
    loadEmployeeInfo();
    loadDeliveryHistory();
    const defaultBtn = document.querySelector('.filter-btn.active');
filterOrders('all', defaultBtn);
    
    
});

async function loadEmployeeInfo() {
    try {
        const response = await fetch('/hozma/api/employee/profile/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('employeeName').textContent = `مرحباً، ${data.name || 'موظف التوصيل'}`;
        }
    } catch (error) {
        console.error('Error loading employee info:', error);
    }
}

function logout() {
fetch(`/api/user/logout`, {
method: "POST",
headers: {
"Content-Type": "application/json",
},
})
.then((response) => response.json())
.then((result) => {
console.log(result);
console.log("Logged out successfully");

// Redirect to login page
window.location.href = "/login";
})
.catch((error) => {
console.error("Error logging out:", error);
});
}


async function loadDeliveryHistory() {
try {
showLoading(true);
const response = await fetch('/hozma/api/delivery-history/', {
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
    }
});

if (!response.ok) {
    throw new Error('Failed to fetch history');
}

allOrders = await response.json();

// Get the "all" filter button
const defaultBtn = document.querySelector('.filter-btn[onclick*="all"]');
filterOrders('all', defaultBtn);

} catch (error) {
console.error('Error loading delivery history:', error);
showAlert('حدث خطأ أثناء تحميل السجل: ' + error.message, 'error');
} finally {
showLoading(false);
}
}


function filterOrders(filter, button = null) {
// Remove 'active' class from all buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
btn.classList.remove('active');
});

// If a button is passed (like from onclick), activate it
if (button) {
button.classList.add('active');
}

const now = new Date();
const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

const filteredOrders = allOrders.filter(order => {
const orderDate = new Date(order.delivery_end_time || order.order_date);

if (filter === 'delivered') return order.delivery_status === 'delivered';
if (filter === 'cancelled') return order.delivery_status === 'cancelled';
if (filter === 'today') return orderDate >= today;
if (filter === 'week') return orderDate >= oneWeekAgo;
return true; // 'all'
});

renderOrders(filteredOrders);
}


function renderOrders(orders) {
    const container = document.getElementById('historyContainer');
    container.innerHTML = '';
    
    if (orders.length === 0) {
        document.getElementById('noHistory').style.display = 'block';
        return;
    }
    
    document.getElementById('noHistory').style.display = 'none';
    
    orders.forEach(order => {
        const orderCard = document.createElement('div');
        orderCard.className = 'order-card';
        
        const statusClass = order.delivery_status === 'delivered' ? 'status-delivered' : 'status-cancelled';
        const statusText = order.delivery_status === 'delivered' ? 'تم التسليم' : 'ملغى';
        
        orderCard.innerHTML = `
            <div class="card-header">
                <span class="invoice-number">الفاتورة #${order.invoice_no}</span>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
            <div class="card-body">
                <div class="order-info-row">
                    <span class="order-info-label">المبلغ:</span>
                    <span class="order-info-value">${order.amount} دينار</span>
                </div>
                <div class="order-info-row">
                    <span class="order-info-label">تاريخ الطلب:</span>
                    <span class="order-info-value">${formatDate(order.date_time)}</span>
                </div>
                <div class="order-info-row">
                    <span class="order-info-label">تاريخ التسليم:</span>
                    <span class="order-info-value">${order.delivery_end_time ? formatDate(order.delivery_end_time) : '--'}</span>
                </div>
            </div>
        `;
        container.appendChild(orderCard);
    });
}

function formatDate(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('ar-LY', options);
}

function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
    if (show) {
        document.getElementById('noHistory').style.display = 'none';
    }
}

function showAlert(message, type) {
    // In a real app, you would use a more sophisticated notification system
    const alertBox = document.createElement('div');
    alertBox.style.position = 'fixed';
    alertBox.style.bottom = '20px';
    alertBox.style.left = '20px';
    alertBox.style.right = '20px';
    alertBox.style.padding = '15px';
    alertBox.style.borderRadius = 'var(--border-radius)';
    alertBox.style.boxShadow = 'var(--shadow-md)';
    alertBox.style.zIndex = '1000';
    alertBox.style.display = 'flex';
    alertBox.style.alignItems = 'center';
    alertBox.style.gap = '10px';
    
    let bgColor, icon;
    switch(type) {
        case 'success':
            bgColor = '#d4edda';
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            bgColor = '#f8d7da';
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        case 'warning':
            bgColor = '#fff3cd';
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
        default:
            bgColor = '#cce5ff';
            icon = '<i class="fas fa-info-circle"></i>';
    }
    
    alertBox.style.backgroundColor = bgColor;
    alertBox.style.color = type === 'warning' ? '#856404' : 
                          type === 'error' ? '#721c24' : 
                          type === 'success' ? '#155724' : '#004085';
    
    alertBox.innerHTML = `
        ${icon}
        <span>${message}</span>
    `;
    
    document.body.appendChild(alertBox);
    
    setTimeout(() => {
        alertBox.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(alertBox);
        }, 300);
    }, 3000);
}