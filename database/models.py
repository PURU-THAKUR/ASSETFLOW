# ============================================
# IMPORTANT: db is imported from app.py
# ============================================
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(50))
    role = db.Column(db.String(50), default='Employee')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    avatar = db.Column(db.String(255))
    
    # Relationships
    assets_allocated = db.relationship('AssetAllocation', foreign_keys='AssetAllocation.user_id', backref='user', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', foreign_keys='MaintenanceRequest.user_id', backref='user', lazy=True)
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy=True)
    bookings = db.relationship('ResourceBooking', foreign_keys='ResourceBooking.user_id', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'Admin'
    
    def is_manager(self):
        return self.role in ['Admin', 'Manager']
    
    def is_employee(self):
        return self.role == 'Employee'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'employee_id': self.employee_id,
            'department': self.department,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'avatar': self.avatar
        }
    
    def __repr__(self):
        return f'<User {self.fullname}>'


class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employees = db.relationship('User', foreign_keys='User.department', primaryjoin='Department.name == User.department', backref='dept', lazy=True)
    assets = db.relationship('Asset', foreign_keys='Asset.department_id', backref='dept', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'employee_count': len(self.employees),
            'asset_count': len(self.assets)
        }
    
    def __repr__(self):
        return f'<Department {self.name}>'


class AssetCategory(db.Model):
    __tablename__ = 'asset_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assets = db.relationship('Asset', foreign_keys='Asset.category_id', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'asset_count': len(self.assets)
        }
    
    def __repr__(self):
        return f'<AssetCategory {self.name}>'


class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('asset_categories.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Available')
    cost = db.Column(db.Float)
    purchase_date = db.Column(db.DateTime)
    warranty_expiry = db.Column(db.DateTime)
    image = db.Column(db.String(255))
    qr_code = db.Column(db.String(255))
    health_score = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    allocations = db.relationship('AssetAllocation', foreign_keys='AssetAllocation.asset_id', backref='asset', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', foreign_keys='MaintenanceRequest.asset_id', backref='asset', lazy=True)
    bookings = db.relationship('ResourceBooking', foreign_keys='ResourceBooking.asset_id', backref='asset', lazy=True)
    
    def is_available(self):
        return self.status == 'Available'
    
    def is_allocated(self):
        return self.status == 'Allocated'
    
    def is_maintenance(self):
        return self.status == 'Maintenance'
    
    def get_current_allocation(self):
        return AssetAllocation.query.filter_by(asset_id=self.id, status='Active').first()
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'name': self.name,
            'serial_number': self.serial_number,
            'category': self.category.name if self.category else None,
            'category_id': self.category_id,
            'department': self.dept.name if self.dept else None,
            'department_id': self.department_id,
            'location': self.location,
            'status': self.status,
            'cost': self.cost,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'health_score': self.health_score,
            'image': self.image,
            'qr_code': self.qr_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Asset {self.tag} - {self.name}>'


class AssetAllocation(db.Model):
    __tablename__ = 'asset_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    allocated_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    actual_return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Active')
    notes = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transfer_requests = db.relationship('TransferRequest', foreign_keys='TransferRequest.allocation_id', backref='allocation', lazy=True)
    
    def is_active(self):
        return self.status == 'Active'
    
    def is_returned(self):
        return self.status == 'Returned'
    
    def is_overdue(self):
        return self.status == 'Active' and self.return_date and self.return_date < datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_tag': self.asset.tag if self.asset else None,
            'asset_name': self.asset.name if self.asset else None,
            'user_id': self.user_id,
            'employee_name': self.user.fullname if self.user else None,
            'employee_email': self.user.email if self.user else None,
            'department': self.user.department if self.user else None,
            'allocated_date': self.allocated_date.isoformat() if self.allocated_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'actual_return_date': self.actual_return_date.isoformat() if self.actual_return_date else None,
            'status': self.status,
            'is_overdue': self.is_overdue(),
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<AssetAllocation {self.asset.tag} -> {self.user.fullname}>'


class TransferRequest(db.Model):
    __tablename__ = 'transfer_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('asset_allocations.id'))
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='transfer_from', lazy=True)
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='transfer_to', lazy=True)
    approver = db.relationship('User', foreign_keys=[approved_by], backref='transfer_approved', lazy=True)
    
    def is_pending(self):
        return self.status == 'Pending'
    
    def is_approved(self):
        return self.status == 'Approved'
    
    def is_rejected(self):
        return self.status == 'Rejected'
    
    def to_dict(self):
        return {
            'id': self.id,
            'allocation_id': self.allocation_id,
            'asset_tag': self.allocation.asset.tag if self.allocation else None,
            'asset_name': self.allocation.asset.name if self.allocation else None,
            'from_user': self.from_user.fullname if self.from_user else None,
            'to_user': self.to_user.fullname if self.to_user else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TransferRequest {self.id} - {self.status}>'


class ResourceBooking(db.Model):
    __tablename__ = 'resource_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_confirmed(self):
        return self.status == 'Confirmed'
    
    def is_cancelled(self):
        return self.status == 'Cancelled'
    
    def is_completed(self):
        return self.status == 'Completed'
    
    def is_active(self):
        now = datetime.now()
        return self.status == 'Confirmed' and self.start_time <= now <= self.end_time
    
    def check_conflict(self, start, end):
        return self.status == 'Confirmed' and (
            (start < self.end_time and end > self.start_time) or
            (start >= self.start_time and start < self.end_time) or
            (end > self.start_time and end <= self.end_time)
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'resource_name': self.asset.name if self.asset else None,
            'resource_tag': self.asset.tag if self.asset else None,
            'user_id': self.user_id,
            'booked_by': self.user.fullname if self.user else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ResourceBooking {self.asset.name} - {self.user.fullname}>'


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    issue = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Pending')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_maintenance', lazy=True)
    
    def is_pending(self):
        return self.status == 'Pending'
    
    def is_approved(self):
        return self.status == 'Approved'
    
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    def is_completed(self):
        return self.status == 'Completed'
    
    def is_rejected(self):
        return self.status == 'Rejected'
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'asset_tag': self.asset.tag if self.asset else None,
            'user_id': self.user_id,
            'reported_by': self.user.fullname if self.user else None,
            'issue': self.issue,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'assigned_to_name': self.assignee.fullname if self.assignee else None,
            'resolution': self.resolution,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.id} - {self.asset.name}>'


class AuditCycle(db.Model):
    __tablename__ = 'audit_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Scheduled')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='audit_created', lazy=True)
    items = db.relationship('AuditItem', foreign_keys='AuditItem.audit_cycle_id', backref='audit', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'item_count': len(self.items)
        }


class AuditItem(db.Model):
    __tablename__ = 'audit_items'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_cycle_id = db.Column(db.Integer, db.ForeignKey('audit_cycles.id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    expected_location = db.Column(db.String(100))
    actual_location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')
    notes = db.Column(db.String(200))
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    
    verifier = db.relationship('User', foreign_keys=[verified_by], backref='audit_verified', lazy=True)
    asset = db.relationship('Asset', foreign_keys=[asset_id], backref='audit_items', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'audit_cycle_id': self.audit_cycle_id,
            'asset_id': self.asset_id,
            'asset_tag': self.asset.tag if self.asset else None,
            'asset_name': self.asset.name if self.asset else None,
            'expected_location': self.expected_location,
            'actual_location': self.actual_location,
            'status': self.status,
            'notes': self.notes,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50))
    icon = db.Column(db.String(10))
    read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_read(self):
        self.read = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'icon': self.icon,
            'read': self.read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'time_ago': self.time_ago()
        }
    
    def time_ago(self):
        if not self.created_at:
            return 'Just now'
        diff = datetime.utcnow() - self.created_at
        if diff.total_seconds() < 60:
            return 'Just now'
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() // 60)
            return f'{mins}m ago'
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() // 3600)
            return f'{hours}h ago'
        elif diff.total_seconds() < 604800:
            days = int(diff.total_seconds() // 86400)
            return f'{days}d ago'
        else:
            return self.created_at.strftime('%b %d')
    
    def __repr__(self):
        return f'<Notification {self.title}>'


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='activities', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.fullname if self.user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id}>'