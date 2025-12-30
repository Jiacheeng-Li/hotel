// Tab switching for My Stays page
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Function to switch tabs
    function switchStaysTab(tabName) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.style.display = 'none';
        });
        
        // Remove active class from all buttons
        tabButtons.forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab content
        const targetTab = document.getElementById(tabName);
        if (targetTab) {
            targetTab.style.display = 'block';
        }
        
        // Add active class to clicked button
        const activeButton = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Update URL hash without scrolling
        if (tabName !== 'current') {
            // Use history API to update hash without scrolling
            if (history.replaceState) {
                history.replaceState(null, null, '#' + tabName);
            } else {
                // Fallback for older browsers
                const scrollY = window.scrollY;
                window.location.hash = tabName;
                window.scrollTo(0, scrollY);
            }
        } else {
            // Remove hash for current tab
            if (history.replaceState) {
                history.replaceState(null, null, window.location.pathname + window.location.search);
            } else {
                window.location.hash = '';
            }
        }
    }
    
    // Add click event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent any default behavior
            const tabName = this.getAttribute('data-tab');
            if (tabName) {
                switchStaysTab(tabName);
            }
        });
    });
    
    // Check URL hash on page load
    const hash = window.location.hash.substring(1);
    if (hash && ['upcoming', 'current', 'past', 'cancelled', 'favorites', 'events'].includes(hash)) {
        switchStaysTab(hash);
    } else {
        // Default to current tab
        switchStaysTab('current');
    }
    
    // Handle cancel booking form submissions
    const cancelForms = document.querySelectorAll('form[action*="cancel_booking"]');
    cancelForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to cancel this booking?')) {
                e.preventDefault();
                return false;
            }
        });
    });
});

