"""
Security utilities for payment processing and CSRF protection
"""
import hashlib
import hmac
import time
from flask import session, request, abort
from functools import wraps
from datetime import datetime, timedelta

def generate_csrf_token():
    """Generate a CSRF token and store it in session"""
    if 'csrf_token' not in session:
        # Generate token based on session ID and timestamp
        token_data = f"{session.get('_id', 'default')}_{time.time()}"
        session['csrf_token'] = hashlib.sha256(token_data.encode()).hexdigest()
    return session['csrf_token']

def validate_csrf_token(token):
    """Validate CSRF token from form"""
    if not token:
        return False
    expected_token = session.get('csrf_token')
    if not expected_token:
        return False
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(token, expected_token)

def csrf_protect(f):
    """Decorator to protect routes with CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not validate_csrf_token(token):
                abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def luhn_check(card_number):
    """
    Validate credit card number using Luhn algorithm
    Returns True if valid, False otherwise
    """
    # Remove spaces and non-digits
    card_number = ''.join(filter(str.isdigit, card_number))
    
    if not card_number or len(card_number) < 13:
        return False
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0

def validate_card_number(card_number):
    """
    Validate card number format and checksum
    Returns (is_valid, error_message)
    """
    # Remove spaces
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Check if all digits
    if not card_number.isdigit():
        return False, "Card number must contain only digits"
    
    # Check length (13-19 digits for most cards)
    if len(card_number) < 13 or len(card_number) > 19:
        return False, "Card number must be between 13 and 19 digits"
    
    # Luhn algorithm check
    if not luhn_check(card_number):
        return False, "Invalid card number (checksum failed)"
    
    return True, None

def validate_expiry_date(month, year):
    """
    Validate expiration date
    Returns (is_valid, error_message)
    """
    try:
        month_int = int(month)
        year_int = int(year)
        
        if month_int < 1 or month_int > 12:
            return False, "Invalid expiration month"
        
        # Check if date is in the past
        from datetime import datetime
        current_date = datetime.now()
        expiry_date = datetime(year_int, month_int, 1)
        
        if expiry_date < current_date:
            return False, "Card has expired"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid expiration date format"

def validate_cvv(cvv):
    """
    Validate CVV (3-4 digits)
    Returns (is_valid, error_message)
    """
    if not cvv or not cvv.isdigit():
        return False, "CVV must be numeric"
    
    if len(cvv) < 3 or len(cvv) > 4:
        return False, "CVV must be 3 or 4 digits"
    
    return True, None

def sanitize_card_input(card_number):
    """
    Sanitize card number input (remove spaces, dashes)
    Note: This does NOT encrypt or hash - just cleans input
    """
    return ''.join(filter(str.isdigit, card_number))

def sanitize_string(input_str, max_length=None):
    """
    Sanitize string input - strip whitespace and validate length
    Returns (sanitized_string, is_valid, error_message)
    """
    if input_str is None:
        return '', False, "Input cannot be None"
    
    # Convert to string and strip
    sanitized = str(input_str).strip()
    
    # Check if empty after stripping
    if not sanitized:
        return '', False, "Input cannot be empty"
    
    # Check max length if specified
    if max_length and len(sanitized) > max_length:
        return sanitized[:max_length], False, f"Input must be no more than {max_length} characters"
    
    return sanitized, True, None

def validate_username(username):
    """
    Validate username
    Returns (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    # Length check
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username must be no more than 50 characters"
    
    # Character check - alphanumeric, underscore, hyphen only
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, None

def validate_email(email):
    """
    Validate email format
    Returns (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Length check
    if len(email) > 255:
        return False, "Email must be no more than 255 characters"
    
    # Basic format check
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, None

def validate_password(password):
    """
    Validate password strength
    Requirements: 8-16 characters, must contain at least one letter and one number
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Length check
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 16:
        return False, "Password must be no more than 16 characters"
    
    # Check for at least one letter
    import re
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    # Check for at least one number
    has_number = bool(re.search(r'\d', password))
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, None

def check_password_strength(password):
    """
    Check password strength and return strength level
    Returns: 'weak', 'medium', 'strong'
    """
    if not password:
        return 'weak'
    
    strength = 0
    
    # Length check
    if len(password) >= 8:
        strength += 1
    if len(password) >= 12:
        strength += 1
    
    # Character variety
    import re
    if re.search(r'[a-z]', password):
        strength += 1
    if re.search(r'[A-Z]', password):
        strength += 1
    if re.search(r'\d', password):
        strength += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    
    if strength <= 2:
        return 'weak'
    elif strength <= 4:
        return 'medium'
    else:
        return 'strong'

def validate_phone(phone):
    """
    Validate phone number (optional field)
    Returns (is_valid, error_message, sanitized_phone)
    """
    if not phone:
        return True, None, None  # Phone is optional
    
    phone = phone.strip()
    
    # Remove common formatting characters
    import re
    phone_clean = re.sub(r'[^\d+]', '', phone)
    
    # Length check (assuming 10-15 digits for international)
    if len(phone_clean) < 10 or len(phone_clean) > 15:
        return False, "Phone number must be between 10 and 15 digits", None
    
    return True, None, phone_clean

def validate_text_field(text, field_name, max_length=None, required=False):
    """
    Validate text field (address, city, country, etc.)
    Returns (is_valid, error_message, sanitized_text)
    """
    if not text:
        if required:
            return False, f"{field_name} is required", None
        return True, None, None
    
    text = text.strip()
    
    if not text and required:
        return False, f"{field_name} is required", None
    
    if max_length and len(text) > max_length:
        return False, f"{field_name} must be no more than {max_length} characters", None
    
    # Basic XSS prevention - remove script tags and dangerous characters
    import re
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove other potentially dangerous tags
    text = re.sub(r'<[^>]+>', '', text)
    
    return True, None, text

def validate_postal_code(postal_code):
    """
    Validate postal code (optional field)
    Returns (is_valid, error_message, sanitized_code)
    """
    if not postal_code:
        return True, None, None  # Postal code is optional
    
    postal_code = postal_code.strip().upper()
    
    # Length check (most postal codes are 5-10 characters)
    if len(postal_code) < 3 or len(postal_code) > 10:
        return False, "Postal code must be between 3 and 10 characters", None
    
    return True, None, postal_code

def validate_rating(rating):
    """
    Validate rating (1-5)
    Returns (is_valid, error_message, rating_int)
    """
    if not rating:
        return False, "Rating is required", None
    
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            return False, "Rating must be between 1 and 5", None
        return True, None, rating_int
    except (ValueError, TypeError):
        return False, "Invalid rating format", None

def validate_comment(comment, max_length=5000):
    """
    Validate review comment
    Returns (is_valid, error_message, sanitized_comment)
    """
    if not comment:
        return True, None, None  # Comment is optional
    
    comment = comment.strip()
    
    if len(comment) > max_length:
        return False, f"Comment must be no more than {max_length} characters", None
    
    # Basic XSS prevention
    import re
    # Remove script tags
    comment = re.sub(r'<script[^>]*>.*?</script>', '', comment, flags=re.IGNORECASE | re.DOTALL)
    # Remove other potentially dangerous tags but allow basic formatting
    # Keep only safe tags like <p>, <br>, <strong>, <em>
    comment = re.sub(r'<(?!\/?(p|br|strong|em|b|i|u)\b)[^>]+>', '', comment)
    
    return True, None, comment

def validate_date(date_str, field_name, min_date=None, max_date=None):
    """
    Validate date string
    Returns (is_valid, error_message, date_obj)
    """
    if not date_str:
        return False, f"{field_name} is required", None
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if min_date and date_obj < min_date:
            return False, f"{field_name} cannot be before {min_date.strftime('%Y-%m-%d')}", None
        
        if max_date and date_obj > max_date:
            return False, f"{field_name} cannot be after {max_date.strftime('%Y-%m-%d')}", None
        
        return True, None, date_obj
    except ValueError:
        return False, f"Invalid {field_name} format. Please use YYYY-MM-DD", None

def validate_integer(value, field_name, min_value=None, max_value=None, required=False):
    """
    Validate integer value
    Returns (is_valid, error_message, int_value)
    """
    if not value:
        if required:
            return False, f"{field_name} is required", None
        return True, None, None
    
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False, f"{field_name} must be at least {min_value}", None
        
        if max_value is not None and int_value > max_value:
            return False, f"{field_name} must be no more than {max_value}", None
        
        return True, None, int_value
    except (ValueError, TypeError):
        return False, f"Invalid {field_name} format", None

# Login attempt tracking (in-memory, for production use Redis or database)
_login_attempts = {}

def check_login_attempts(identifier, max_attempts=5, lockout_duration=900):
    """
    Check if login attempts exceed limit
    identifier: email or IP address
    max_attempts: maximum failed attempts allowed
    lockout_duration: lockout duration in seconds (default 15 minutes)
    Returns (allowed, remaining_attempts, lockout_until)
    """
    now = datetime.now()
    
    if identifier not in _login_attempts:
        return True, max_attempts, None
    
    attempts_data = _login_attempts[identifier]
    
    # Check if locked out
    if attempts_data.get('lockout_until'):
        if now < attempts_data['lockout_until']:
            remaining_seconds = int((attempts_data['lockout_until'] - now).total_seconds())
            return False, 0, attempts_data['lockout_until']
        else:
            # Lockout expired, reset
            _login_attempts[identifier] = {'attempts': 0, 'last_attempt': None, 'lockout_until': None}
            return True, max_attempts, None
    
    # Check attempt count
    attempts = attempts_data.get('attempts', 0)
    last_attempt = attempts_data.get('last_attempt')
    
    # Reset if last attempt was more than 1 hour ago
    if last_attempt and (now - last_attempt).total_seconds() > 3600:
        _login_attempts[identifier] = {'attempts': 0, 'last_attempt': None, 'lockout_until': None}
        return True, max_attempts, None
    
    if attempts >= max_attempts:
        # Lock out
        lockout_until = now + timedelta(seconds=lockout_duration)
        _login_attempts[identifier]['lockout_until'] = lockout_until
        return False, 0, lockout_until
    
    remaining = max_attempts - attempts
    return True, remaining, None

def record_login_attempt(identifier, success):
    """
    Record a login attempt
    identifier: email or IP address
    success: True if login successful, False otherwise
    """
    if success:
        # Reset on successful login
        if identifier in _login_attempts:
            del _login_attempts[identifier]
    else:
        # Increment failed attempts
        if identifier not in _login_attempts:
            _login_attempts[identifier] = {'attempts': 0, 'last_attempt': None, 'lockout_until': None}
        
        _login_attempts[identifier]['attempts'] += 1
        _login_attempts[identifier]['last_attempt'] = datetime.now()

def get_client_ip():
    """
    Get client IP address from request
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

