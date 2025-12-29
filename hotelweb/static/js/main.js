document.addEventListener('DOMContentLoaded', function () {
    // Update flash messages container position based on navbar height
    function updateFlashMessagesPosition() {
        const navbar = document.querySelector('nav.navbar');
        const flashContainer = document.getElementById('flash-messages-container');
        if (navbar && flashContainer) {
            const navbarHeight = navbar.offsetHeight;
            flashContainer.style.top = navbarHeight + 'px';
        }
    }
    
    // Update position on load
    updateFlashMessagesPosition();
    
    // Update position on window resize (in case navbar height changes)
    window.addEventListener('resize', updateFlashMessagesPosition);
    
    // Auto-dismiss alerts after 2 seconds
    const alerts = document.querySelectorAll('.alert.auto-dismiss');
    alerts.forEach(function(alert) {
        const dismissTime = alert.getAttribute('data-auto-dismiss') || 2000;
        setTimeout(function() {
            // Check if bootstrap is defined (it might not be on all pages or loaded yet)
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                // Fallback if bootstrap is not available
                alert.style.display = 'none';
            }
        }, dismissTime);
    });

    // Active Nav Link Highlighter
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link:not(.dropdown-toggle)');

    navLinks.forEach(link => link.classList.remove('active'));

    navLinks.forEach(link => {
        try {
            const linkPath = new URL(link.href).pathname;

            if (linkPath === currentPath ||
                (currentPath === '/' && linkPath === '/') ||
                (currentPath.startsWith('/search') && linkPath === '/') ||
                (currentPath.startsWith('/brand') && linkPath === '/brands')) {
                link.classList.add('active');
            }
        } catch (e) {
            // Ignore invalid URLs
        }
    });
});

// Date validation functions
function updateCheckOutMin() {
    const checkIn = document.getElementById('check_in');
    const checkOut = document.getElementById('check_out');
    if (checkIn && checkIn.value) {
        const checkInDate = new Date(checkIn.value);
        checkInDate.setDate(checkInDate.getDate() + 1);
        const minCheckOut = checkInDate.toISOString().split('T')[0];
        if (checkOut) {
            checkOut.min = minCheckOut;
            if (checkOut.value && checkOut.value < minCheckOut) {
                checkOut.value = minCheckOut;
            }
        }
    }
}

function updateCheckOutMinSidebar() {
    const checkIn = document.querySelector('input[name="check_in"]');
    const checkOut = document.getElementById('sidebar_check_out');
    if (checkIn && checkOut && checkIn.value) {
        const checkInDate = new Date(checkIn.value);
        checkInDate.setDate(checkInDate.getDate() + 1);
        const minCheckOut = checkInDate.toISOString().split('T')[0];
        checkOut.min = minCheckOut;
        if (checkOut.value && checkOut.value < minCheckOut) {
            checkOut.value = minCheckOut;
        }
    }
}
