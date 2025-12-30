// Login Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    if (!form || !emailInput || !passwordInput) return;
    
    // Setup field validation
    setupFieldValidation(emailInput, validateEmail, 'Email');
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        const emailResult = validateEmail(emailInput.value);
        
        if (!emailResult.valid) {
            e.preventDefault();
            showValidationError(emailInput, emailResult.message);
            emailInput.focus();
            return false;
        }
        
        if (!passwordInput.value || passwordInput.value.trim() === '') {
            e.preventDefault();
            showValidationError(passwordInput, 'Password is required');
            passwordInput.focus();
            return false;
        }
    });
});

