from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import Asset, AssetAllocation, User, Notification, ActivityLog, TransferRequest
from database.database import db
from datetime import datetime, timedelta

allocation_bp = Blueprint('allocation', __name__, url_prefix='/allocation')

@allocation_bp.route('/')
def list_allocations():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get all active allocations
    allocations = AssetAllocation.query.order_by(
        AssetAllocation.created_at.desc()
    ).all()
    
    total_allocated = AssetAllocation.query.filter_by(status='Active').count()
    active_allocations = total_allocated
    pending_returns = AssetAllocation.query.filter(
        AssetAllocation.return_date < datetime.now(),
        AssetAllocation.status == 'Active'
    ).count()
    
    return render_template('allocation.html',
        allocations=allocations,
        total_allocated=total_allocated,
        active_allocations=active_allocations,
        pending_returns=pending_returns
    )

@allocation_bp.route('/allocate', methods=['POST'])
def allocate_asset():
    if 'user_id' not in session:
        return redirect('/login')
    
    asset_id = request.form.get('asset_id')
    employee_id = request.form.get('employee_id')
    allocated_date = request.form.get('allocated_date')
    return_date = request.form.get('return_date')
    notes = request.form.get('notes', '')
    
    if not asset_id or not employee_id:
        flash('Please select both asset and employee.', 'error')
        return redirect(url_for('allocation.list_allocations'))
    
    asset = Asset.query.get(asset_id)
    user = User.query.get(employee_id)
    
    if not asset or not user:
        flash('Asset or employee not found.', 'error')
        return redirect(url_for('allocation.list_allocations'))
    
    if not asset.is_available():
        flash(f'Asset {asset.tag} is not available for allocation.', 'error')
        return redirect(url_for('allocation.list_allocations'))
    
    # Validate allocation
    from ai.rule_engine import RuleEngine
    rule_engine = RuleEngine()
    validation = rule_engine.validate_allocation(asset_id, employee_id)
    
    if not validation['valid']:
        flash(validation['error'], 'error')
        return redirect(url_for('allocation.list_allocations'))
    
    # Create allocation
    allocation = AssetAllocation(
        asset_id=asset_id,
        user_id=employee_id,
        notes=notes,
        status='Active'
    )
    
    if allocated_date:
        try:
            allocation.allocated_date = datetime.strptime(allocated_date, '%Y-%m-%d')
        except:
            pass
    
    if return_date:
        try:
            allocation.return_date = datetime.strptime(return_date, '%Y-%m-%d')
        except:
            pass
    
    # Update asset status
    asset.status = 'Allocated'
    
    db.session.add(allocation)
    db.session.commit()
    
    # Create notification for employee
    notification = Notification(
        user_id=user.id,
        title='Asset Allocated',
        message=f'Asset {asset.tag} - {asset.name} has been allocated to you.',
        type='allocation',
        icon='📋',
        link=f'/allocation/view/{allocation.id}'
    )
    db.session.add(notification)
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='allocate_asset',
        resource_type='allocation',
        resource_id=allocation.id,
        details=f'Allocated {asset.tag} to {user.fullname}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash(f'Asset {asset.tag} allocated to {user.fullname} successfully! 🎉', 'success')
    return redirect(url_for('allocation.list_allocations'))

@allocation_bp.route('/return/<int:allocation_id>', methods=['POST'])
def return_asset(allocation_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    allocation = AssetAllocation.query.get_or_404(allocation_id)
    condition = request.form.get('condition', 'Good')
    
    if allocation.status != 'Active':
        flash('This allocation is already completed.', 'error')
        return redirect(url_for('allocation.list_allocations'))
    
    # Update allocation
    allocation.status = 'Returned'
    allocation.actual_return_date = datetime.now()
    
    # Update asset status
    asset = allocation.asset
    asset.status = 'Available'
    
    # Update health score based on condition
    if condition == 'Good':
        asset.health_score = min(100, (asset.health_score or 100) + 5)
    elif condition == 'Fair':
        asset.health_score = max(0, (asset.health_score or 100) - 5)
    elif condition == 'Poor':
        asset.health_score = max(0, (asset.health_score or 100) - 15)
    
    db.session.commit()
    
    # Create notification for employee
    notification = Notification(
        user_id=allocation.user_id,
        title='Asset Returned',
        message=f'Asset {asset.tag} - {asset.name} has been returned successfully.',
        type='return',
        icon='↩️',
        link=f'/assets/view/{asset.id}'
    )
    db.session.add(notification)
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='return_asset',
        resource_type='allocation',
        resource_id=allocation.id,
        details=f'Returned {asset.tag} - Condition: {condition}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash(f'Asset {asset.tag} returned successfully! ✅', 'success')
    return redirect(url_for('allocation.list_allocations'))

@allocation_bp.route('/transfer/<int:allocation_id>', methods=['GET', 'POST'])
def transfer_asset(allocation_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    allocation = AssetAllocation.query.get_or_404(allocation_id)
    
    if request.method == 'POST':
        to_user_id = request.form.get('to_user_id')
        reason = request.form.get('reason', '')
        
        if not to_user_id:
            flash('Please select an employee.', 'error')
            return redirect(url_for('allocation.transfer_asset', allocation_id=allocation_id))
        
        to_user = User.query.get(to_user_id)
        if not to_user:
            flash('Employee not found.', 'error')
            return redirect(url_for('allocation.transfer_asset', allocation_id=allocation_id))
        
        # Create transfer request
        transfer = TransferRequest(
            allocation_id=allocation_id,
            from_user_id=allocation.user_id,
            to_user_id=to_user_id,
            reason=reason,
            status='Pending'
        )
        
        db.session.add(transfer)
        db.session.commit()
        
        # Notify manager
        managers = User.query.filter_by(role='Manager').all()
        for manager in managers:
            notification = Notification(
                user_id=manager.id,
                title='Transfer Request',
                message=f'Transfer request for {allocation.asset.tag} from {allocation.user.fullname} to {to_user.fullname}',
                type='transfer',
                icon='🔄',
                link=f'/allocation/transfer-requests'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash(f'Transfer request submitted for approval. ✅', 'success')
        return redirect(url_for('allocation.list_allocations'))
    
    # GET - show transfer form
    employees = User.query.filter_by(role='Employee').all()
    return render_template('transfer.html',
        allocation=allocation,
        employees=employees
    )

@allocation_bp.route('/transfer-requests')
def transfer_requests():
    if 'user_id' not in session:
        return redirect('/login')
    
    requests = TransferRequest.query.order_by(
        TransferRequest.created_at.desc()
    ).all()
    
    return render_template('transfer_requests.html', requests=requests)

@allocation_bp.route('/transfer-requests/<int:request_id>/approve', methods=['POST'])
def approve_transfer(request_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user.is_manager() and not user.is_admin():
        flash('Permission denied.', 'error')
        return redirect(url_for('allocation.transfer_requests'))
    
    transfer = TransferRequest.query.get_or_404(request_id)
    
    if transfer.status != 'Pending':
        flash('Request already processed.', 'error')
        return redirect(url_for('allocation.transfer_requests'))
    
    # Update transfer
    transfer.status = 'Approved'
    transfer.approved_by = user.id
    
    # Update allocation
    allocation = transfer.allocation
    allocation.user_id = transfer.to_user_id
    allocation.updated_at = datetime.now()
    
    db.session.commit()
    
    # Notify users
    for user_id in [transfer.from_user_id, transfer.to_user_id]:
        notification = Notification(
            user_id=user_id,
            title='Transfer Approved',
            message=f'Asset {allocation.asset.tag} transfer has been approved.',
            type='transfer',
            icon='✅',
            link=f'/allocation/view/{allocation.id}'
        )
        db.session.add(notification)
    
    db.session.commit()
    
    flash('Transfer approved successfully! ✅', 'success')
    return redirect(url_for('allocation.transfer_requests'))

@allocation_bp.route('/transfer-requests/<int:request_id>/reject', methods=['POST'])
def reject_transfer(request_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user.is_manager() and not user.is_admin():
        flash('Permission denied.', 'error')
        return redirect(url_for('allocation.transfer_requests'))
    
    transfer = TransferRequest.query.get_or_404(request_id)
    
    if transfer.status != 'Pending':
        flash('Request already processed.', 'error')
        return redirect(url_for('allocation.transfer_requests'))
    
    transfer.status = 'Rejected'
    transfer.approved_by = user.id
    
    db.session.commit()
    
    # Notify users
    for user_id in [transfer.from_user_id, transfer.to_user_id]:
        notification = Notification(
            user_id=user_id,
            title='Transfer Rejected',
            message=f'Asset {transfer.allocation.asset.tag} transfer request was rejected.',
            type='transfer',
            icon='❌'
        )
        db.session.add(notification)
    
    db.session.commit()
    
    flash('Transfer rejected.', 'info')
    return redirect(url_for('allocation.transfer_requests'))

@allocation_bp.route('/api/allocations')
def api_allocations():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    allocations = AssetAllocation.query.all()
    return jsonify([a.to_dict() for a in allocations])

@allocation_bp.route('/api/available-assets')
def api_available_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    assets = Asset.query.filter_by(status='Available').all()
    return jsonify([a.to_dict() for a in assets])