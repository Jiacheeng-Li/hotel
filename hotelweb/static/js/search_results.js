// Search Results Map Logic
let mapInitialized = false;
let map;

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar search form validation with English error messages
    const sidebarForm = document.getElementById('sidebarSearchForm');
    if (sidebarForm) {
        sidebarForm.addEventListener('submit', function(e) {
            const cityInput = document.getElementById('sidebar_city');
            const checkInInput = document.getElementById('sidebar_check_in');
            const checkOutInput = document.getElementById('sidebar_check_out');
            
            // Reset custom validity
            if (cityInput) cityInput.setCustomValidity('');
            if (checkInInput) checkInInput.setCustomValidity('');
            if (checkOutInput) checkOutInput.setCustomValidity('');
            
            // Validate city
            if (cityInput && !cityInput.value.trim()) {
                cityInput.setCustomValidity('Please enter a destination.');
                cityInput.reportValidity();
                e.preventDefault();
                return false;
            }
            
            // Validate dates
            if (checkInInput && !checkInInput.value) {
                checkInInput.setCustomValidity('Please select a check-in date.');
                checkInInput.reportValidity();
                e.preventDefault();
                return false;
            }
            
            if (checkOutInput && !checkOutInput.value) {
                checkOutInput.setCustomValidity('Please select a check-out date.');
                checkOutInput.reportValidity();
                e.preventDefault();
                return false;
            }
            
            // Validate check-out is after check-in
            if (checkInInput && checkOutInput && checkInInput.value && checkOutInput.value) {
                if (new Date(checkOutInput.value) <= new Date(checkInInput.value)) {
                    checkOutInput.setCustomValidity('Check-out date must be after check-in date.');
                    checkOutInput.reportValidity();
                    e.preventDefault();
                    return false;
                }
            }
        });
    }
    
    // Map initialization
    const mapTab = document.getElementById('map-tab');
    if (mapTab && window.searchData && window.searchData.hasResults) {
        mapTab.addEventListener('shown.bs.tab', () => {
            if (mapInitialized) {
                map.invalidateSize();
                return;
            }

            const defaultLat = window.searchData.defaultLat || 40.7128;
            const defaultLon = window.searchData.defaultLon || -74.0060;

            map = L.map('map').setView([defaultLat, defaultLon], 10);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            const hotels = window.searchData.hotels || [];

            hotels.forEach(h => {
                if (h.lat && h.lon) {
                    L.marker([h.lat, h.lon]).addTo(map)
                        .bindPopup(
                            `<b>${h.name}</b><br>
                             From $${h.price}<br>
                             <a href="${h.url}">View</a>`
                        );
                }
            });

            mapInitialized = true;
            setTimeout(() => map.invalidateSize(), 200);
        });
    }
});

