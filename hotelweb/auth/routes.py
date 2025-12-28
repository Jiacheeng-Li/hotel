from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from ..models import User
from ..extensions import db
from . import bp
import requests

def verify_recaptcha(response_token):
    """Verify reCAPTCHA token with Google's API"""
    if not current_app.config.get('RECAPTCHA_SECRET_KEY'):
        # If no secret key configured, skip verification (for development)
        return True
    
    secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    
    data = {
        'secret': secret_key,
        'response': response_token
    }
    
    try:
        response = requests.post(verify_url, data=data, timeout=5)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        current_app.logger.error(f'reCAPTCHA verification error: {e}')
        return False

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email_value = ''
    show_recaptcha = False
    
    # Check if reCAPTCHA should be shown
    # Show on first visit or after failed login attempts
    if request.method == 'GET':
        # Check if this is first visit (no trusted email in session)
        trusted_emails = session.get('trusted_emails', [])
        login_failed_attempts = session.get('login_failed_attempts', 0)
        
        # Show reCAPTCHA if:
        # 1. No trusted emails (first time visiting)
        # 2. Previous login failed
        if not trusted_emails or login_failed_attempts > 0:
            show_recaptcha = True
    elif request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        email_value = email  # Preserve email for form
        
        # Check if reCAPTCHA is required
        trusted_emails = session.get('trusted_emails', [])
        login_failed_attempts = session.get('login_failed_attempts', 0)
        
        if not trusted_emails or login_failed_attempts > 0:
            show_recaptcha = True
            # Verify reCAPTCHA if required
            recaptcha_response = request.form.get('g-recaptcha-response')
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                flash('Please complete the reCAPTCHA verification.', 'danger')
                return render_template('auth/login.html', email=email_value, show_recaptcha=True, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
        
        # Validate credentials
        if not email or not password:
            flash('Email and password are required.', 'danger')
            session['login_failed_attempts'] = session.get('login_failed_attempts', 0) + 1
            return render_template('auth/login.html', email=email_value, show_recaptcha=True, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Login successful
            login_user(user)
            session['login_failed_attempts'] = 0
            session['trusted_email_login'] = True
            # Keep track of recent successful logins for this email
            trusted_emails = session.get('trusted_emails', [])
            if email not in trusted_emails:
                trusted_emails.append(email)
                if len(trusted_emails) > 5:
                    trusted_emails.pop(0)
            session['trusted_emails'] = trusted_emails
            
            print(f"User {user.username} logged in.") 
            next_page = request.args.get('next')
            flash('You have been logged in successfully.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            # Login failed
            session['login_failed_attempts'] = session.get('login_failed_attempts', 0) + 1
            flash('Login Unsuccessful. Please check email and password', 'danger')
            show_recaptcha = True
            
    return render_template('auth/login.html', email=email_value, show_recaptcha=show_recaptcha, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verify reCAPTCHA (always required for registration)
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash('Please complete the reCAPTCHA verification.', 'danger')
            return render_template('auth/register.html', username=username or '', email=email or '', recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', username=username or '', email=email or '', recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
            
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address.', 'danger')
            return render_template('auth/register.html', username=username, email=email, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
            
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', username=username, email=email, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('auth/register.html', username=username, email=email, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return render_template('auth/register.html', username=username, email=email, recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))
            
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', recaptcha_site_key=current_app.config.get('RECAPTCHA_SITE_KEY', ''))

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))
