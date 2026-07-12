from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database.models import Notification
from database.database import db

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
def list_notifications():
    if 'user_id' not in session:
        return redirect('/login')
    
    notifications = Notification.query.filter_by(
        user_id=session['user_id']
    ).order_by(Notification.created_at.desc()).all()
    
    unread_count = Notification.query.filter_by(
        user_id=session['user_id'],
        read=False
    ).count()
    
    return render_template('notifications.html',
        notifications=notifications,
        unread_count=unread_count
    )

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@notifications_bp.route('/mark-all-read', methods=['POST'])
def mark_all_read():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    Notification.query.filter_by(
        user_id=session['user_id'],
        read=False
    ).update({'read': True})
    
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@notifications_bp.route('/api/unread-count')
def api_unread_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    count = Notification.query.filter_by(
        user_id=session['user_id'],
        read=False
    ).count()
    
    return jsonify({'count': count})