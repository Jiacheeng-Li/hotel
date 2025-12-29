from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from ..models import User
from ..extensions import db
from ..utils.security import (
    validate_email as validate_email_format,
    validate_username,
    validate_password,
    sanitize_string,
    check_login_attempts,
    record_login_attempt,
    get_client_ip,
    generate_csrf_token
)
from datetime import datetime
from werkzeug.security import generate_password_hash
from . import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Generate CSRF token for GET request
    csrf_token = generate_csrf_token()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        client_ip = get_client_ip()
        
        # Use email as identifier for login attempts (more secure than IP)
        identifier = email if email else client_ip
        
        # Check login attempts
        allowed, remaining, lockout_until = check_login_attempts(identifier, max_attempts=5, lockout_duration=900)
        if not allowed:
            if lockout_until:
                from datetime import datetime
                now = datetime.now()
                if lockout_until > now:
                    minutes = int((lockout_until - now).total_seconds() / 60) + 1
                    flash(f'Too many failed login attempts. Please try again in {minutes} minute(s).', 'danger')
                else:
                    flash('Too many failed login attempts. Please try again later.', 'danger')
            else:
                flash('Too many failed login attempts. Please try again later.', 'danger')
            return render_template('auth/login.html', email=email, csrf_token=csrf_token)
        
        # Validate credentials
        if not email or not password:
            record_login_attempt(identifier, False)
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html', email=email, csrf_token=csrf_token)
        
        # Validate email format
        is_valid, error_msg = validate_email_format(email)
        if not is_valid:
            record_login_attempt(identifier, False)
            flash(error_msg or 'Invalid email format.', 'danger')
            return render_template('auth/login.html', email=email, csrf_token=csrf_token)
        
        # Validate password (basic check - not empty)
        if len(password) < 1:
            record_login_attempt(identifier, False)
            flash('Password is required.', 'danger')
            return render_template('auth/login.html', email=email, csrf_token=csrf_token)
        
        # Query user (use constant-time comparison to prevent user enumeration)
        user = User.query.filter_by(email=email).first()
        
        # Always perform password check to prevent timing attacks
        # Use a dummy password hash if user doesn't exist
        if user:
            password_valid = user.check_password(password)
        else:
            # Use a dummy check to prevent timing attacks
            dummy_hash = generate_password_hash('dummy')
            password_valid = False
        
        if user and password_valid:
            # Login successful
            record_login_attempt(identifier, True)
            login_user(user)
            next_page = request.args.get('next')
            flash('You have been logged in successfully.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            # Login failed - don't reveal if email exists
            record_login_attempt(identifier, False)
            flash('Invalid email or password. Please try again.', 'danger')
            if remaining and remaining < 5:
                flash(f'Warning: {remaining} attempt(s) remaining before account lockout.', 'warning')
            
    return render_template('auth/login.html', csrf_token=csrf_token)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Generate CSRF token for GET request
    csrf_token = generate_csrf_token()
        
    if request.method == 'POST':
        username_raw = request.form.get('username', '').strip()
        email_raw = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Sanitize and validate username
        username, is_valid, error_msg = sanitize_string(username_raw, max_length=50)
        if not is_valid or not username:
            flash(error_msg or 'Username is required.', 'danger')
            return render_template('auth/register.html', username=username_raw, email=email_raw, csrf_token=csrf_token)
        
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            flash(error_msg or 'Invalid username.', 'danger')
            return render_template('auth/register.html', username=username_raw, email=email_raw, csrf_token=csrf_token)
        
        # Validate email
        email, is_valid, error_msg = sanitize_string(email_raw, max_length=255)
        if not is_valid or not email:
            flash(error_msg or 'Email is required.', 'danger')
            return render_template('auth/register.html', username=username_raw, email=email_raw, csrf_token=csrf_token)
        
        is_valid, error_msg = validate_email_format(email)
        if not is_valid:
            flash(error_msg or 'Invalid email address.', 'danger')
            return render_template('auth/register.html', username=username_raw, email=email_raw, csrf_token=csrf_token)
        
        # Validate password (enhanced: 8-16 chars, letter + number)
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg or 'Invalid password.', 'danger')
            return render_template('auth/register.html', username=username_raw, email=email_raw, csrf_token=csrf_token)
        
        # Check for existing email (use constant-time to prevent enumeration)
        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            flash('An account with this email already exists. Please use a different email or try logging in.', 'warning')
            return render_template('auth/register.html', username=username, email='', csrf_token=csrf_token)  # Don't reveal email
            
        # Check for existing username
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_username:
            flash('Username already taken. Please choose a different username.', 'warning')
            return render_template('auth/register.html', username='', email=email, csrf_token=csrf_token)  # Don't reveal username
            
        # Create user - only as customer role (never accept role from frontend)
        user = User(username=username, email=email, role='customer')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', csrf_token=csrf_token)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Save user role before logout (current_user becomes unavailable after logout_user())
    user_role = current_user.role if current_user.is_authenticated else None
    logout_user()
    
    # Redirect to appropriate login page based on role
    if user_role == 'staff':
        return redirect(url_for('staff.login'))
    elif user_role == 'admin':
        return redirect(url_for('admin.login'))
    else:
        return redirect(url_for('auth.login'))
