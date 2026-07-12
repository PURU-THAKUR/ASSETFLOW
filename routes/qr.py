from flask import Blueprint, render_template, request, session, jsonify, send_file, redirect, url_for
from database.models import Asset
from database.database import db
import qrcode
import io
import base64
import os
from datetime import datetime

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')

@qr_bp.route('/generate/<int:asset_id>', methods=['POST'])
def generate_qr(asset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    asset = Asset.query.get_or_404(asset_id)
    
    import json
    qr_data = {
        'type': 'asset',
        'id': asset.id,
        'tag': asset.tag,
        'name': asset.name
    }
    qr_text = json.dumps(qr_data)
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return jsonify({
        'success': True,
        'qr_code': f'data:image/png;base64,{img_base64}'
    })

@qr_bp.route('/view/<int:asset_id>')
def view_qr(asset_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    asset = Asset.query.get_or_404(asset_id)
    return render_template('qr_view.html', asset=asset)