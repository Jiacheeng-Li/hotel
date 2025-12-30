// Home page search form validation with English error messages

document.addEventListener('DOMContentLoaded', function() {
    const homeForm = document.getElementById('homeSearchForm');
    if (!homeForm) return;
    
    const cityInput = document.getElementById('city');
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    
    // Set up custom validation messages for each input
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
            // Automatically update check-out date when check-in changes
            updateCheckOutMin();
        });
        
        checkInInput.addEventListener('change', function() {
            // Also update on change event (for date picker)
            updateCheckOutMin();
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
    
    // Form submission validation
    homeForm.addEventListener('submit', function(e) {
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
    
    // Function to update check-out minimum date based on check-in date
    function updateCheckOutMin() {
        if (checkInInput && checkInInput.value && checkOutInput) {
            const checkInDate = new Date(checkInInput.value);
            checkInDate.setDate(checkInDate.getDate() + 1);
            const minCheckOut = checkInDate.toISOString().split('T')[0];
            checkOutInput.min = minCheckOut;
            
            // If current check-out is before new minimum, update it
            if (checkOutInput.value && checkOutInput.value < minCheckOut) {
                checkOutInput.value = minCheckOut;
            }
        }
    }
});


