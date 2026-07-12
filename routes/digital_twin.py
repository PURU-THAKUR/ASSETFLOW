from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database.models import Asset, Department

digital_twin_bp = Blueprint('digital_twin', __name__, url_prefix='/digital-twin')

@digital_twin_bp.route('/')
def digital_twin():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('digital_twin.html')

@digital_twin_bp.route('/api/assets')
def get_twin_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    assets = Asset.query.all()
    data = []
    for idx, asset in enumerate(assets):
        data.append({
            'id': asset.id,
            'tag': asset.tag,
            'name': asset.name,
            'category': asset.category.name if asset.category else 'Unknown',
            'status': asset.status,
            'department': asset.dept.name if asset.dept else 'Unknown',
            'location': asset.location or 'Unknown',
            'health_score': asset.health_score or 100
        })
    
    return jsonify(data)

@digital_twin_bp.route('/api/stats')
def get_twin_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'total': Asset.query.count(),
        'available': Asset.query.filter_by(status='Available').count(),
        'allocated': Asset.query.filter_by(status='Allocated').count(),
        'maintenance': Asset.query.filter_by(status='Maintenance').count(),
        'lost': Asset.query.filter_by(status='Lost').count()
    })

@digital_twin_bp.route('/api/departments')
def get_twin_departments():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    departments = Department.query.all()
    data = [{'id': d.id, 'name': d.name, 'asset_count': len(d.assets)} for d in departments]
    return jsonify(data)