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
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if there were previous failed attempts
        failed_attempts = session.get('login_failed_attempts', 0)
        
        # If there were failed attempts, require reCAPTCHA
        if failed_attempts > 0:
            recaptcha_response = request.form.get('g-recaptcha-response')
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                flash('Please complete the reCAPTCHA verification', 'danger')
                session['login_failed_attempts'] = failed_attempts + 1
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
            session['login_failed_attempts'] = failed_attempts + 1
            show_recaptcha = True  # Show reCAPTCHA after failure
            
    return render_template('auth/login.html', show_recaptcha=show_recaptcha)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    show_recaptcha = False
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if there were previous failed attempts
        failed_attempts = session.get('register_failed_attempts', 0)
        
        # If there were failed attempts, require reCAPTCHA
        if failed_attempts > 0:
            recaptcha_response = request.form.get('g-recaptcha-response')
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                flash('Please complete the reCAPTCHA verification', 'danger')
                session['register_failed_attempts'] = failed_attempts + 1
                return render_template('auth/register.html', show_recaptcha=True, 
                                     username=username, email=email)
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            session['register_failed_attempts'] = failed_attempts + 1
            return render_template('auth/register.html', show_recaptcha=(failed_attempts + 1 > 0),
                                 username=username or '', email=email or '')
            
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address.', 'danger')
            session['register_failed_attempts'] = failed_attempts + 1
            return render_template('auth/register.html', show_recaptcha=(failed_attempts + 1 > 0),
                                 username=username, email=email)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            session['register_failed_attempts'] = failed_attempts + 1
            return render_template('auth/register.html', show_recaptcha=(failed_attempts + 1 > 0),
                                 username=username, email=email)
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            session['register_failed_attempts'] = failed_attempts + 1
            return render_template('auth/register.html', show_recaptcha=(failed_attempts + 1 > 0),
                                 username=username, email=email)
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            session['register_failed_attempts'] = failed_attempts + 1
            return render_template('auth/register.html', show_recaptcha=(failed_attempts + 1 > 0),
                                 username=username, email=email)
            
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session['register_failed_attempts'] = 0  # Reset on success
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', show_recaptcha=show_recaptcha)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))
