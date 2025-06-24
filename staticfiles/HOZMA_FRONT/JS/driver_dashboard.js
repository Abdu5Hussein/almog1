let map;
let userMarker;
let clientMarker;
let currentOrder = null;
let watchId = null;
let currentInvoiceItems = [];
let routePolyline = null;

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
        const tableBody = document.querySelector('#ordersTable tbody');
        tableBody.innerHTML = '';
        
        if (orders.length === 0) {
            document.getElementById('noOrders').style.display = 'block';
            document.getElementById('ordersTable').style.display = 'none';
        } else {
            document.getElementById('noOrders').style.display = 'none';
            document.getElementById('ordersTable').style.display = 'table';
            
            orders.forEach(order => {
                const row = document.createElement('tr');
                const clientLocation = order.client_geo_location ? 
                    order.client_geo_location.split(',').map(Number) : 
                    [null, null];
                
                row.innerHTML = `
                    <td>${order.invoice_no}</td>
                    <td>${order.amount} دينار</td>
                    <td>${translateStatus(order.delivery_status)}</td>
                    <td>
                        ${clientLocation[0] && clientLocation[1] ?
                            `<button class="btn" onclick="openMap(${clientLocation[0]}, ${clientLocation[1]}, '${order.autoid}', '${order.invoice_no}')">
                                <i class="fas fa-map-marker-alt"></i> تتبع
                            </button>` : ''}
                        <button class="btn" onclick="showInvoiceItems('${order.invoice_no}')">
                            <i class="fas fa-list"></i> العناصر
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        alert('حدث خطأ أثناء تحميل الطلبات: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    // You can implement a loading spinner here if needed
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

function openMap(clientLat, clientLng, orderId, invoiceNo) {
    currentOrder = { clientLat, clientLng, orderId, invoiceNo };
    document.getElementById('mapContainer').style.display = 'block';
    initMap(clientLat, clientLng);
    startTracking();
    
    // Update delivery status to "in_progress" if it's "assigned"
    updateDeliveryStatus(orderId, 'in_progress');
}

function closeMap() {
    document.getElementById('mapContainer').style.display = 'none';
    if (map) map.remove();
    map = null;
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
            html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%;"></div>',
            iconSize: [20, 20]
        })
    }).addTo(map).bindPopup("موقع العميل");
}

function startTracking() {
    if (watchId) navigator.geolocation.clearWatch(watchId);
    
    watchId = navigator.geolocation.watchPosition(
        (position) => {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            // Update or create user marker
            if (userMarker) {
                userMarker.setLatLng([userLat, userLng]);
            } else {
                userMarker = L.marker([userLat, userLng], {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: '<div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%;"></div>',
                        iconSize: [20, 20]
                    })
                }).addTo(map).bindPopup("موقعك الحالي").openPopup();
            }
            
            // Update map view
            updateMapView();
            
            // Calculate distance
            if (currentOrder) {
                const distance = calculateDistance(
                    userLat, userLng, 
                    currentOrder.clientLat, currentOrder.clientLng
                );
                document.getElementById('distance').textContent = Math.round(distance);
                
                // Estimate time (assuming 5 km/h walking speed)
                const time = (distance / 1000) / 5 * 60;
                document.getElementById('duration').textContent = Math.round(time);
                
                // Draw route if not already drawn
                drawRoute(userLat, userLng, currentOrder.clientLat, currentOrder.clientLng);
            }
        },
        (error) => {
            console.error('Geolocation error:', error);
            alert('تعذر الحصول على موقعك. يرجى تفعيل خدمة تحديد الموقع.');
        },
        {
            enableHighAccuracy: true,
            maximumAge: 10000,
            timeout: 5000
        }
    );
}

function drawRoute(startLat, startLng, endLat, endLng) {
    // In a real app, you would use a routing service like OSRM, Mapbox, etc.
    // This is a simplified version that just draws a straight line
    
    if (routePolyline) {
        map.removeLayer(routePolyline);
    }
    
    routePolyline = L.polyline(
        [[startLat, startLng], [endLat, endLng]],
        {color: 'blue', weight: 3, dashArray: '5, 5'}
    ).addTo(map);
}

function stopTracking() {
    if (watchId) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }
    userMarker = null;
    if (routePolyline) {
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
        alert('حدث خطأ أثناء تحميل العناصر: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function closeItemsModal() {
    document.getElementById('itemsModal').style.display = 'none';
}

function validateQuantity(input, maxQuantity) {
    if (input.value > maxQuantity) {
        alert('لا يمكن تسليم كمية أكبر من المطلوبة');
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
        
        alert('تم حفظ الكميات بنجاح');
        closeItemsModal();
    } catch (error) {
        console.error('Error saving quantities:', error);
        alert('حدث خطأ أثناء حفظ الكميات: ' + error.message);
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
            
            alert('تم تأكيد التسليم بنجاح');
            closeMap();
            loadOrders(); // Refresh the orders list
        } catch (error) {
            console.error('Error confirming delivery:', error);
            alert('حدث خطأ أثناء تأكيد التسليم: ' + error.message);
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

// Load orders when page loads
document.addEventListener('DOMContentLoaded', loadOrders);