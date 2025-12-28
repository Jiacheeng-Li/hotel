// Hotel Detail Logic
function toggleReviews() {
    const container = document.querySelector('.reviews-container');
    const text = document.getElementById('toggle-reviews-text');
    const icon = document.getElementById('toggle-reviews-icon');
    
    if (container.classList.contains('expanded')) {
        container.classList.remove('expanded');
        if (window.hotelDetailData) {
            const totalReviews = window.hotelDetailData.totalReviews;
            const visibleReviews = window.hotelDetailData.visibleReviews;
            text.textContent = `Show More Reviews (${totalReviews - visibleReviews} more)`;
        }
    } else {
        container.classList.add('expanded');
        text.textContent = 'Show Less';
    }
}

// Align image bottom with map bottom
document.addEventListener('DOMContentLoaded', function() {
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
    if (window.hotelDetailData && window.hotelDetailData.lat && window.hotelDetailData.lng) {
        // Use OpenStreetMap for hotel location
        const mapDiv = document.getElementById('hotel-map');
        if (mapDiv) {
            const lat = window.hotelDetailData.lat;
            const lng = window.hotelDetailData.lng;
            const zoom = 15;
            const bbox = `${lng - 0.01},${lat - 0.01},${lng + 0.01},${lat + 0.01}`;
            mapDiv.innerHTML = `<iframe width="100%" height="100%" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat},${lng}&zoom=${zoom}" style="border: none; border-radius: 12px;"></iframe>`;
            
            // Re-align after map loads
            setTimeout(alignHeights, 100);
        }
    }
});

