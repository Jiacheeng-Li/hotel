// Search Results Map Logic
let mapInitialized = false;
let map;

// Initialize search data from data attributes
function initializeSearchData() {
    const dataElement = document.querySelector('.search-data');
    if (dataElement) {
        try {
            const hasResults = dataElement.getAttribute('data-has-results') === 'true';
            const defaultLat = parseFloat(dataElement.getAttribute('data-default-lat')) || 40.7128;
            const defaultLon = parseFloat(dataElement.getAttribute('data-default-lon')) || -74.0060;
            
            window.searchData = {
                hasResults: hasResults,
                defaultLat: defaultLat,
                defaultLon: defaultLon,
                hotels: []
            };
            
            // Load hotels from JSON script tag
            const hotelsScript = document.getElementById('search-hotels-data');
            if (hotelsScript) {
                try {
                    window.searchData.hotels = JSON.parse(hotelsScript.textContent);
                } catch (e) {
                    console.error('Error parsing hotels data:', e);
                    window.searchData.hotels = [];
                }
            }
        } catch (e) {
            console.error('Error initializing search data:', e);
            window.searchData = {
                hasResults: false,
                defaultLat: 40.7128,
                defaultLon: -74.0060,
                hotels: []
            };
        }
    } else {
        window.searchData = {
            hasResults: false,
            defaultLat: 40.7128,
            defaultLon: -74.0060,
            hotels: []
        };
    }
}

// Toggle search filter on mobile
function toggleSearchFilter() {
    const filterContent = document.querySelector('.search-filter-content');
    const toggleButton = document.querySelector('.search-filter-toggle');
    
    if (!filterContent || !toggleButton) return;
    
    const isExpanded = filterContent.classList.contains('show');
    
    if (isExpanded) {
        filterContent.classList.remove('show');
        toggleButton.setAttribute('aria-expanded', 'false');
    } else {
        filterContent.classList.add('show');
        toggleButton.setAttribute('aria-expanded', 'true');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize data first
    initializeSearchData();
    
    // Mobile filter toggle
    const filterToggle = document.querySelector('.search-filter-toggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSearchFilter();
        });
        
        // Initialize state - collapsed on mobile by default
        if (window.innerWidth <= 576) {
            const filterContent = document.querySelector('.search-filter-content');
            if (filterContent) {
                filterContent.classList.remove('show');
                filterToggle.setAttribute('aria-expanded', 'false');
            }
        }
    }
    
    // Sidebar search form validation with English error messages
    const sidebarForm = document.getElementById('sidebarSearchForm');
    if (sidebarForm) {
        const cityInput = document.getElementById('sidebar_city');
        const checkInInput = document.getElementById('sidebar_check_in');
        const checkOutInput = document.getElementById('sidebar_check_out');
        
        // Set up custom validation messages
        if (cityInput) {
            cityInput.addEventListener('invalid', function(e) {
                if (!this.value.trim()) {
                    this.setCustomValidity('Please enter a destination.');
                } else {
                    this.setCustomValidity('');
                }
            });
            
            cityInput.addEventListener('input', function() {
                this.setCustomValidity('');
            });
        }
        
        if (checkInInput) {
            checkInInput.addEventListener('invalid', function(e) {
                if (!this.value) {
                    this.setCustomValidity('Please select a check-in date.');
                } else {
                    this.setCustomValidity('');
                }
            });
            
            checkInInput.addEventListener('input', function() {
                this.setCustomValidity('');
            });
            
            checkInInput.addEventListener('change', function() {
                updateCheckOutMinSidebar();
            });
            
            checkInInput.addEventListener('input', function() {
                updateCheckOutMinSidebar();
            });
        }
        
        if (checkOutInput) {
            checkOutInput.addEventListener('invalid', function(e) {
                if (!this.value) {
                    this.setCustomValidity('Please select a check-out date.');
                } else {
                    this.setCustomValidity('');
                }
            });
            
            checkOutInput.addEventListener('input', function() {
                this.setCustomValidity('');
            });
        }
        
        // Sort by change handler
        const sortSelect = document.getElementById('sort_by');
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                this.form.submit();
            });
        }
        
        sidebarForm.addEventListener('submit', function(e) {
            // Reset custom validity
            if (cityInput) cityInput.setCustomValidity('');
            if (checkInInput) checkInInput.setCustomValidity('');
            if (checkOutInput) checkOutInput.setCustomValidity('');
            
            // Validate and set default values for guests and rooms if empty
            const guestsInput = document.getElementById('sidebar_guests');
            const roomsInput = document.getElementById('sidebar_rooms_needed');
            
            if (guestsInput) {
                const guestsValue = parseInt(guestsInput.value);
                if (!guestsInput.value || isNaN(guestsValue) || guestsValue < 1) {
                    guestsInput.value = '1';
                }
            }
            
            if (roomsInput) {
                const roomsValue = parseInt(roomsInput.value);
                if (!roomsInput.value || isNaN(roomsValue) || roomsValue < 1) {
                    roomsInput.value = '1';
                }
            }
            
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

