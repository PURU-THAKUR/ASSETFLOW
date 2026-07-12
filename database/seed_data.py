from database.database import db
from database.models import *
from datetime import datetime, timedelta
import random

def generate_asset_tag():
    """Generate a unique asset tag"""
    prefix = 'AF'
    # Get the highest tag number
    all_assets = Asset.query.all()
    max_num = 0
    for asset in all_assets:
        if asset.tag and asset.tag.startswith('AF-'):
            try:
                num = int(asset.tag[3:])
                if num > max_num:
                    max_num = num
            except:
                pass
    return f"{prefix}-{str(max_num + 1).zfill(4)}"

# Rest of seed_data remains same...

def seed_data():
    """Seed database with initial data"""
    
    # Check if data already exists
    if User.query.first():
        print("⚠️ Data already exists. Skipping seed...")
        return
    
    print("🌱 Seeding database with initial data...")
    
    # ============================================
    # 1. Create Departments
    # ============================================
    print("  📁 Creating departments...")
    departments = [
        Department(name='IT', description='Information Technology Department'),
        Department(name='HR', description='Human Resources Department'),
        Department(name='Finance', description='Finance and Accounting Department'),
        Department(name='Marketing', description='Marketing and Communications Department'),
        Department(name='Operations', description='Operations and Logistics Department'),
        Department(name='Sales', description='Sales and Business Development'),
        Department(name='R&D', description='Research and Development')
    ]
    db.session.add_all(departments)
    db.session.commit()
    print(f"  ✅ Created {len(departments)} departments")

    # ============================================
    # 2. Create Asset Categories
    # ============================================
    print("  📂 Creating asset categories...")
    categories = [
        AssetCategory(name='Laptop', icon='💻', description='Portable computers'),
        AssetCategory(name='Desktop', icon='🖥️', description='Desktop computers'),
        AssetCategory(name='Printer', icon='🖨️', description='Printing devices'),
        AssetCategory(name='Projector', icon='📽️', description='Projection equipment'),
        AssetCategory(name='Tablet', icon='📱', description='Tablet devices'),
        AssetCategory(name='Phone', icon='📞', description='Telephone equipment'),
        AssetCategory(name='Scanner', icon='📄', description='Scanning devices'),
        AssetCategory(name='Chair', icon='🪑', description='Office chairs'),
        AssetCategory(name='Vehicle', icon='🚗', description='Company vehicles'),
        AssetCategory(name='Meeting Room', icon='🏢', description='Meeting and conference rooms'),
        AssetCategory(name='Monitor', icon='🖥️', description='Display monitors'),
        AssetCategory(name='Keyboard', icon='⌨️', description='Input devices')
    ]
    db.session.add_all(categories)
    db.session.commit()
    print(f"  ✅ Created {len(categories)} categories")

    # ============================================
    # 3. Create Users
    # ============================================
    print("  👤 Creating users...")
    
    # Admin
    admin = User(
        fullname='Admin User',
        email='admin@assetflow.com',
        employee_id='ADMIN001',
        department='IT',
        role='Admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Manager
    manager = User(
        fullname='Asset Manager',
        email='manager@assetflow.com',
        employee_id='MGR001',
        department='IT',
        role='Manager'
    )
    manager.set_password('manager123')
    db.session.add(manager)
    
    # Employees
    employees_data = [
        ('Rahul Kumar', 'rahul@company.com', 'EMP001', 'IT', 'Employee'),
        ('Aman Singh', 'aman@company.com', 'EMP002', 'HR', 'Employee'),
        ('Priya Sharma', 'priya@company.com', 'EMP003', 'Finance', 'Employee'),
        ('Amit Patel', 'amit@company.com', 'EMP004', 'Marketing', 'Employee'),
        ('Sneha Reddy', 'sneha@company.com', 'EMP005', 'Operations', 'Employee'),
        ('Vikram Singh', 'vikram@company.com', 'EMP006', 'IT', 'Employee'),
        ('Neha Gupta', 'neha@company.com', 'EMP007', 'HR', 'Employee'),
        ('Rajesh Kumar', 'rajesh@company.com', 'EMP008', 'Finance', 'Employee'),
        ('Deepak Sharma', 'deepak@company.com', 'EMP009', 'Marketing', 'Employee'),
        ('Ananya Patel', 'ananya@company.com', 'EMP010', 'Operations', 'Employee'),
        ('Arjun Singh', 'arjun@company.com', 'EMP011', 'IT', 'Employee'),
        ('Meera Reddy', 'meera@company.com', 'EMP012', 'HR', 'Employee'),
        ('Karan Gupta', 'karan@company.com', 'EMP013', 'Finance', 'Employee'),
        ('Riya Sharma', 'riya@company.com', 'EMP014', 'Marketing', 'Employee'),
        ('Akash Kumar', 'akash@company.com', 'EMP015', 'Sales', 'Employee'),
        ('Divya Patel', 'divya@company.com', 'EMP016', 'Sales', 'Employee'),
        ('Suresh Singh', 'suresh@company.com', 'EMP017', 'R&D', 'Employee'),
        ('Kavya Reddy', 'kavya@company.com', 'EMP018', 'R&D', 'Employee'),
    ]
    
    for name, email, emp_id, dept, role in employees_data:
        user = User(
            fullname=name,
            email=email,
            employee_id=emp_id,
            department=dept,
            role=role
        )
        user.set_password('password123')
        db.session.add(user)
    
    db.session.commit()
    print(f"  ✅ Created {len(employees_data) + 2} users")

    # ============================================
    # 4. Create Assets
    # ============================================
    print("  💻 Creating assets...")
    
    assets_data = [
        ('Dell Latitude 5430', 'DLX12345', 'Laptop', 'IT', 'Floor 2 - IT Lab', 70000),
        ('HP ProBook 450', 'HPX67890', 'Laptop', 'IT', 'Floor 2 - IT Lab', 65000),
        ('Lenovo ThinkPad X1', 'LEN11223', 'Laptop', 'Finance', 'Floor 1 - Finance', 80000),
        ('Apple MacBook Pro', 'APL44556', 'Laptop', 'Marketing', 'Floor 3 - Marketing', 120000),
        ('Dell XPS 13', 'DLX99882', 'Laptop', 'IT', 'Floor 2 - IT Lab', 75000),
        ('HP Pavilion', 'HPP33446', 'Laptop', 'Marketing', 'Floor 3 - Marketing', 55000),
        ('Apple MacBook Air', 'APL99887', 'Laptop', 'HR', 'Floor 1 - HR', 90000),
        ('Lenovo Yoga', 'LEN44556', 'Laptop', 'Operations', 'Floor 3 - Operations', 60000),
        ('Dell Desktop XPS', 'DEX99887', 'Desktop', 'IT', 'Floor 2 - IT Lab', 50000),
        ('Lenovo ThinkCentre', 'LEN22334', 'Desktop', 'Operations', 'Floor 3 - Operations', 40000),
        ('HP EliteDesk', 'HPL66778', 'Desktop', 'Finance', 'Floor 1 - Finance', 45000),
        ('Apple iMac', 'APL11223', 'Desktop', 'Marketing', 'Floor 3 - Marketing', 100000),
        ('HP LaserJet Pro', 'HPL33445', 'Printer', 'HR', 'Floor 1 - HR', 25000),
        ('Canon ImageRunner', 'CAN44556', 'Printer', 'Finance', 'Floor 1 - Finance', 35000),
        ('Brother DCP-L5500', 'BRO66778', 'Printer', 'Operations', 'Floor 3 - Operations', 28000),
        ('Epson Projector', 'EPS66778', 'Projector', 'IT', 'Floor 2 - Conference Room', 40000),
        ('BenQ Projector', 'BEN22334', 'Projector', 'Marketing', 'Floor 3 - Conference Room', 35000),
        ('Sony Projector', 'SON44556', 'Projector', 'HR', 'Floor 1 - Conference Room', 45000),
        ('Samsung Galaxy Tab', 'SAM99881', 'Tablet', 'Marketing', 'Floor 3 - Marketing', 30000),
        ('Apple iPad Pro', 'APP12345', 'Tablet', 'Finance', 'Floor 1 - Finance', 45000),
        ('Microsoft Surface', 'MSF66778', 'Tablet', 'Sales', 'Floor 2 - Sales', 50000),
        ('iPhone 14 Pro', 'IPH99887', 'Phone', 'IT', 'Floor 2 - IT Lab', 80000),
        ('Samsung Galaxy S23', 'SAM11223', 'Phone', 'Sales', 'Floor 2 - Sales', 75000),
        ('Google Pixel 7', 'GOG33445', 'Phone', 'Marketing', 'Floor 3 - Marketing', 65000),
        ('Fujitsu ScanSnap', 'FUJ44556', 'Scanner', 'Finance', 'Floor 1 - Finance', 20000),
        ('Epson Perfection', 'EPS66779', 'Scanner', 'HR', 'Floor 1 - HR', 18000),
        ('Herman Miller Aeron', 'HER99887', 'Chair', 'IT', 'Floor 2 - IT Lab', 15000),
        ('Steelcase Leap', 'STE11223', 'Chair', 'Finance', 'Floor 1 - Finance', 14000),
        ('Toyota Camry', 'TOY33445', 'Vehicle', 'Operations', 'Parking Lot', 3000000),
        ('Honda Accord', 'HON66778', 'Vehicle', 'Sales', 'Parking Lot', 2800000),
        ('Tata Nexon', 'TAT99881', 'Vehicle', 'HR', 'Parking Lot', 1500000),
        ('Conference Room A', 'CONF_A', 'Meeting Room', 'IT', 'Floor 2', 0),
        ('Conference Room B', 'CONF_B', 'Meeting Room', 'Marketing', 'Floor 3', 0),
        ('Board Room', 'BOARD_01', 'Meeting Room', 'Finance', 'Floor 1', 0),
    ]
    
    assets = []

    for i, (name, serial, cat_name, dept_name, location, cost) in enumerate(assets_data, start=1):

        category = AssetCategory.query.filter_by(name=cat_name).first()
        department = Department.query.filter_by(name=dept_name).first()

        if not category or not department:
            continue

        asset = Asset(
            tag=f"AF-{i:04d}",
            name=name,
            serial_number=serial,
            category_id=category.id,
            department_id=department.id,
            location=location,
            status="Available",
            cost=cost,
            health_score=random.randint(85, 100)
        )

        assets.append(asset)

    db.session.add_all(assets)
    db.session.commit()

    print(f"  ✅ Created {len(assets)} assets")

    # ============================================
    # 5. Create Allocations
    # ============================================
    print("  📋 Creating allocations...")
    
    allocation_data = [
        ('AF-0001', 'EMP001'),
        ('AF-0003', 'EMP003'),
        ('AF-0004', 'EMP004'),
        ('AF-0006', 'EMP002'),
        ('AF-0008', 'EMP004'),
        ('AF-0010', 'EMP006'),
        ('AF-0002', 'EMP011'),
        ('AF-0005', 'EMP001'),
        ('AF-0007', 'EMP006'),
        ('AF-0009', 'EMP003'),
        ('AF-0011', 'EMP008'),
        ('AF-0012', 'EMP005'),
    ]
    
    for tag, emp_id in allocation_data:
        asset = Asset.query.filter_by(tag=tag).first()
        user = User.query.filter_by(employee_id=emp_id).first()
        if asset and user and asset.is_available():
            allocation = AssetAllocation(
                asset_id=asset.id,
                user_id=user.id,
                allocated_date=datetime.now() - timedelta(days=random.randint(10, 90)),
                return_date=datetime.now() + timedelta(days=random.randint(5, 30)),
                status='Active'
            )
            db.session.add(allocation)
            asset.status = 'Allocated'
    
    db.session.commit()
    print(f"  ✅ Created {len(allocation_data)} allocations")

    # ============================================
    # 6. Create Notifications
    # ============================================
    print("  🔔 Creating notifications...")
    
    employees = User.query.filter_by(role='Employee').all()
    
    notification_data = [
        ('Asset Allocated', 'Laptop AF-0001 has been allocated to Rahul', 'allocation', '📋'),
        ('Booking Confirmed', 'Conference Room A booked for 3 PM tomorrow', 'booking', '📅'),
        ('Return Overdue', 'Asset AF-0010 is overdue for return', 'overdue', '⚠️'),
    ]
    
    for title, message, type, icon in notification_data:
        for user in random.sample(employees, min(3, len(employees))):
            notif = Notification(
                user_id=user.id,
                title=title,
                message=message,
                type=type,
                icon=icon,
                read=False
            )
            db.session.add(notif)
    
    db.session.commit()
    print(f"  ✅ Created {len(notification_data) * 3} notifications")

    # ============================================
    # 7. Summary
    # ============================================
    print("\n🎉 Database seeding completed successfully!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"  • Departments: {Department.query.count()}")
    print(f"  • Categories: {AssetCategory.query.count()}")
    print(f"  • Users: {User.query.count()}")
    print(f"  • Assets: {Asset.query.count()}")
    print(f"  • Allocations: {AssetAllocation.query.count()}")
    print(f"  • Notifications: {Notification.query.count()}")
    print("=" * 50)
    
    print("\n🔑 Login Credentials:")
    print("  • Admin: admin@assetflow.com / admin123")
    print("  • Manager: manager@assetflow.com / manager123")
    print("  • Employee: EMP001 / password123")
    print("\n🚀 Ready to use AssetFlow AI!")