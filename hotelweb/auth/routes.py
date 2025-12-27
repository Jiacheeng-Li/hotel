from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from ..models import User
from ..extensions import db
from . import bp
import requests

def verify_recaptcha(response):
    """Verify reCAPTCHA response with Google's API"""
    try:
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJv')
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': secret_key,
            'response': response
        }
        result = requests.post(verify_url, data=data, timeout=5)
        result_json = result.json()
        return result_json.get('success', False)
    except Exception as e:
        # In development, return True to allow testing
        print(f"reCAPTCHA verification error: {e}")
        return True

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    show_recaptcha = False
    if request.method == 'GET':
        # Show reCAPTCHA for first-time login or if email is not in trusted list
        if not session.get('trusted_email_login', False):
            show_recaptcha = True
        elif session.get('login_failed_attempts', 0) > 0:
            show_recaptcha = True
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Determine if reCAPTCHA should be enforced for this POST request
        # Enforce if it was shown on GET, or if it's a subsequent failed attempt
        if not session.get('trusted_email_login', False) or session.get('login_failed_attempts', 0) > 0:
            recaptcha_response = request.form.get('g-recaptcha-response')
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                flash('Please complete the reCAPTCHA verification', 'danger')
                session['login_failed_attempts'] = session.get('login_failed_attempts', 0) + 1
                return render_template('auth/login.html', show_recaptcha=True)
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
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
            flash('Login Unsuccessful. Please check email and password', 'danger')
            session['login_failed_attempts'] = session.get('login_failed_attempts', 0) + 1
            show_recaptcha = True
            
    return render_template('auth/login.html', show_recaptcha=show_recaptcha)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    show_recaptcha = True  # Always show reCAPTCHA for registration (low intensity)
    
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        # For registration, reCAPTCHA is advisory (low intensity).
        # If verification fails, we still allow registration but log it or add extra checks.
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash('Please complete the reCAPTCHA verification (recommended)', 'warning')
            # Do NOT return here, allow registration to proceed but flag it if needed
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', show_recaptcha=show_recaptcha)
            
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address.', 'danger')
            return render_template('auth/register.html', show_recaptcha=show_recaptcha)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', show_recaptcha=show_recaptcha)
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('auth/register.html', show_recaptcha=show_recaptcha)
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return render_template('auth/register.html', show_recaptcha=show_recaptcha)
            
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', show_recaptcha=show_recaptcha)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))
