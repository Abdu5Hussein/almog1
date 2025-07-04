let map;
let marker;
let defaultPosition = [32.8872, 13.1913]; // Default to Tripoli, Libya

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
    if (!navigator.geolocation) {
        showToast("المتصفح لا يدعم تحديد الموقع", "error");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            map.setView([lat, lng], 15);
            marker.setLatLng([lat, lng]);
            updateGeoLocation({ lat, lng });
        },
        (error) => {
            console.error("Geolocation error:", error);
            showToast("تعذر الحصول على موقعك الحالي", "error");

            // Optional fallback to Tripoli
            const fallbackLat = 32.8872;
            const fallbackLng = 13.1913;
            map.setView([fallbackLat, fallbackLng], 12);
            marker.setLatLng([fallbackLat, fallbackLng]);
            updateGeoLocation({ lat: fallbackLat, lng: fallbackLng });
        }
    );
}


function loadProfileData() {
    const customerId = JSON.parse(localStorage.getItem("session_data@client_id")).replace(/^c-/, '');
    
    customFetch(`/hozma/api/clients/${customerId}/`)
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
   
    document.getElementById('mobile').value = clientData.mobile || '';
    document.getElementById('website').value = clientData.website || '';
    document.getElementById('address').value = clientData.address || '';
}

function updateProfile() {
    const customerId = JSON.parse(localStorage.getItem("session_data@client_id")).replace(/^c-/, '');

    const nameField = document.getElementById('name');
    const addressField = document.getElementById('address');

    const newName = nameField.value;
    const newAddress = addressField.value;

    // Get current values from localStorage or hidden fields (replace this with actual sources if needed)
    const currentName = nameField.getAttribute('data-current') || "";
    const currentAddress = addressField.getAttribute('data-current') || "";

    // If no change, do nothing
    if (newName === currentName && newAddress === currentAddress) {
        Toastify({
            text: "لم تقم بأي تغيير على الاسم أو العنوان.",
            duration: 3000,
            close: true,
            gravity: "top",
            position: "right",
            backgroundColor: "#ffc107",
        }).showToast();
        return;
    }

    // Show confirmation Swal
    Swal.fire({
        title: 'هل أنت متأكد؟',
        text: 'سيتم تحديث الاسم أو العنوان، هل ترغب في المتابعة؟',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'نعم، تحديث',
        cancelButtonText: 'إلغاء'
    }).then((result) => {
        if (!result.isConfirmed) return;

        // Continue if confirmed
        const formData = {
            name: newName,
            email: document.getElementById('email').value,
            mobile: document.getElementById('mobile').value,
            website: document.getElementById('website').value,
            address: newAddress,
            geo_location: document.getElementById('geo_location').value
        };

        const saveBtn = document.querySelector('#profileForm button[type="submit"]');
        const originalBtnText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> جاري الحفظ...';
        saveBtn.disabled = true;

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
            Toastify({
                text: "✅ تم تحديث الملف الشخصي بنجاح",
                duration: 3000,
                close: true,
                gravity: "top",
                position: "right",
                backgroundColor: "#28a745",
            }).showToast();

            setTimeout(() => {
                window.location.href = '/hozma/hozmaDashbord';
            }, 1500);
        })
        .catch(error => {
            const errorMsg = error.detail || '❌ حدث خطأ أثناء تحديث الملف الشخصي';
            Swal.fire({
                icon: 'error',
                title: 'خطأ!',
                text: errorMsg,
                confirmButtonText: 'حسنًا'
            });
        })
        .finally(() => {
            saveBtn.innerHTML = originalBtnText;
            saveBtn.disabled = false;
        });
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