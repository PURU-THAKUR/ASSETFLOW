from database.models import Asset, AssetAllocation, MaintenanceRequest
from database.database import db
from datetime import datetime, timedelta

class RecommendationEngine:
    def get_recommendations(self):
        recommendations = []
        
        # Idle assets
        cutoff = datetime.now() - timedelta(days=30)
        idle = Asset.query.filter(
            Asset.status == 'Available',
            Asset.updated_at < cutoff
        ).limit(3).all()
        
        if idle:
            recommendations.append({
                'type': 'idle_assets',
                'icon': '💤',
                'priority': 'medium',
                'title': f"{len(idle)} assets idle for 30+ days",
                'message': "These assets may be better utilized elsewhere.",
                'assets': [{'tag': a.tag, 'name': a.name} for a in idle],
                'action': "Consider reallocating to high-demand departments."
            })
        
        # Overdue
        overdue = AssetAllocation.query.filter(
            AssetAllocation.return_date < datetime.now(),
            AssetAllocation.status == 'Active'
        ).limit(3).all()
        
        if overdue:
            recommendations.append({
                'type': 'overdue',
                'icon': '⚠️',
                'priority': 'high',
                'title': f"{len(overdue)} assets are overdue",
                'message': "These assets need to be returned immediately.",
                'assets': [{'tag': a.asset.tag, 'name': a.asset.name} for a in overdue],
                'action': "Send reminder notifications to employees."
            })
        
        return recommendations