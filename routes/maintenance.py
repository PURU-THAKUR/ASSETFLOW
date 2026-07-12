from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import Asset, MaintenanceRequest, User, Notification, ActivityLog
from database.database import db
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
def list_maintenance():
    if 'user_id' not in session:
        return redirect('/login')
    
    requests = MaintenanceRequest.query.order_by(
        MaintenanceRequest.created_at.desc()
    ).all()
    
    pending = MaintenanceRequest.query.filter_by(status='Pending').count()
    in_progress = MaintenanceRequest.query.filter_by(status='In Progress').count()
    completed = MaintenanceRequest.query.filter_by(status='Completed').count()
    
    assets = Asset.query.all()
    
    return render_template('maintenance.html',
        maintenance_requests=requests,
        pending_maintenance=pending,
        in_progress=in_progress,
        completed_maintenance=completed,
        assets=assets
    )

@maintenance_bp.route('/raise', methods=['POST'])
def raise_request():
    if 'user_id' not in session:
        return redirect('/login')
    
    asset_id = request.form.get('asset_id')
    issue = request.form.get('issue', '').strip()
    priority = request.form.get('priority', 'Medium')
    
    if not asset_id or not issue:
        flash('Please provide all required information.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    asset = Asset.query.get(asset_id)
    if not asset:
        flash('Asset not found.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    # Create maintenance request
    request_obj = MaintenanceRequest(
        asset_id=asset_id,
        user_id=session['user_id'],
        issue=issue,
        priority=priority,
        status='Pending'
    )
    
    db.session.add(request_obj)
    
    # Update asset status
    asset.status = 'Maintenance'
    
    db.session.commit()
    
    # Create notification for manager
    managers = User.query.filter_by(role='Manager').all()
    for manager in managers:
        notification = Notification(
            user_id=manager.id,
            title='Maintenance Request',
            message=f'Maintenance request for {asset.tag} - {asset.name} (Priority: {priority})',
            type='maintenance',
            icon='🔧',
            link=f'/maintenance/view/{request_obj.id}'
        )
        db.session.add(notification)
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='raise_maintenance',
        resource_type='maintenance',
        resource_id=request_obj.id,
        details=f'Raised maintenance for {asset.tag} - Priority: {priority}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash('Maintenance request raised successfully! 🔧', 'success')
    return redirect(url_for('maintenance.list_maintenance'))

@maintenance_bp.route('/approve/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user.is_manager() and not user.is_admin():
        flash('Permission denied.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    request_obj = MaintenanceRequest.query.get_or_404(request_id)
    
    if request_obj.status != 'Pending':
        flash('Request already processed.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    request_obj.status = 'In Progress'
    request_obj.assigned_to = session['user_id']
    db.session.commit()
    
    # Notify requester
    notification = Notification(
        user_id=request_obj.user_id,
        title='Maintenance Approved',
        message=f'Maintenance request for {request_obj.asset.tag} has been approved and is in progress.',
        type='maintenance',
        icon='✅',
        link=f'/maintenance/view/{request_obj.id}'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Maintenance request approved! 🔧', 'success')
    return redirect(url_for('maintenance.list_maintenance'))

@maintenance_bp.route('/complete/<int:request_id>', methods=['POST'])
def complete_request(request_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user.is_manager() and not user.is_admin():
        flash('Permission denied.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    request_obj = MaintenanceRequest.query.get_or_404(request_id)
    resolution = request.form.get('resolution', '').strip()
    
    if request_obj.status != 'In Progress':
        flash('Request must be in progress to complete.', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    
    request_obj.status = 'Completed'
    request_obj.resolution = resolution
    request_obj.resolved_at = datetime.now()
    
    # Update asset health
    asset = request_obj.asset
    asset.status = 'Available'
    if asset.health_score < 90:
        asset.health_score = min(100, asset.health_score + 10)
    
    db.session.commit()
    
    # Notify requester
    notification = Notification(
        user_id=request_obj.user_id,
        title='Maintenance Completed',
        message=f'Maintenance for {request_obj.asset.tag} has been completed.',
        type='maintenance',
        icon='✅',
        link=f'/maintenance/view/{request_obj.id}'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Maintenance completed successfully! ✅', 'success')
    return redirect(url_for('maintenance.list_maintenance'))

@maintenance_bp.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user.is_manager() and not user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    request_obj = MaintenanceRequest.query.get_or_404(request_id)
    
    # Reset asset status if still in maintenance
    if request_obj.asset.status == 'Maintenance':
        request_obj.asset.status = 'Available'
    
    db.session.delete(request_obj)
    db.session.commit()
    
    return jsonify({'success': True})

@maintenance_bp.route('/api/maintenance')
def api_maintenance():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    requests = MaintenanceRequest.query.all()
    return jsonify([r.to_dict() for r in requests])