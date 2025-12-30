// Register Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const strengthIndicator = document.getElementById('password-strength-indicator');
    
    if (!form || !usernameInput || !emailInput || !passwordInput || !strengthIndicator) return;
    
    // Setup field validation
    setupFieldValidation(usernameInput, validateUsername, 'Username');
    setupFieldValidation(emailInput, validateEmail, 'Email');
    setupFieldValidation(passwordInput, validatePassword, 'Password');
    
    // Password strength indicator
    passwordInput.addEventListener('input', function() {
        const password = passwordInput.value;
        if (password.length > 0) {
            strengthIndicator.classList.remove('hidden');
            strengthIndicator.style.display = 'block';
            updatePasswordStrength(passwordInput, 'password-strength-indicator', 'password-strength-message');
        } else {
            strengthIndicator.classList.add('hidden');
            strengthIndicator.style.display = 'none';
        }
        clearValidationError(passwordInput);
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let hasErrors = false;
        
        const usernameResult = validateUsername(usernameInput.value);
        if (!usernameResult.valid) {
            e.preventDefault();
            showValidationError(usernameInput, usernameResult.message);
            if (!hasErrors) {
                usernameInput.focus();
                hasErrors = true;
            }
        }
        
        const emailResult = validateEmail(emailInput.value);
        if (!emailResult.valid) {
            e.preventDefault();
            showValidationError(emailInput, emailResult.message);
            if (!hasErrors) {
                emailInput.focus();
                hasErrors = true;
            }
        }
        
        const passwordResult = validatePassword(passwordInput.value);
        if (!passwordResult.valid) {
            e.preventDefault();
            showValidationError(passwordInput, passwordResult.message);
            if (!hasErrors) {
                passwordInput.focus();
                hasErrors = true;
            }
        }
        
        if (hasErrors) {
            return false;
        }
    });
});

