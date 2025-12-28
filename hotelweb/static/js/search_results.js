// Search Results Map Logic
let mapInitialized = false;
let map;

document.addEventListener('DOMContentLoaded', function() {
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

