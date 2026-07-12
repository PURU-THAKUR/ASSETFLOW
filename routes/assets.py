from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from database.models import Asset, AssetCategory, Department, AssetAllocation, Notification, ActivityLog
from database.database import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
from ai.knowledge import KnowledgeBase

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

@assets_bp.route('/')
def list_assets():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get filters
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    department = request.args.get('department', '')
    search = request.args.get('search', '')
    
    query = Asset.query
    
    if category:
        query = query.filter(Asset.category.has(name=category))
    if status:
        query = query.filter_by(status=status)
    if department:
        query = query.filter(Asset.department.has(name=department))
    if search:
        query = query.filter(
            (Asset.name.ilike(f'%{search}%')) |
            (Asset.tag.ilike(f'%{search}%')) |
            (Asset.serial_number.ilike(f'%{search}%'))
        )
    
    assets = query.order_by(Asset.created_at.desc()).all()
    categories = AssetCategory.query.all()
    departments = Department.query.all()
    statuses = ['Available', 'Allocated', 'Maintenance', 'Lost']
    
    return render_template('assets.html',
        assets=assets,
        categories=categories,
        departments=departments,
        statuses=statuses,
        selected_category=category,
        selected_status=status,
        selected_department=department,
        search_query=search
    )

@assets_bp.route('/view/<int:asset_id>')
def view_asset(asset_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    asset = Asset.query.get_or_404(asset_id)
    allocation = asset.get_current_allocation()
    maintenance_history = MaintenanceRequest.query.filter_by(asset_id=asset_id).all()
    booking_history = ResourceBooking.query.filter_by(asset_id=asset_id).all()
    
    return render_template('asset_view.html',
        asset=asset,
        allocation=allocation,
        maintenance_history=maintenance_history,
        booking_history=booking_history
    )

@assets_bp.route('/add', methods=['POST'])
def add_asset():
    if 'user_id' not in session:
        return redirect('/login')
    
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category')
    serial_number = request.form.get('serial', '').strip()
    department_id = request.form.get('department')
    location = request.form.get('location', '').strip()
    cost = request.form.get('cost', 0)
    purchase_date = request.form.get('purchase_date', '')
    
    if not name:
        flash('Asset name is required.', 'error')
        return redirect(url_for('assets.list_assets'))
    
    # Generate asset tag
    from ai.rule_engine import RuleEngine
    rule_engine = RuleEngine()
    tag = rule_engine.generate_asset_tag()
    
    asset = Asset(
        tag=tag,
        name=name,
        serial_number=serial_number if serial_number else None,
        category_id=int(category_id) if category_id else None,
        department_id=int(department_id) if department_id else None,
        location=location if location else None,
        cost=float(cost) if cost else None,
        status='Available',
        health_score=100
    )
    
    if purchase_date:
        try:
            asset.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        except:
            pass
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(f"asset_{tag}_{file.filename}")
            filepath = os.path.join('static/uploads/assets', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            asset.image = f'/static/uploads/assets/{filename}'
    
    db.session.add(asset)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=session['user_id'],
        title='Asset Created',
        message=f'Asset {tag} - {name} has been added to the system.',
        type='asset_created',
        icon='✨',
        link=f'/assets/view/{asset.id}'
    )
    db.session.add(notification)
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='create_asset',
        resource_type='asset',
        resource_id=asset.id,
        details=f'Created asset {tag} - {name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash(f'Asset {tag} created successfully! 🎉', 'success')
    return redirect(url_for('assets.list_assets'))

@assets_bp.route('/edit/<int:asset_id>', methods=['POST'])
def edit_asset(asset_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    asset = Asset.query.get_or_404(asset_id)
    
    asset.name = request.form.get('name', asset.name)
    asset.serial_number = request.form.get('serial', asset.serial_number)
    asset.category_id = int(request.form.get('category')) if request.form.get('category') else asset.category_id
    asset.department_id = int(request.form.get('department')) if request.form.get('department') else asset.department_id
    asset.location = request.form.get('location', asset.location)
    asset.cost = float(request.form.get('cost')) if request.form.get('cost') else asset.cost
    
    purchase_date = request.form.get('purchase_date', '')
    if purchase_date:
        try:
            asset.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        except:
            pass
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(f"asset_{asset.tag}_{file.filename}")
            filepath = os.path.join('static/uploads/assets', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            asset.image = f'/static/uploads/assets/{filename}'
    
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='update_asset',
        resource_type='asset',
        resource_id=asset.id,
        details=f'Updated asset {asset.tag} - {asset.name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Asset {asset.tag} updated successfully! ✅', 'success')
    return redirect(url_for('assets.view_asset', asset_id=asset.id))

@assets_bp.route('/delete/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user.is_admin() and not user.is_manager():
        return jsonify({'error': 'Permission denied'}), 403
    
    asset = Asset.query.get_or_404(asset_id)
    
    # Check if asset is allocated
    if asset.is_allocated():
        return jsonify({'error': 'Cannot delete allocated asset. Return it first.'}), 400
    
    tag = asset.tag
    name = asset.name
    
    db.session.delete(asset)
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='delete_asset',
        resource_type='asset',
        resource_id=asset_id,
        details=f'Deleted asset {tag} - {name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Asset {tag} deleted successfully.'})

@assets_bp.route('/api/assets')
def api_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    assets = Asset.query.all()
    return jsonify([a.to_dict() for a in assets])

@assets_bp.route('/api/assets/<int:asset_id>')
def api_asset(asset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    asset = Asset.query.get_or_404(asset_id)
    return jsonify(asset.to_dict())

@assets_bp.route('/api/categories')
def api_categories():
    categories = AssetCategory.query.all()
    return jsonify([c.to_dict() for c in categories])

@assets_bp.route('/api/departments')
def api_departments():
    departments = Department.query.all()
    return jsonify([d.to_dict() for d in departments])