// Home page search form validation with English error messages

document.addEventListener('DOMContentLoaded', function() {
    const homeForm = document.getElementById('homeSearchForm');
    if (homeForm) {
        homeForm.addEventListener('submit', function(e) {
            const cityInput = document.getElementById('city');
            const checkInInput = document.getElementById('check_in');
            const checkOutInput = document.getElementById('check_out');
            
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
});


