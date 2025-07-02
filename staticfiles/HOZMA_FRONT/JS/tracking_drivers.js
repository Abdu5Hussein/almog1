// Initialize the map centered on Tripoli, Libya
const map = L.map('map').setView([32.8872, 13.1913], 12);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Store employee markers
const employeeMarkers = {};
const clientMarkers = {};

// Icons for different employee types
const icons = {
    driver: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/1559/1559861.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    Shop_employee: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/1077/1077114.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    Hozma_employee: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3442/3442348.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    admin: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/2206/2206368.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    manager: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3281/3281289.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    accountant: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3059/3059518.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    }),
    default: L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/1077/1077063.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    })
};
const clientIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/869/869636.png', // example client icon, you can replace it
    iconSize: [28, 28],
    iconAnchor: [14, 28]
});

// Company icon (store icon)
const companyIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/4300/4300059.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40]
});

const storageIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2897/2897818.png',
    iconSize: [36, 36],
    iconAnchor: [18, 36]
});
// Add company marker
const companyMarker = L.marker([32.856019, 13.142810], { icon: companyIcon })
    .addTo(map)
    .bindPopup('<b>Our Company Location</b>');

// Add storage marker
const storageMarker = L.marker([32.854169, 13.142441], { icon: storageIcon })
    .addTo(map)
    .bindPopup('<b>Storage Location</b>');

// Function to get icon color based on availability and order status
function getStatusColor(isAvailable, hasActiveOrder) {
    if (!isAvailable) return '#E74C3C'; // Red for unavailable
    if (hasActiveOrder) return '#F39C12'; // Orange for on order
    return '#2ECC71'; // Green for available
}

// Fetch and update employee markers on the map
// Update employee and client markers on the map
function updateEmployeeLocations() {
    fetch('/hozma/locations/', {
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        // --- HANDLE EMPLOYEES ---

        // Remove old employee markers no longer in data
        Object.keys(employeeMarkers).forEach(id => {
            if (!data.employees.some(emp => emp.employee_id.toString() === id)) {
                map.removeLayer(employeeMarkers[id]);
                delete employeeMarkers[id];
            }
        });

        // Add/update employee markers
        data.employees.forEach(employee => {
            const id = employee.employee_id.toString();
            const lat = employee.current_latitude;
            const lng = employee.current_longitude;
            
            if (lat && lng) {
                const icon = icons[employee.type] || icons.default;
                const customIcon = L.divIcon({
                    html: `
                        <div class="employee-marker">
                            <img src="${icon.options.iconUrl}" 
                                 width="${icon.options.iconSize[0]}" 
                                 height="${icon.options.iconSize[1]}"
                                 style="filter: drop-shadow(0 0 2px ${getStatusColor(employee.is_available, employee.has_active_order)})">
                            <div class="employee-name">${employee.name}</div>
                        </div>
                    `,
                    className: 'employee-div-icon',
                    iconSize: [icon.options.iconSize[0], icon.options.iconSize[1] + 20],
                    iconAnchor: [icon.options.iconAnchor[0], icon.options.iconAnchor[1] + 10]
                });

                if (employeeMarkers[id]) {
                    employeeMarkers[id].setLatLng([lat, lng]);
                } else {
                    employeeMarkers[id] = L.marker([lat, lng], { icon: customIcon }).addTo(map);
                    employeeMarkers[id].bindPopup(`
                        <b>${employee.name}</b><br>
                        Type: ${employee.type.replace('_', ' ')}<br>
                        Status: ${employee.is_available ? 
                            (employee.has_active_order ? 'On Order' : 'Available') : 'Unavailable'}<br>
                        Phone: ${employee.phone || 'N/A'}<br>
                        Last Update: ${employee.last_updated}
                    `);
                }
            }
        });

        // --- HANDLE CLIENTS ---

        // Remove old client markers no longer in data
        Object.keys(clientMarkers).forEach(id => {
            if (!data.clients.some(client => client.clientid.toString() === id)) {
                map.removeLayer(clientMarkers[id]);
                delete clientMarkers[id];
            }
        });

        // Add/update client markers
        data.clients.forEach(client => {
            const id = client.clientid.toString();
            if (!client.geo_location) return;

            // Parse lat,lng from geo_location string
            // Example format: "32.84440429734253,13.061499595642092"
            let [latStr, lngStr] = client.geo_location.split(',').map(s => s.trim());

            // Skip if parse fails
            if (!latStr || !lngStr) return;

            // Sometimes coordinates can have degree symbols or directions (e.g. "40.7128° N")
            // For this example, ignore any with invalid format:
            if (latStr.includes('°') || lngStr.includes('°')) return;

            const lat = parseFloat(latStr);
            const lng = parseFloat(lngStr);
            if (isNaN(lat) || isNaN(lng)) return;

            if (clientMarkers[id]) {
                clientMarkers[id].setLatLng([lat, lng]);
            } else {
                clientMarkers[id] = L.marker([lat, lng], { icon: clientIcon }).addTo(map);
                clientMarkers[id].bindPopup(`
                    <b>Client: ${client.name || 'Unknown'}</b><br>
                    Phone: ${client.phone || 'N/A'}<br>
                    ID: ${client.clientid}
                `);
            }
        });
    })
    .catch(error => console.error('Error fetching locations:', error));
}

// Helper to get CSRF cookie by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            const cookie = c.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initial load
updateEmployeeLocations();

// Auto-refresh every 1 second
setInterval(updateEmployeeLocations, 1000);

// Manual refresh button handler
document.getElementById('refreshBtn').addEventListener('click', updateEmployeeLocations);
