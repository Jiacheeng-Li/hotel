// Hotel Detail Logic
function toggleReviews() {
    const container = document.querySelector('.reviews-container');
    const text = document.getElementById('toggle-reviews-text');
    const icon = document.getElementById('toggle-reviews-icon');
    
    if (!container) return;
    
    if (container.classList.contains('expanded')) {
        container.classList.remove('expanded');
        if (window.hotelDetailData) {
            const totalReviews = window.hotelDetailData.totalReviews;
            const visibleReviews = window.hotelDetailData.visibleReviews;
            if (text) {
                text.textContent = `Show More Reviews (${totalReviews - visibleReviews} more)`;
            }
        }
    } else {
        container.classList.add('expanded');
        if (text) {
            text.textContent = 'Show Less';
        }
    }
}

// Initialize hotel detail data from data attribute
function initializeHotelDetailData() {
    const container = document.querySelector('[data-hotel-detail]');
    if (container) {
        try {
            const dataStr = container.getAttribute('data-hotel-detail');
            if (dataStr) {
                window.hotelDetailData = JSON.parse(dataStr);
            } else {
                // Default values if data attribute is missing
                window.hotelDetailData = {
                    totalReviews: 0,
                    visibleReviews: 6,
                    lat: null,
                    lng: null
                };
            }
        } catch (e) {
            console.error('Error parsing hotel detail data:', e);
            window.hotelDetailData = {
                totalReviews: 0,
                visibleReviews: 6,
                lat: null,
                lng: null
            };
        }
    } else {
        // Default values if container is missing
        window.hotelDetailData = {
            totalReviews: 0,
            visibleReviews: 6,
            lat: null,
            lng: null
        };
    }
}

// Align image bottom with map bottom
document.addEventListener('DOMContentLoaded', function() {
    // Initialize data first
    initializeHotelDetailData();
    
    const image = document.getElementById('hotel-main-image');
    const infoColumn = document.getElementById('hotel-info-column');
    
    function alignHeights() {
        if (image && infoColumn) {
            const infoHeight = infoColumn.offsetHeight;
            image.style.height = infoHeight + 'px';
        }
    }
    
    // Align on load
    alignHeights();
    
    // Re-align on window resize
    window.addEventListener('resize', alignHeights);
    
    // Map initialization
    if (window.hotelDetailData) {
        const lat = window.hotelDetailData.lat;
        const lng = window.hotelDetailData.lng;
        
        // Check if lat and lng are valid numbers (not null, not undefined, not NaN)
        if (lat !== null && lng !== null && !isNaN(lat) && !isNaN(lng)) {
            // Use OpenStreetMap for hotel location
            const mapDiv = document.getElementById('hotel-map');
            if (mapDiv) {
                // Convert to numbers to ensure they're numeric
                const latNum = parseFloat(lat);
                const lngNum = parseFloat(lng);
                const zoom = 15;
                const bbox = `${lngNum - 0.01},${latNum - 0.01},${lngNum + 0.01},${latNum + 0.01}`;
                mapDiv.innerHTML = `<iframe width="100%" height="100%" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${latNum},${lngNum}&zoom=${zoom}" style="border: none; border-radius: 12px;"></iframe>`;
                
                // Re-align after map loads
                setTimeout(alignHeights, 100);
            }
        }
    }
    
    // Initialize toggle reviews button
    const toggleReviewsBtn = document.getElementById('toggle-reviews-btn');
    if (toggleReviewsBtn) {
        toggleReviewsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleReviews();
        });
    }
});

