from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database.models import Asset, AssetAllocation, MaintenanceRequest
from database.database import db
from datetime import datetime
from sqlalchemy import func

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/')
def health_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('health_dashboard.html')

@health_bp.route('/api/score/<int:asset_id>')
def get_health_score(asset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    asset = Asset.query.get_or_404(asset_id)
    score = asset.health_score or 100
    
    return jsonify({
        'asset_id': asset.id,
        'tag': asset.tag,
        'name': asset.name,
        'score': score,
        'status': 'Good' if score >= 70 else 'Fair' if score >= 40 else 'Poor',
        'color': '#00E676' if score >= 70 else '#FFB300' if score >= 40 else '#FF1744'
    })

@health_bp.route('/api/overview')
def health_overview():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    assets = Asset.query.all()
    total = len(assets)
    
    if total == 0:
        return jsonify({'total': 0, 'average_score': 0, 'distribution': {}, 'status': 'No Data'})
    
    excellent = sum(1 for a in assets if (a.health_score or 100) >= 80)
    good = sum(1 for a in assets if 60 <= (a.health_score or 100) < 80)
    fair = sum(1 for a in assets if 40 <= (a.health_score or 100) < 60)
    poor = sum(1 for a in assets if (a.health_score or 100) < 40)
    
    avg_score = db.session.query(func.avg(Asset.health_score)).scalar() or 0
    
    return jsonify({
        'total': total,
        'average_score': round(avg_score, 1),
        'distribution': {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor
        },
        'status': 'Good' if avg_score >= 60 else 'Fair'
    })