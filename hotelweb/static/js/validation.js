// Client-side input validation

/**
 * Validate email format
 */
function validateEmail(email) {
    if (!email || !email.trim()) {
        return { valid: false, message: 'Email is required' };
    }
    
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email.trim())) {
        return { valid: false, message: 'Invalid email format' };
    }
    
    if (email.trim().length > 255) {
        return { valid: false, message: 'Email must be no more than 255 characters' };
    }
    
    return { valid: true };
}

/**
 * Validate username
 */
function validateUsername(username) {
    if (!username || !username.trim()) {
        return { valid: false, message: 'Username is required' };
    }
    
    const trimmed = username.trim();
    
    if (trimmed.length < 3) {
        return { valid: false, message: 'Username must be at least 3 characters' };
    }
    
    if (trimmed.length > 50) {
        return { valid: false, message: 'Username must be no more than 50 characters' };
    }
    
    const usernameRegex = /^[a-zA-Z0-9_-]+$/;
    if (!usernameRegex.test(trimmed)) {
        return { valid: false, message: 'Username can only contain letters, numbers, underscores, and hyphens' };
    }
    
    return { valid: true };
}

/**
 * Validate password (8-16 characters, must contain letter and number)
 */
function validatePassword(password) {
    if (!password) {
        return { valid: false, message: 'Password is required' };
    }
    
    if (password.length < 8) {
        return { valid: false, message: 'Password must be at least 8 characters' };
    }
    
    if (password.length > 16) {
        return { valid: false, message: 'Password must be no more than 16 characters' };
    }
    
    // Check for at least one letter
    const hasLetter = /[a-zA-Z]/.test(password);
    if (!hasLetter) {
        return { valid: false, message: 'Password must contain at least one letter' };
    }
    
    // Check for at least one number
    const hasNumber = /\d/.test(password);
    if (!hasNumber) {
        return { valid: false, message: 'Password must contain at least one number' };
    }
    
    return { valid: true };
}

/**
 * Check password strength
 */
function checkPasswordStrength(password) {
    if (!password) {
        return { strength: 'weak', message: '' };
    }
    
    let strength = 0;
    let feedback = [];
    
    // Length check
    if (password.length >= 8) {
        strength += 1;
    } else {
        feedback.push('At least 8 characters');
    }
    
    if (password.length >= 12) {
        strength += 1;
    }
    
    // Character variety
    if (/[a-z]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('lowercase letter');
    }
    
    if (/[A-Z]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('uppercase letter');
    }
    
    if (/\d/.test(password)) {
        strength += 1;
    } else {
        feedback.push('number');
    }
    
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('special character');
    }
    
    let strengthLevel = 'weak';
    let message = '';
    
    if (strength <= 2) {
        strengthLevel = 'weak';
        message = feedback.length > 0 ? 'Consider adding: ' + feedback.slice(0, 2).join(', ') : '';
    } else if (strength <= 4) {
        strengthLevel = 'medium';
        message = feedback.length > 0 ? 'Consider adding: ' + feedback[0] : 'Good password';
    } else {
        strengthLevel = 'strong';
        message = 'Strong password';
    }
    
    return { strength: strengthLevel, message: message };
}

/**
 * Update password strength indicator
 */
function updatePasswordStrength(input, indicatorId, messageId) {
    const password = input.value;
    const strength = checkPasswordStrength(password);
    const indicator = document.getElementById(indicatorId);
    const message = document.getElementById(messageId);
    
    if (!indicator) return;
    
    // Remove all strength classes
    indicator.classList.remove('password-weak', 'password-medium', 'password-strong');
    
    if (password.length === 0) {
        indicator.className = '';
        if (message) message.textContent = '';
        return;
    }
    
    // Add appropriate class
    indicator.classList.add(`password-${strength.strength}`);
    
    if (message) {
        message.textContent = strength.message;
        message.className = `password-strength-message password-${strength.strength}`;
    }
}

/**
 * Validate text field (address, city, country, etc.)
 */
function validateTextField(text, fieldName, maxLength, required = false) {
    if (!text || !text.trim()) {
        if (required) {
            return { valid: false, message: `${fieldName} is required` };
        }
        return { valid: true };
    }
    
    const trimmed = text.trim();
    
    if (maxLength && trimmed.length > maxLength) {
        return { valid: false, message: `${fieldName} must be no more than ${maxLength} characters` };
    }
    
    return { valid: true };
}

/**
 * Validate phone number
 */
function validatePhone(phone) {
    if (!phone || !phone.trim()) {
        return { valid: true }; // Phone is optional
    }
    
    const cleaned = phone.replace(/[^\d+]/g, '');
    
    if (cleaned.length < 10 || cleaned.length > 15) {
        return { valid: false, message: 'Phone number must be between 10 and 15 digits' };
    }
    
    return { valid: true };
}

/**
 * Validate postal code
 */
function validatePostalCode(postalCode) {
    if (!postalCode || !postalCode.trim()) {
        return { valid: true }; // Postal code is optional
    }
    
    const trimmed = postalCode.trim();
    
    if (trimmed.length < 3 || trimmed.length > 10) {
        return { valid: false, message: 'Postal code must be between 3 and 10 characters' };
    }
    
    return { valid: true };
}

/**
 * Validate date
 */
function validateDate(dateStr, fieldName, minDate = null, maxDate = null) {
    if (!dateStr || !dateStr.trim()) {
        return { valid: false, message: `${fieldName} is required` };
    }
    
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateStr)) {
        return { valid: false, message: `Invalid ${fieldName} format. Please use YYYY-MM-DD` };
    }
    
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
        return { valid: false, message: `Invalid ${fieldName}` };
    }
    
    if (minDate) {
        const min = new Date(minDate);
        if (date < min) {
            return { valid: false, message: `${fieldName} cannot be before ${minDate}` };
        }
    }
    
    if (maxDate) {
        const max = new Date(maxDate);
        if (date > max) {
            return { valid: false, message: `${fieldName} cannot be after ${maxDate}` };
        }
    }
    
    return { valid: true };
}

/**
 * Validate integer
 */
function validateInteger(value, fieldName, minValue = null, maxValue = null, required = false) {
    if (!value || value.toString().trim() === '') {
        if (required) {
            return { valid: false, message: `${fieldName} is required` };
        }
        return { valid: true };
    }
    
    const intValue = parseInt(value, 10);
    
    if (isNaN(intValue)) {
        return { valid: false, message: `Invalid ${fieldName} format` };
    }
    
    if (minValue !== null && intValue < minValue) {
        return { valid: false, message: `${fieldName} must be at least ${minValue}` };
    }
    
    if (maxValue !== null && intValue > maxValue) {
        return { valid: false, message: `${fieldName} must be no more than ${maxValue}` };
    }
    
    return { valid: true };
}

/**
 * Validate rating (1-5)
 */
function validateRating(rating) {
    if (!rating) {
        return { valid: false, message: 'Rating is required' };
    }
    
    const ratingInt = parseInt(rating, 10);
    
    if (isNaN(ratingInt) || ratingInt < 1 || ratingInt > 5) {
        return { valid: false, message: 'Rating must be between 1 and 5' };
    }
    
    return { valid: true };
}

/**
 * Validate comment/review text
 */
function validateComment(comment, maxLength = 5000) {
    if (!comment || !comment.trim()) {
        return { valid: true }; // Comment is optional
    }
    
    const trimmed = comment.trim();
    
    if (trimmed.length > maxLength) {
        return { valid: false, message: `Comment must be no more than ${maxLength} characters` };
    }
    
    return { valid: true };
}

/**
 * Show validation error message
 */
function showValidationError(input, message) {
    // Remove existing error message
    const existingError = input.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Remove error class
    input.classList.remove('is-invalid');
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error text-danger small mt-1';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
    input.classList.add('is-invalid');
}

/**
 * Clear validation error
 */
function clearValidationError(input) {
    const existingError = input.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
    input.classList.remove('is-invalid');
}

/**
 * Validate form field on blur
 */
function setupFieldValidation(input, validator, fieldName, options = {}) {
    input.addEventListener('blur', function() {
        const value = input.value;
        const result = validator(value, fieldName, ...Object.values(options));
        
        if (!result.valid) {
            showValidationError(input, result.message);
        } else {
            clearValidationError(input);
        }
    });
    
    input.addEventListener('input', function() {
        // Clear error on input
        clearValidationError(input);
    });
}

