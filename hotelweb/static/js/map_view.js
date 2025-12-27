// Encapsulate Map Logic
document.addEventListener('DOMContentLoaded', function () {
    const mapTab = document.getElementById('map-tab');
    if (!mapTab) return;

    let mapInitialized = false;
    let map;

    mapTab.addEventListener('shown.bs.tab', function () {
        if (mapInitialized) {
            setTimeout(() => map.invalidateSize(), 100);
            return;
        }

        initializeMap();
        mapInitialized = true;
    });

    function initializeMap() {
        const data = window.searchMapData || {};
        const results = data.results || [];

        let centerLat = data.defaultLat || 40.7128;
        let centerLon = data.defaultLon || -74.0060;

        map = L.map('map').setView([centerLat, centerLon], 12);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        results.forEach(hotel => {
            if (hotel.lat && hotel.lon) {

                // Custom Icon using Brand Logo
                let customIcon = L.icon({
                    iconUrl: hotel.brand_logo,
                    iconSize: [48, 48], // Size of the icon
                    iconAnchor: [24, 24], // Point of the icon which will correspond to marker's location
                    popupAnchor: [0, -24], // Point from which the popup should open relative to the iconAnchor
                    className: 'rounded-circle border border-2 border-white shadow bg-white object-fit-cover'
                });

                L.marker([hotel.lat, hotel.lon], { icon: customIcon }).addTo(map)
                    .bindPopup(
                        `<div class="text-center">
                            <h6 class="fw-bold mb-1">${hotel.name}</h6>
                            <p class="text-success fw-bold mb-1">From $${hotel.price}</p>
                            <a href="${hotel.url}" class="btn btn-primary btn-sm btn-sm-custom" style="padding: 2px 10px; font-size: 12px;">View</a>
                         </div>`
                    );
            }
        });

        // Trigger resize
        setTimeout(() => {
            map.invalidateSize();
        }, 200);
    }
});
