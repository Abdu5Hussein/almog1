let map;
let userMarker;
let clientMarker;
let currentOrder = null;
let watchId = null;
let currentInvoiceItems = [];
let routePolyline = null;
let isAvailable = false;
let locationUpdateInterval;


// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadOrders();
    checkAvailabilityStatus();
    setupAvailabilityToggle();
    loadEmployeeInfo();
});

// Check current availability status
async function checkAvailabilityStatus() {
    try {
        const response = await fetch('/hozma/api/employee/check-availability/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            isAvailable = data.is_available;
            document.getElementById('availabilityToggle').checked = isAvailable;
        }
    } catch (error) {
        console.error('Error checking availability:', error);
    }
}

function startLocationUpdates(lat, lng) {
    // Clear any existing interval
    if (locationUpdateInterval) clearInterval(locationUpdateInterval);
    
    // Send immediately
    sendLocationToServer(lat, lng);
    
    // Set up interval for every 2 seconds
    locationUpdateInterval = setInterval(() => {
        sendLocationToServer(lat, lng);
    }, 2000);
}

function stopLocationUpdates() {
    if (locationUpdateInterval) {
        clearInterval(locationUpdateInterval);
        locationUpdateInterval = null;
    }
}

// Setup availability toggle functionality
function setupAvailabilityToggle() {
    const toggle = document.getElementById('availabilityToggle');
    toggle.addEventListener('change', async function() {
        try {
            const newStatus = toggle.checked;
            const response = await fetch('/hozma/employee/set-availability/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
                body: JSON.stringify({
                    is_available: newStatus
                })
            });
            
            if (response.ok) {
                isAvailable = newStatus;
                showAlert(newStatus ? 'تم تفعيل حالة التوفر بنجاح' : 'تم إيقاف حالة التوفر', 'success');
            } else {
                toggle.checked = !newStatus; // Revert if failed
                throw new Error('Failed to update availability');
            }
        } catch (error) {
            console.error('Error updating availability:', error);
            showAlert('حدث خطأ أثناء تحديث الحالة', 'error');
        }
    });
}

// Load orders assigned to the current delivery employee
async function loadOrders() {
    try {
        showLoading(true);
        const response = await fetch('/hozma/api/my-assigned-orders/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch orders');
        }
        
        const orders = await response.json();
        const ordersContainer = document.getElementById('ordersContainer');
        ordersContainer.innerHTML = '';
        
        if (orders.length === 0) {
            document.getElementById('noOrders').style.display = 'block';
        } else {
            document.getElementById('noOrders').style.display = 'none';
            
            orders.forEach(order => {
                const clientLocation = order.client_geo_location ? 
                    order.client_geo_location.split(',').map(Number) : 
                    [null, null];
                
                const orderCard = document.createElement('div');
                orderCard.className = 'order-card';
                
                orderCard.innerHTML = `
                    <div class="card-header">
                        <span class="invoice-number">الفاتورة #${order.invoice_no}</span>
                        <span class="status-badge ${getStatusClass(order.delivery_status)}">
                            ${translateStatus(order.delivery_status)}
                        </span>
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
                        <div class="order-actions">
                            ${clientLocation[0] && clientLocation[1] ?
                                `<button class="btn btn-primary" onclick="openMap(${clientLocation[0]}, ${clientLocation[1]}, '${order.autoid}', '${order.invoice_no}')">
                                    <i class="fas fa-map-marker-alt"></i> تتبع
                                </button>` : ''}
                            <button class="btn btn-warning" onclick="showInvoiceItems('${order.invoice_no}')">
                                <i class="fas fa-list"></i> العناصر
                            </button>
                        </div>
                    </div>
                `;
                ordersContainer.appendChild(orderCard);
            });
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        showAlert('حدث خطأ أثناء تحميل الطلبات: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function getStatusClass(status) {
    const statusClasses = {
        'not_assigned': '',
        'assigned': 'status-assigned',
        'in_progress': 'status-in-progress',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    return statusClasses[status] || '';
}

function translateStatus(status) {
    const statusMap = {
        'not_assigned': 'غير مخصص',
        'assigned': 'مخصص',
        'in_progress': 'قيد التوصيل',
        'delivered': 'تم التوصيل',
        'cancelled': 'ملغى'
    };
    return statusMap[status] || status;
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
        document.getElementById('noOrders').style.display = 'none';
    }
}

function showAlert(message, type) {
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

function openMap(clientLat, clientLng, orderId, invoiceNo) {
    currentOrder = { clientLat, clientLng, orderId, invoiceNo };
    document.getElementById('mapContainer').style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent scrolling
    
    // Initialize map with better mobile view
    initMap(clientLat, clientLng);
    startTracking();
    
    // Update delivery status
    updateDeliveryStatus(orderId, 'in_progress');
    
    // Force resize of map to fit container
    setTimeout(() => {
        if (map) map.invalidateSize();
    }, 100);
}
function closeMap() {
    document.getElementById('mapContainer').style.display = 'none';
    
    if (map) {
        map.remove();
        map = null;
    }

    stopTracking();
}


function showOrderDetails() {
    if (currentOrder) {
        showInvoiceItems(currentOrder.invoiceNo);
    }
}

function initMap(clientLat, clientLng) {
    if (map) map.remove();
    
    map = L.map('map').setView([clientLat, clientLng], 15);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add client marker
    clientMarker = L.marker([clientLat, clientLng], {
        icon: L.divIcon({
            className: 'client-marker',
            html: '<div style="background-color: #f72585; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; border: 2px solid white;"><i class="fas fa-user"></i></div>',
            iconSize: [32, 32]
        })
    }).addTo(map).bindPopup("موقع العميل").openPopup();
}

// Modify the startTracking function
function startTracking() {
    if (watchId) navigator.geolocation.clearWatch(watchId);
    
    watchId = navigator.geolocation.watchPosition(
        (position) => {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            // Start continuous location updates
            startLocationUpdates(userLat, userLng);
            
            // Rest of the tracking code...
            if (userMarker) {
                userMarker.setLatLng([userLat, userLng]);
            } else {
                userMarker = L.marker([userLat, userLng], {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: '<div style="background-color: #4361ee; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; border: 2px solid white;"><i class="fas fa-motorcycle"></i></div>',
                        iconSize: [32, 32]
                    })
                }).addTo(map).bindPopup("موقعك الحالي").openPopup();
            }
            
            updateMapView();
            
            if (currentOrder) {
                const distance = calculateDistance(
                    userLat, userLng, 
                    currentOrder.clientLat, currentOrder.clientLng
                );
                document.getElementById('distance').textContent = Math.round(distance);
                
                const time = (distance / 1000) / 5 * 60;
                document.getElementById('duration').textContent = Math.round(time);
                
                drawRoute(userLat, userLng, currentOrder.clientLat, currentOrder.clientLng);
            }
        },
        (error) => {
            console.error('Geolocation error:', error);
            showAlert('تعذر الحصول على موقعك. يرجى تفعيل خدمة تحديد الموقع.', 'error');
        },
        {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 5000
        }
    );
}

// ... [previous code remains the same until the drawRoute function] ...

function drawRoute(startLat, startLng, endLat, endLng) {
    // Remove existing route if any
    if (routePolyline) {
        map.removeLayer(routePolyline);
    }

    // Use OSRM (Open Source Routing Machine) for actual road routing
    const baseUrl = 'https://router.project-osrm.org';
    const profile = 'driving'; // can be 'walking' or 'driving'
    
    fetch(`${baseUrl}/route/v1/${profile}/${startLng},${startLat};${endLng},${endLat}?overview=full&geometries=geojson`)
        .then(response => response.json())
        .then(data => {
            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];
                const routeCoordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
                
                // Draw the route on the map
                routePolyline = L.polyline(routeCoordinates, {
                    color: '#4361ee',
                    weight: 5,
                    opacity: 0.7,
                    dashArray: '10, 10'
                }).addTo(map);
                
                // Update distance and duration with actual routing data
                document.getElementById('distance').textContent = Math.round(route.distance);
                document.getElementById('duration').textContent = Math.round(route.duration / 60); // convert to minutes
                
                // Fit the map to the route bounds
                if (routePolyline) {
                    map.fitBounds(routePolyline.getBounds().pad(0.2));
                }
            }
        })
        .catch(error => {
            console.error('Error fetching route:', error);
            // Fallback to straight line if routing fails
            routePolyline = L.polyline(
                [[startLat, startLng], [endLat, endLng]],
                {color: '#4361ee', weight: 4, dashArray: '5, 5'}
            ).addTo(map);
        });
}

// ... [rest of the code remains the same] ...

function stopTracking() {
    if (watchId) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }

    stopLocationUpdates();
    userMarker = null;

    if (map && routePolyline) {
        map.removeLayer(routePolyline);
        routePolyline = null;
    }
}

function updateMapView() {
    if (userMarker && clientMarker && map) {
        const group = L.featureGroup([userMarker, clientMarker]);
        map.fitBounds(group.getBounds().pad(0.5));
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // metres
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c;
}

async function showInvoiceItems(invoiceNo) {
    try {
        showLoading(true);
        const response = await fetch(`/hozma/api/invoice-items/${invoiceNo}/`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch items');
        }
        
        currentInvoiceItems = await response.json();
        document.getElementById('invoiceNumber').textContent = invoiceNo;
        const itemsTableBody = document.getElementById('itemsTableBody');
        itemsTableBody.innerHTML = '';
       
        currentInvoiceItems.forEach(item => {
            const deliveryQty = item.confirmed_delevery_quantity != null ? item.confirmed_delevery_quantity : item.confirm_quantity;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.pno}</td>
                <td>${item.name}</td>
                <td>${item.confirm_quantity}</td>
                <td>
                    <input type="number" class="quantity-input" 
                           min="0" max="${item.confirm_quantity}" 
                           value="${deliveryQty}" 
                           onchange="validateQuantity(this, ${item.confirm_quantity})">
                </td>
            `;
            itemsTableBody.appendChild(row);
        });

        document.getElementById('itemsModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading items:', error);
        showAlert('حدث خطأ أثناء تحميل العناصر: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function closeItemsModal() {
    document.getElementById('itemsModal').style.display = 'none';
}

function validateQuantity(input, maxQuantity) {
    if (input.value > maxQuantity) {
        showAlert('لا يمكن تسليم كمية أكبر من المطلوبة', 'warning');
        input.value = maxQuantity;
    } else if (input.value < 0) {
        input.value = 0;
    }
}

async function saveQuantities() {
    try {
        showLoading(true);
        const inputs = document.querySelectorAll('.quantity-input');
        const itemsToUpdate = [];
        
        inputs.forEach((input, index) => {
            itemsToUpdate.push({
                item_id: currentInvoiceItems[index].pno,
                delivered_quantity: parseInt(input.value) || 0
            });
        });
        
        const response = await fetch(`/hozma/api/delivery/update-items/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            },
            body: JSON.stringify({
                items: itemsToUpdate,
                invoice_no: document.getElementById('invoiceNumber').textContent
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save quantities');
        }
        
        showAlert('تم حفظ الكميات بنجاح', 'success');
        closeItemsModal();
    } catch (error) {
        console.error('Error saving quantities:', error);
        showAlert('حدث خطأ أثناء حفظ الكميات: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function confirmDelivery() {
    if (confirm('هل أنت متأكد أنك سلمت جميع العناصر للعميل؟')) {
        try {
            showLoading(true);
            const response = await fetch(`/hozma/api/delivery/confirm-delivery/${currentOrder.orderId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
                body: JSON.stringify({
                    end_time: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to confirm delivery');
            }
            
            showAlert('تم تأكيد التسليم بنجاح', 'success');
            closeMap();
            loadOrders(); // Refresh the orders list
        } catch (error) {
            console.error('Error confirming delivery:', error);
            showAlert('حدث خطأ أثناء تأكيد التسليم: ' + error.message, 'error');
        } finally {
            showLoading(false);
        }
    }
}

async function updateDeliveryStatus(orderId, status) {
    try {
        const response = await fetch(`/hozma/api/delivery/update-status/${orderId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            },
            body: JSON.stringify({
                status: status,
                start_time: status === 'in_progress' ? new Date().toISOString() : null
            })
        });
        
        if (!response.ok) {
            console.error('Failed to update delivery status');
        }
    } catch (error) {
        console.error('Error updating delivery status:', error);
    }
}

async function loadEmployeeInfo() {
    try {
        const response = await fetch('/hozma/api/employee/profile/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('employeeName').textContent = data.name || 'موظف التوصيل';
            document.getElementById('employeeImage').src = data.employee_image_url || '/img/default-user.png';
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


function showHistory() {
    window.location.href = '/hozma/delivery-history/';
}

let lastSentTime = 0;

function sendLocationToServer(lat, lng) {
    const now = Date.now();

    // Only send once every 10 seconds
    if (now - lastSentTime < 1000) return;

    lastSentTime = now;

    fetch('/hozma/api/employee/update-location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng
        })
    })
    .then(res => {
        if (!res.ok) {
            console.error('Failed to update location');
        }
    })
    .catch(error => {
        console.error('Error sending location:', error);
    });
}
