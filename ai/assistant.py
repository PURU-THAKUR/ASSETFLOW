from database.models import Asset, AssetAllocation, MaintenanceRequest, User, Department
from database.database import db
from datetime import datetime, timedelta
from sqlalchemy import func

class AIAssistant:
    def __init__(self):
        self.context = {}
        self.load_context()
    
    def load_context(self):
        try:
            self.context = {
                'total_assets': Asset.query.count(),
                'available': Asset.query.filter_by(status='Available').count(),
                'allocated': Asset.query.filter_by(status='Allocated').count(),
                'maintenance': Asset.query.filter_by(status='Maintenance').count(),
                'overdue': AssetAllocation.query.filter(
                    AssetAllocation.return_date < datetime.now(),
                    AssetAllocation.status == 'Active'
                ).count()
            }
        except:
            self.context = {}
    
    def get_response(self, message):
        message = message.lower().strip()
        self.load_context()
        
        if 'overdue' in message and ('asset' in message or 'return' in message):
            return self._handle_overdue()
        
        if 'available' in message or 'status' in message:
            return self._handle_status()
        
        if 'maintenance' in message:
            return self._handle_maintenance()
        
        if 'recommend' in message or 'suggest' in message:
            return self._handle_recommendation()
        
        if 'hello' in message or 'hi' in message:
            return "Hello! 👋 I'm your AssetFlow AI Assistant. Ask me about assets, allocations, or maintenance!"
        
        return self._handle_default()
    
    def _handle_overdue(self):
        overdue = AssetAllocation.query.filter(
            AssetAllocation.return_date < datetime.now(),
            AssetAllocation.status == 'Active'
        ).all()
        
        if not overdue:
            return "✅ No overdue assets! All allocations are on track."
        
        response = f"⚠️ {len(overdue)} assets are overdue:\n\n"
        for alloc in overdue[:5]:
            response += f"• {alloc.asset.tag} - {alloc.asset.name} (Return by: {alloc.return_date.strftime('%b %d')})\n"
        return response
    
    def _handle_status(self):
        return f"""📊 Asset Status:
• Total Assets: {self.context.get('total_assets', 0)}
• Available: {self.context.get('available', 0)}
• Allocated: {self.context.get('allocated', 0)}
• Maintenance: {self.context.get('maintenance', 0)}
• Overdue: {self.context.get('overdue', 0)}"""
    
    def _handle_maintenance(self):
        pending = MaintenanceRequest.query.filter_by(status='Pending').count()
        return f"🔧 Maintenance: {pending} pending requests"
    
    def _handle_recommendation(self):
        return "💡 Recommendation: Check idle assets and consider reallocation."
    
    def _handle_default(self):
        return """🤖 I can help you with:
• Asset status ("Show asset status")
• Overdue returns ("Show overdue assets")
• Maintenance ("Maintenance status")
• Recommendations ("Give recommendations")

What would you like to know?"""
    
    def get_daily_insights(self):
        self.load_context()
        insights = []
        
        if self.context.get('overdue', 0) > 0:
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': f"{self.context['overdue']} assets overdue",
                'message': "These assets need to be returned immediately."
            })
        
        pending = MaintenanceRequest.query.filter_by(status='Pending').count()
        if pending > 0:
            insights.append({
                'type': 'info',
                'icon': '🔧',
                'title': f"{pending} maintenance pending",
                'message': "These requests need attention."
            })
        
        if not insights:
            insights.append({
                'type': 'success',
                'icon': '✅',
                'title': "All Systems Healthy",
                'message': "No issues detected. Keep up the good work!"
            })
        
        return insights