from flask import Blueprint, render_template, request, session, jsonify, send_file
from database.models import Asset, AssetAllocation, MaintenanceRequest, ResourceBooking, Department, User
from database.database import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import pandas as pd
import io
import json

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def reports():
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('reports.html')

@reports_bp.route('/api/most-used')
def api_most_used():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    result = db.session.query(
        Asset,
        func.count(AssetAllocation.id).label('count')
    ).join(AssetAllocation, AssetAllocation.asset_id == Asset.id)\
    .filter(AssetAllocation.status == 'Active')\
    .group_by(Asset.id)\
    .order_by(desc('count'))\
    .limit(10).all()
    
    data = []
    for asset, count in result:
        data.append({
            'rank': len(data) + 1,
            'asset': f"{asset.tag} - {asset.name}",
            'usage_count': count,
            'department': asset.dept.name if asset.dept else 'N/A'
        })
    
    return jsonify(data)

@reports_bp.route('/api/idle-assets')
def api_idle_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    cutoff = datetime.now() - timedelta(days=30)
    idle = Asset.query.filter(
        Asset.status == 'Available',
        Asset.updated_at < cutoff
    ).limit(10).all()
    
    data = [{
        'tag': a.tag,
        'name': a.name,
        'department': a.dept.name if a.dept else 'N/A',
        'location': a.location,
        'idle_days': (datetime.now() - (a.updated_at or a.created_at)).days
    } for a in idle]
    
    return jsonify(data)

@reports_bp.route('/api/maintenance-frequency')
def api_maintenance_frequency():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    result = db.session.query(
        Asset.tag,
        Asset.name,
        func.count(MaintenanceRequest.id).label('count')
    ).join(MaintenanceRequest, MaintenanceRequest.asset_id == Asset.id)\
    .group_by(Asset.id)\
    .order_by(desc('count'))\
    .limit(10).all()
    
    data = [{
        'tag': tag,
        'name': name,
        'maintenance_count': count
    } for tag, name, count in result]
    
    return jsonify(data)

@reports_bp.route('/api/department-assets')
def api_department_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    result = db.session.query(
        Department.name,
        func.count(Asset.id).label('count')
    ).join(Asset, Asset.department_id == Department.id, isouter=True)\
    .group_by(Department.id)\
    .all()
    
    data = [{
        'department': dept,
        'count': count
    } for dept, count in result if dept]
    
    return jsonify(data)

@reports_bp.route('/api/booking-heatmap')
def api_booking_heatmap():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get bookings by hour for last 30 days
    bookings = ResourceBooking.query.filter(
        ResourceBooking.start_time >= datetime.now() - timedelta(days=30)
    ).all()
    
    heatmap = {}
    for booking in bookings:
        hour = booking.start_time.hour
        if hour not in heatmap:
            heatmap[hour] = 0
        heatmap[hour] += 1
    
    data = [{
        'hour': h,
        'bookings': count
    } for h, count in sorted(heatmap.items())]
    
    return jsonify(data)

@reports_bp.route('/api/health-report')
def api_health_report():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    excellent = Asset.query.filter(Asset.health_score >= 80).count()
    good = Asset.query.filter(Asset.health_score >= 60, Asset.health_score < 80).count()
    fair = Asset.query.filter(Asset.health_score >= 40, Asset.health_score < 60).count()
    poor = Asset.query.filter(Asset.health_score >= 20, Asset.health_score < 40).count()
    critical = Asset.query.filter(Asset.health_score < 20).count()
    
    avg_health = db.session.query(func.avg(Asset.health_score)).scalar() or 0
    
    return jsonify({
        'average_health': round(avg_health, 1),
        'distribution': {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor,
            'critical': critical
        }
    })

@reports_bp.route('/export/pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect('/login')
    
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import io
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph('AssetFlow AI - Asset Report', title_style))
    story.append(Spacer(1, 20))
    
    # Asset summary
    total = Asset.query.count()
    available = Asset.query.filter_by(status='Available').count()
    allocated = Asset.query.filter_by(status='Allocated').count()
    maintenance = Asset.query.filter_by(status='Maintenance').count()
    
    summary_data = [
        ['Metric', 'Count'],
        ['Total Assets', str(total)],
        ['Available', str(available)],
        ['Allocated', str(allocated)],
        ['In Maintenance', str(maintenance)]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Asset list
    assets = Asset.query.limit(20).all()
    asset_data = [['Tag', 'Name', 'Category', 'Status', 'Location']]
    
    for asset in assets:
        asset_data.append([
            asset.tag,
            asset.name,
            asset.category.name if asset.category else 'N/A',
            asset.status,
            asset.location or 'N/A'
        ])
    
    asset_table = Table(asset_data)
    asset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(asset_table)
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'asset_report_{datetime.now().strftime("%Y%m%d")}.pdf', mimetype='application/pdf')

@reports_bp.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect('/login')
    
    assets = Asset.query.all()
    data = []
    for asset in assets:
        data.append({
            'Tag': asset.tag,
            'Name': asset.name,
            'Serial': asset.serial_number or '',
            'Category': asset.category.name if asset.category else '',
            'Department': asset.dept.name if asset.dept else '',
            'Location': asset.location or '',
            'Status': asset.status,
            'Cost': asset.cost or 0,
            'Health Score': asset.health_score or 100
        })
    
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        as_attachment=True,
        download_name=f'asset_report_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )