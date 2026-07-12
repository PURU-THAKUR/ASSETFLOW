from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import Asset, ResourceBooking, User, Notification, ActivityLog
from database.database import db
from datetime import datetime, timedelta

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/')
def list_bookings():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get bookings
    bookings = ResourceBooking.query.order_by(
        ResourceBooking.start_time.desc()
    ).all()
    
    # Stats
    today = datetime.now().date()
    today_bookings = ResourceBooking.query.filter(
        db.func.date(ResourceBooking.start_time) == today
    ).count()
    
    booked_resources = ResourceBooking.query.filter(
        ResourceBooking.status == 'Confirmed',
        ResourceBooking.start_time <= datetime.now(),
        ResourceBooking.end_time >= datetime.now()
    ).count()
    
    available_resources = Asset.query.filter_by(status='Available').count()
    
    # Resources for booking
    resources = Asset.query.filter(
        Asset.status.in_(['Available', 'Allocated'])
    ).all()
    
    return render_template('booking.html',
        bookings=bookings,
        today_bookings=today_bookings,
        booked_resources=booked_resources,
        available_resources=available_resources,
        resources=resources,
        upcoming_bookings=bookings[:10]
    )

@booking_bp.route('/create', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        return redirect('/login')
    
    asset_id = request.form.get('asset_id')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    purpose = request.form.get('purpose', '')
    
    if not asset_id or not start_time or not end_time:
        flash('All fields are required.', 'error')
        return redirect(url_for('booking.list_bookings'))
    
    asset = Asset.query.get(asset_id)
    if not asset:
        flash('Asset not found.', 'error')
        return redirect(url_for('booking.list_bookings'))
    
    try:
        start = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        end = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
    except:
        flash('Invalid date format.', 'error')
        return redirect(url_for('booking.list_bookings'))
    
    if start >= end:
        flash('End time must be after start time.', 'error')
        return redirect(url_for('booking.list_bookings'))
    
    if start < datetime.now():
        flash('Cannot book in the past.', 'error')
        return redirect(url_for('booking.list_bookings'))
    
    # Validate booking
    from ai.rule_engine import RuleEngine
    rule_engine = RuleEngine()
    validation = rule_engine.validate_booking(asset_id, start, end)
    
    if not validation['valid']:
        flash(validation['error'], 'error')
        return redirect(url_for('booking.list_bookings'))
    
    # Create booking
    booking = ResourceBooking(
        asset_id=asset_id,
        user_id=session['user_id'],
        start_time=start,
        end_time=end,
        purpose=purpose,
        status='Confirmed'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=session['user_id'],
        title='Booking Confirmed',
        message=f'{asset.name} booked from {start.strftime("%I:%M %p")} to {end.strftime("%I:%M %p")}',
        type='booking',
        icon='📅',
        link=f'/booking/view/{booking.id}'
    )
    db.session.add(notification)
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='create_booking',
        resource_type='booking',
        resource_id=booking.id,
        details=f'Booked {asset.name} from {start} to {end}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash(f'{asset.name} booked successfully! 🎉', 'success')
    return redirect(url_for('booking.list_bookings'))

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    booking = ResourceBooking.query.get_or_404(booking_id)
    
    if booking.user_id != session['user_id']:
        user = User.query.get(session['user_id'])
        if not user.is_manager() and not user.is_admin():
            flash('Permission denied.', 'error')
            return redirect(url_for('booking.list_bookings'))
    
    booking.status = 'Cancelled'
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=booking.user_id,
        title='Booking Cancelled',
        message=f'{booking.asset.name} booking has been cancelled.',
        type='booking',
        icon='🚫',
        link=f'/booking/view/{booking.id}'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('booking.list_bookings'))

@booking_bp.route('/api/bookings')
def api_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookings = ResourceBooking.query.all()
    return jsonify([b.to_dict() for b in bookings])

@booking_bp.route('/api/bookings/calendar')
def api_calendar_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = ResourceBooking.query.filter_by(status='Confirmed')
    
    if start:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        query = query.filter(ResourceBooking.start_time >= start_date)
    
    if end:
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        query = query.filter(ResourceBooking.end_time <= end_date)
    
    bookings = query.all()
    
    return jsonify([{
        'id': b.id,
        'title': f'{b.asset.name} - {b.user.fullname}',
        'start': b.start_time.isoformat() if b.start_time else None,
        'end': b.end_time.isoformat() if b.end_time else None,
        'color': '#6C63FF',
        'extendedProps': {
            'purpose': b.purpose,
            'asset_id': b.asset_id,
            'user_id': b.user_id
        }
    } for b in bookings])