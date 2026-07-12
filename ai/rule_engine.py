from database.models import Asset, AssetAllocation, MaintenanceRequest, Notification
from database.database import db
from datetime import datetime, timedelta

class RuleEngine:
    """Business rule engine for automated actions and validations"""
    
    def __init__(self):
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """Load all business rules"""
        self.rules = [
            {
                'name': 'asset_overdue_check',
                'description': 'Check for overdue assets daily',
                'action': self._check_overdue_assets,
                'schedule': 'daily'
            },
            {
                'name': 'maintenance_reminder',
                'description': 'Send reminders for pending maintenance',
                'action': self._check_maintenance_reminders,
                'schedule': 'daily'
            },
            {
                'name': 'low_health_alert',
                'description': 'Alert for low health assets',
                'action': self._check_low_health_assets,
                'schedule': 'daily'
            },
            {
                'name': 'return_reminder',
                'description': 'Send return reminders before due date',
                'action': self._check_return_reminders,
                'schedule': 'daily'
            },
            {
                'name': 'asset_utilization_check',
                'description': 'Check asset utilization patterns',
                'action': self._check_utilization,
                'schedule': 'weekly'
            }
        ]
    
    def run_all_rules(self):
        """Run all rules"""
        results = []
        for rule in self.rules:
            try:
                result = rule['action']()
                results.append({
                    'rule': rule['name'],
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'rule': rule['name'],
                    'success': False,
                    'error': str(e)
                })
        return results
    
    def _check_overdue_assets(self):
        """Check for overdue assets and create notifications"""
        overdue = AssetAllocation.query.filter(
            AssetAllocation.return_date < datetime.now(),
            AssetAllocation.status == 'Active'
        ).all()
        
        notifications_created = 0
        for alloc in overdue:
            if alloc.user:
                notification = Notification(
                    user_id=alloc.user.id,
                    title='Asset Overdue',
                    message=f'Asset {alloc.asset.tag} - {alloc.asset.name} is overdue by {(datetime.now() - alloc.return_date).days} days',
                    type='overdue',
                    icon='⚠️',
                    link=f'/allocations/{alloc.id}'
                )
                db.session.add(notification)
                notifications_created += 1
        
        db.session.commit()
        return {
            'overdue_count': len(overdue),
            'notifications_created': notifications_created
        }
    
    def _check_maintenance_reminders(self):
        """Check pending maintenance and create reminders"""
        pending = MaintenanceRequest.query.filter_by(status='Pending').all()
        
        notifications_created = 0
        for req in pending:
            if req.user:
                notification = Notification(
                    user_id=req.user.id,
                    title='Maintenance Pending',
                    message=f'Maintenance request for {req.asset.name} is pending for approval',
                    type='maintenance',
                    icon='🔧',
                    link=f'/maintenance/{req.id}'
                )
                db.session.add(notification)
                notifications_created += 1
        
        db.session.commit()
        return {
            'pending_count': len(pending),
            'notifications_created': notifications_created
        }
    
    def _check_low_health_assets(self):
        """Check assets with low health score"""
        low_health = Asset.query.filter(Asset.health_score < 40).all()
        
        notifications_created = 0
        for asset in low_health:
            # Notify manager
            managers = User.query.filter_by(role='Manager').all()
            for manager in managers:
                notification = Notification(
                    user_id=manager.id,
                    title='Low Health Asset Alert',
                    message=f'Asset {asset.tag} - {asset.name} has low health score ({asset.health_score}%)',
                    type='health',
                    icon='💚',
                    link=f'/assets/view/{asset.id}'
                )
                db.session.add(notification)
                notifications_created += 1
        
        db.session.commit()
        return {
            'low_health_count': len(low_health),
            'notifications_created': notifications_created
        }
    
    def _check_return_reminders(self):
        """Send reminders for upcoming returns"""
        upcoming = AssetAllocation.query.filter(
            AssetAllocation.return_date.between(
                datetime.now(),
                datetime.now() + timedelta(days=3)
            ),
            AssetAllocation.status == 'Active'
        ).all()
        
        notifications_created = 0
        for alloc in upcoming:
            if alloc.user:
                days_left = (alloc.return_date - datetime.now()).days
                notification = Notification(
                    user_id=alloc.user.id,
                    title='Asset Return Reminder',
                    message=f'Asset {alloc.asset.tag} - {alloc.asset.name} is due for return in {days_left} days',
                    type='reminder',
                    icon='📅',
                    link=f'/allocations/{alloc.id}'
                )
                db.session.add(notification)
                notifications_created += 1
        
        db.session.commit()
        return {
            'upcoming_count': len(upcoming),
            'notifications_created': notifications_created
        }
    
    def _check_utilization(self):
        """Check asset utilization patterns"""
        # Find idle assets
        idle = Asset.query.filter(
            Asset.status == 'Available',
            Asset.updated_at < datetime.now() - timedelta(days=30)
        ).limit(10).all()
        
        notifications_created = 0
        for asset in idle:
            # Notify manager
            managers = User.query.filter_by(role='Manager').all()
            for manager in managers[:1]:  # Only first manager to avoid spam
                notification = Notification(
                    user_id=manager.id,
                    title='Idle Asset Detected',
                    message=f'Asset {asset.tag} - {asset.name} has been idle for {(datetime.now() - asset.updated_at).days} days',
                    type='utilization',
                    icon='💡',
                    link=f'/assets/view/{asset.id}'
                )
                db.session.add(notification)
                notifications_created += 1
        
        db.session.commit()
        return {
            'idle_count': len(idle),
            'notifications_created': notifications_created
        }
    
    def validate_allocation(self, asset_id, user_id):
        """Validate if an allocation is allowed"""
        asset = Asset.query.get(asset_id)
        user = User.query.get(user_id)
        
        if not asset or not user:
            return {'valid': False, 'error': 'Asset or user not found'}
        
        if not asset.is_available():
            return {'valid': False, 'error': f'Asset {asset.tag} is not available'}
        
        if not user.is_active:
            return {'valid': False, 'error': 'User is not active'}
        
        # Check if user already has this asset
        existing = AssetAllocation.query.filter_by(
            asset_id=asset_id,
            user_id=user_id,
            status='Active'
        ).first()
        
        if existing:
            return {'valid': False, 'error': 'User already has this asset allocated'}
        
        return {'valid': True}
    
    def validate_booking(self, asset_id, start_time, end_time):
        """Validate if a booking is allowed"""
        asset = Asset.query.get(asset_id)
        
        if not asset:
            return {'valid': False, 'error': 'Asset not found'}
        
        if not asset.is_available() and asset.status != 'Allocated':
            return {'valid': False, 'error': 'Asset is not available for booking'}
        
        # Check for overlapping bookings
        conflicts = ResourceBooking.query.filter(
            ResourceBooking.asset_id == asset_id,
            ResourceBooking.status == 'Confirmed',
            ResourceBooking.start_time < end_time,
            ResourceBooking.end_time > start_time
        ).all()
        
        if conflicts:
            return {
                'valid': False, 
                'error': 'Time slot conflicts with existing booking',
                'conflicts': [b.to_dict() for b in conflicts]
            }
        
        return {'valid': True}
    
    def generate_asset_tag(self):
        """Generate next available asset tag"""
        last_asset = Asset.query.order_by(Asset.id.desc()).first()
        if last_asset and last_asset.tag:
            try:
                num = int(last_asset.tag[3:]) + 1
            except:
                num = 1
        else:
            num = 1
        return f"AF-{str(num).zfill(4)}"