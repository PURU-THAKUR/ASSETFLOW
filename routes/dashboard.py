from flask import Blueprint, render_template, session, jsonify, request
from database.models import Asset, AssetAllocation, MaintenanceRequest, ResourceBooking, User, Department, Notification, ActivityLog
from database.database import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    
    # Stats
    total_assets = Asset.query.count()
    available_assets = Asset.query.filter_by(status='Available').count()
    allocated_assets = Asset.query.filter_by(status='Allocated').count()
    maintenance_count = Asset.query.filter_by(status='Maintenance').count()
    lost_count = Asset.query.filter_by(status='Lost').count()
    total_bookings = ResourceBooking.query.count()
    
    # Upcoming returns (next 7 days)
    upcoming_returns = AssetAllocation.query.filter(
        AssetAllocation.return_date >= datetime.now(),
        AssetAllocation.return_date <= datetime.now() + timedelta(days=7),
        AssetAllocation.status == 'Active'
    ).count()
    
    # Overdue
    overdue = AssetAllocation.query.filter(
        AssetAllocation.return_date < datetime.now(),
        AssetAllocation.status == 'Active'
    ).count()
    
    # Recent activity (last 20)
    recent_activities = []
    
    # Recent allocations
    recent_allocations = AssetAllocation.query.order_by(
        AssetAllocation.created_at.desc()
    ).limit(5).all()
    
    for alloc in recent_allocations:
        recent_activities.append({
            'icon': '📋',
            'message': f'Asset {alloc.asset.tag} allocated to {alloc.user.fullname}',
            'time': alloc.created_at.strftime('%b %d, %I:%M %p') if alloc.created_at else 'Just now'
        })
    
    # Recent bookings
    recent_bookings = ResourceBooking.query.order_by(
        ResourceBooking.created_at.desc()
    ).limit(3).all()
    
    for booking in recent_bookings:
        recent_activities.append({
            'icon': '📅',
            'message': f'{booking.asset.name} booked by {booking.user.fullname}',
            'time': booking.created_at.strftime('%b %d, %I:%M %p') if booking.created_at else 'Just now'
        })
    
    # Recent maintenance
    recent_maintenance = MaintenanceRequest.query.order_by(
        MaintenanceRequest.created_at.desc()
    ).limit(3).all()
    
    for req in recent_maintenance:
        recent_activities.append({
            'icon': '🔧',
            'message': f'Maintenance request for {req.asset.name} - {req.status}',
            'time': req.created_at.strftime('%b %d, %I:%M %p') if req.created_at else 'Just now'
        })
    
    # Sort by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]
    
    # Get notifications count
    notifications_count = Notification.query.filter_by(
        user_id=user.id,
        read=False
    ).count()
    
    # Department data for chart
    dept_data = db.session.query(
        Department.name,
        func.count(Asset.id).label('count')
    ).join(Asset, Asset.department_id == Department.id, isouter=True)\
    .group_by(Department.id).all()
    
    departments = [d.name for d in dept_data]
    dept_counts = [d.count or 0 for d in dept_data]
    
    # Asset status distribution
    status_data = {
        'Available': available_assets,
        'Allocated': allocated_assets,
        'Maintenance': maintenance_count,
        'Lost': lost_count
    }
    
    return render_template('dashboard.html',
        user=user,
        total_assets=total_assets,
        available_assets=available_assets,
        allocated_assets=allocated_assets,
        maintenance_count=maintenance_count,
        lost_count=lost_count,
        total_bookings=total_bookings,
        upcoming_returns=upcoming_returns,
        overdue=overdue,
        recent_activities=recent_activities,
        notifications_count=notifications_count,
        departments=departments,
        dept_counts=dept_counts,
        status_data=status_data
    )

@dashboard_bp.route('/api/dashboard/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_assets = Asset.query.count()
    available = Asset.query.filter_by(status='Available').count()
    allocated = Asset.query.filter_by(status='Allocated').count()
    maintenance = Asset.query.filter_by(status='Maintenance').count()
    
    return jsonify({
        'total': total_assets,
        'available': available,
        'allocated': allocated,
        'maintenance': maintenance,
        'utilization': round((allocated / total_assets * 100) if total_assets > 0 else 0, 1)
    })

@dashboard_bp.route('/api/dashboard/activities')
def get_activities():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    activities = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(20).all()
    
    return jsonify([{
        'id': a.id,
        'action': a.action,
        'details': a.details,
        'user': a.user.fullname if a.user else 'System',
        'created_at': a.created_at.isoformat() if a.created_at else None,
        'time_ago': a.created_at.strftime('%b %d, %I:%M %p') if a.created_at else 'Just now'
    } for a in activities])

@dashboard_bp.route('/api/dashboard/notifications')
def get_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notifications = Notification.query.filter_by(
        user_id=session['user_id']
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify([n.to_dict() for n in notifications])