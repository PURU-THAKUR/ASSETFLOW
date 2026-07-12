from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import User, Notification
from database.database import db
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is deactivated. Please contact admin.', 'error')
                return render_template('login.html')
            
            session['user_id'] = user.id
            session['user_name'] = user.fullname
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['user_department'] = user.department
            session['user_employee_id'] = user.employee_id
            
            if remember:
                session.permanent = True
            
            flash(f'Welcome back, {user.fullname}! 🎉', 'success')
            
            # Log login activity
            from database.models import ActivityLog
            log = ActivityLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                resource_id=user.id,
                details=f'User logged in from {request.remote_addr}',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        department = request.form.get('department', '').strip()
        password = request.form.get('password', '')
        
        # Validation
        if not all([fullname, email, employee_id, department, password]):
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Please enter a valid email address.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(employee_id=employee_id).first():
            flash('Employee ID already exists.', 'error')
            return render_template('signup.html')
        
        # Create user (default role: Employee)
        user = User(
            fullname=fullname,
            email=email,
            employee_id=employee_id,
            department=department,
            role='Employee'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login to continue. 🎉', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # TODO: Send password reset email
            flash('Password reset link has been sent to your email.', 'success')
        else:
            flash('Email address not found.', 'error')
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # TODO: Implement password reset with token
    return render_template('reset_password.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        # Log logout activity
        from database.models import ActivityLog
        log = ActivityLog(
            user_id=session['user_id'],
            action='logout',
            resource_type='user',
            resource_id=session['user_id'],
            details='User logged out',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get user stats
    assets_count = db.session.query(db.func.count(AssetAllocation.id)).filter_by(
        user_id=user.id, status='Active'
    ).scalar() or 0
    
    returns_count = db.session.query(db.func.count(AssetAllocation.id)).filter_by(
        user_id=user.id, status='Returned'
    ).scalar() or 0
    
    booking_count = db.session.query(db.func.count(ResourceBooking.id)).filter_by(
        user_id=user.id
    ).scalar() or 0
    
    user.assets_count = assets_count
    user.returns_count = returns_count
    user.booking_count = booking_count
    
    return render_template('profile.html', user=user)

@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    
    fullname = request.form.get('fullname', '').strip()
    if fullname:
        user.fullname = fullname
    
    # Handle avatar upload
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename:
            from werkzeug.utils import secure_filename
            import os
            filename = secure_filename(f"user_{user.id}_{file.filename}")
            filepath = os.path.join('static/uploads/avatars', filename)
            file.save(filepath)
            user.avatar = f'/static/uploads/avatars/{filename}'
    
    db.session.commit()
    session['user_name'] = user.fullname
    flash('Profile updated successfully! ✅', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    
    current = request.form.get('current_password', '')
    new = request.form.get('new_password', '')
    confirm = request.form.get('confirm_password', '')
    
    if not user.check_password(current):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))
    
    if len(new) < 6:
        flash('New password must be at least 6 characters.', 'error')
        return redirect(url_for('auth.profile'))
    
    if new != confirm:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))
    
    user.set_password(new)
    db.session.commit()
    
    flash('Password changed successfully! 🔒', 'success')
    return redirect(url_for('auth.profile'))