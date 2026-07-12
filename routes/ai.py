from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from ai.assistant import AIAssistant
from ai.recommendation import RecommendationEngine
from database.models import Asset

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/assistant')
def assistant_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('ai_assistant.html')

@ai_bp.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'Please ask me something! 🤖'})
    
    assistant = AIAssistant()
    response = assistant.get_response(message)
    return jsonify({'response': response})

@ai_bp.route('/api/recommendations')
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    engine = RecommendationEngine()
    recommendations = engine.get_recommendations()
    return jsonify(recommendations)

@ai_bp.route('/api/insights')
def get_insights():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    assistant = AIAssistant()
    insights = assistant.get_daily_insights()
    return jsonify(insights)

@ai_bp.route('/api/search')
def search():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    # Simple search
    results = []
    assets = Asset.query.filter(
        (Asset.name.ilike(f'%{query}%')) |
        (Asset.tag.ilike(f'%{query}%'))
    ).limit(5).all()
    
    for asset in assets:
        results.append({
            'icon': '💻',
            'title': f"{asset.tag} - {asset.name}",
            'description': f"Status: {asset.status} | Location: {asset.location or 'N/A'}",
            'url': f'/assets/view/{asset.id}',
            'type': 'asset'
        })
    
    return jsonify(results)