let map;
let marker;
let defaultPosition = [24.7136, 46.6753]; // Default to Riyadh

function initMap() {
    // Initialize map
    map = L.map('map').setView(defaultPosition, 12);
    
    // Add tile layer (you can use any tile layer you prefer)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Add marker
    marker = L.marker(defaultPosition, {
        draggable: true
    }).addTo(map);
    
    // Update geo_location when marker is moved
    marker.on('dragend', function() {
        updateGeoLocation(marker.getLatLng());
    });
    
    // Click on map to add marker
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        updateGeoLocation(e.latlng);
    });
    
    // Load existing location if available
    loadProfileData();
}
let debounceTimer;
function updateGeoLocation(position) {
clearTimeout(debounceTimer);
debounceTimer = setTimeout(() => {
const geoLocation = `${position.lat},${position.lng}`;
document.getElementById('geo_location').value = geoLocation;

fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.lat}&lon=${position.lng}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('address').value = data.display_name;
    })
    .catch(error => console.error('Geocoding error:', error));
}, 500); // Delay in milliseconds
}



function locateMe() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                map.setView([pos.lat, pos.lng], 15);
                marker.setLatLng([pos.lat, pos.lng]);
                updateGeoLocation({lat: pos.lat, lng: pos.lng});
            },
            () => {
                showToast("تعذر الحصول على موقعك الحالي", "error");
            }
        );
    } else {
        showToast("المتصفح لا يدعم تحديد الموقع", "error");
    }
}

function loadProfileData() {
    const customerId = JSON.parse(localStorage.getItem("session_data@user_id")).replace(/^c-/, '');
    
    customFetch(`http://45.13.59.226/api/clients/${customerId}/`)
        .then(response => response.json())
        .then(data => {
            if (!data || !data.clients || data.clients.length === 0) {
                throw new Error("No client data found");
            }

            const client = data.clients[0];
            populateForm(client);
            
            // Set map location if available
            if (client.geo_location) {
                const [lat, lng] = client.geo_location.split(',').map(Number);
                
                map.setView([lat, lng], 15);
                marker.setLatLng([lat, lng]);
                document.getElementById('geo_location').value = client.geo_location;
            }
        })
        .catch(error => {
            console.error('Error loading profile:', error);
            showToast('حدث خطأ أثناء تحميل بيانات الملف الشخصي', 'error');
        });
}

function populateForm(clientData) {
    document.getElementById('name').value = clientData.name || '';
    document.getElementById('email').value = clientData.email || '';
    document.getElementById('phone').value = clientData.phone || '';
    document.getElementById('mobile').value = clientData.mobile || '';
    document.getElementById('website').value = clientData.website || '';
    document.getElementById('address').value = clientData.address || '';
}

function updateProfile() {
    const customerId = JSON.parse(localStorage.getItem("session_data@user_id")).replace(/^c-/, '');
    
    // Prepare form data
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        mobile: document.getElementById('mobile').value,
        website: document.getElementById('website').value,
        address: document.getElementById('address').value,
        geo_location: document.getElementById('geo_location').value
    };
    
    // Show loading state
    const saveBtn = document.querySelector('#profileForm button[type="submit"]');
    const originalBtnText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> جاري الحفظ...';
    saveBtn.disabled = true;
    
    // Send to API
    customFetch(`/hozma/api/update-client/${customerId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        showToast('تم تحديث الملف الشخصي بنجاح', 'success');
        setTimeout(() => {
            window.location.href = '/hozma/hozmaDashbord';
        }, 1500);
    })
    .catch(error => {
        console.error('Error updating profile:', error);
        const errorMsg = error.detail || 'حدث خطأ أثناء تحديث الملف الشخصي';
        showToast(errorMsg, 'error');
    })
    .finally(() => {
        saveBtn.innerHTML = originalBtnText;
        saveBtn.disabled = false;
    });
}

// Initialize form
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('profileForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateProfile();
    });
    
    initMap();
});

function showToast(message, type) {
    // Implement your toast notification here
    alert(`${type === 'success' ? '✓' : '✗'} ${message}`);
}