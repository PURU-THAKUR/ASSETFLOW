from database.models import Asset, AssetAllocation, MaintenanceRequest, User, Department, AssetCategory
from database.database import db
from datetime import datetime
import json

class KnowledgeBase:
    """Knowledge base for AI to learn and improve"""
    
    def __init__(self):
        self.knowledge = {
            'asset_patterns': {},
            'user_patterns': {},
            'department_patterns': {},
            'maintenance_patterns': {},
            'allocation_patterns': {},
            'learned_rules': []
        }
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load knowledge from database"""
        try:
            # Load asset patterns
            assets = Asset.query.all()
            for asset in assets:
                key = f"{asset.category.name if asset.category else 'Unknown'}_{asset.department}"
                if key not in self.knowledge['asset_patterns']:
                    self.knowledge['asset_patterns'][key] = {
                        'count': 0,
                        'avg_health': 0,
                        'maintenance_frequency': 0
                    }
                self.knowledge['asset_patterns'][key]['count'] += 1
                self.knowledge['asset_patterns'][key]['avg_health'] += (asset.health_score or 0)
            
            # Calculate averages
            for key in self.knowledge['asset_patterns']:
                count = self.knowledge['asset_patterns'][key]['count']
                if count > 0:
                    self.knowledge['asset_patterns'][key]['avg_health'] /= count
            
            # Load maintenance patterns
            maintenance = MaintenanceRequest.query.all()
            for req in maintenance:
                if req.asset:
                    key = req.asset.category.name if req.asset.category else 'Unknown'
                    if key not in self.knowledge['maintenance_patterns']:
                        self.knowledge['maintenance_patterns'][key] = {
                            'count': 0,
                            'avg_resolution_time': 0,
                            'common_issues': {}
                        }
                    self.knowledge['maintenance_patterns'][key]['count'] += 1
                    
                    # Track common issues
                    if req.issue:
                        issue_key = req.issue[:50]  # Truncate
                        if issue_key not in self.knowledge['maintenance_patterns'][key]['common_issues']:
                            self.knowledge['maintenance_patterns'][key]['common_issues'][issue_key] = 0
                        self.knowledge['maintenance_patterns'][key]['common_issues'][issue_key] += 1
            
            # Load allocation patterns
            allocations = AssetAllocation.query.all()
            for alloc in allocations:
                if alloc.asset and alloc.user:
                    key = f"{alloc.asset.category.name if alloc.asset.category else 'Unknown'}_{alloc.user.department or 'Unknown'}"
                    if key not in self.knowledge['allocation_patterns']:
                        self.knowledge['allocation_patterns'][key] = {
                            'count': 0,
                            'avg_duration': 0
                        }
                    self.knowledge['allocation_patterns'][key]['count'] += 1
                    
                    if alloc.return_date and alloc.allocated_date:
                        duration = (alloc.return_date - alloc.allocated_date).days
                        if duration > 0:
                            self.knowledge['allocation_patterns'][key]['avg_duration'] += duration
            
            # Calculate average durations
            for key in self.knowledge['allocation_patterns']:
                count = self.knowledge['allocation_patterns'][key]['count']
                if count > 0:
                    self.knowledge['allocation_patterns'][key]['avg_duration'] /= count
            
        except Exception as e:
            print(f"Error loading knowledge: {e}")
    
    def learn_from_allocation(self, allocation):
        """Learn from a new allocation"""
        if not allocation or not allocation.asset or not allocation.user:
            return
        
        key = f"{allocation.asset.category.name if allocation.asset.category else 'Unknown'}_{allocation.user.department or 'Unknown'}"
        
        if key not in self.knowledge['allocation_patterns']:
            self.knowledge['allocation_patterns'][key] = {
                'count': 0,
                'avg_duration': 0,
                'recent_allocations': []
            }
        
        self.knowledge['allocation_patterns'][key]['count'] += 1
        self.knowledge['allocation_patterns'][key]['recent_allocations'].append({
            'allocated_at': allocation.allocated_date.isoformat() if allocation.allocated_date else None,
            'user': allocation.user.fullname,
            'asset': allocation.asset.tag
        })
        
        # Keep only last 10 allocations
        if len(self.knowledge['allocation_patterns'][key]['recent_allocations']) > 10:
            self.knowledge['allocation_patterns'][key]['recent_allocations'] = \
                self.knowledge['allocation_patterns'][key]['recent_allocations'][-10:]
    
    def learn_from_maintenance(self, request):
        """Learn from a maintenance request"""
        if not request or not request.asset:
            return
        
        key = request.asset.category.name if request.asset.category else 'Unknown'
        
        if key not in self.knowledge['maintenance_patterns']:
            self.knowledge['maintenance_patterns'][key] = {
                'count': 0,
                'avg_resolution_time': 0,
                'common_issues': {}
            }
        
        self.knowledge['maintenance_patterns'][key]['count'] += 1
        
        if request.issue:
            issue_key = request.issue[:50]
            if issue_key not in self.knowledge['maintenance_patterns'][key]['common_issues']:
                self.knowledge['maintenance_patterns'][key]['common_issues'][issue_key] = 0
            self.knowledge['maintenance_patterns'][key]['common_issues'][issue_key] += 1
    
    def get_insights(self):
        """Get insights from knowledge base"""
        insights = []
        
        # Most problematic asset categories
        problem_categories = []
        for category, data in self.knowledge['maintenance_patterns'].items():
            if data['count'] > 3:
                problem_categories.append({
                    'category': category,
                    'maintenance_count': data['count'],
                    'common_issue': max(data['common_issues'].items(), key=lambda x: x[1])[0] if data['common_issues'] else 'None'
                })
        
        problem_categories.sort(key=lambda x: x['maintenance_count'], reverse=True)
        if problem_categories:
            insights.append({
                'type': 'maintenance',
                'title': 'Problem Asset Categories',
                'message': f"Most problematic: {problem_categories[0]['category']} with {problem_categories[0]['maintenance_count']} maintenance requests",
                'details': problem_categories[:3]
            })
        
        # Allocation patterns
        high_demand = []
        for key, data in self.knowledge['allocation_patterns'].items():
            if data['count'] > 5:
                high_demand.append({
                    'pattern': key,
                    'count': data['count'],
                    'avg_duration': data['avg_duration']
                })
        
        high_demand.sort(key=lambda x: x['count'], reverse=True)
        if high_demand:
            insights.append({
                'type': 'allocation',
                'title': 'High Demand Patterns',
                'message': f"Most common allocation: {high_demand[0]['pattern']} with {high_demand[0]['count']} allocations",
                'details': high_demand[:3]
            })
        
        return insights
    
    def get_suggestion(self, asset_id, user_id=None):
        """Get personalized suggestion"""
        asset = Asset.query.get(asset_id)
        if not asset:
            return None
        
        suggestions = []
        
        # Check if asset has history
        allocations = AssetAllocation.query.filter_by(asset_id=asset_id).all()
        if len(allocations) == 0:
            suggestions.append({
                'type': 'info',
                'message': 'This asset has never been allocated. Consider allocating to a department.',
                'action': 'Allocate now'
            })
        
        # Check maintenance history
        maintenance_count = MaintenanceRequest.query.filter_by(asset_id=asset_id).count()
        if maintenance_count > 3:
            suggestions.append({
                'type': 'warning',
                'message': f'This asset has had {maintenance_count} maintenance requests. Consider replacement.',
                'action': 'View maintenance history'
            })
        
        # Check health
        if asset.health_score and asset.health_score < 50:
            suggestions.append({
                'type': 'warning',
                'message': f'Asset health is low ({asset.health_score}%). Schedule maintenance.',
                'action': 'Schedule maintenance'
            })
        
        # Check if user has similar assets
        if user_id:
            user = User.query.get(user_id)
            if user:
                user_assets = AssetAllocation.query.filter_by(user_id=user_id, status='Active').all()
                if len(user_assets) > 3:
                    suggestions.append({
                        'type': 'info',
                        'message': f'{user.fullname} already has {len(user_assets)} assets allocated. Consider redistribution.',
                        'action': 'Review allocations'
                    })
        
        return suggestions
    
    def get_faq(self):
        """Get frequently asked questions and answers"""
        faqs = [
            {
                'question': 'How do I allocate an asset?',
                'answer': 'Go to the Allocation page, select an available asset, choose an employee, and click "Allocate Asset".'
            },
            {
                'question': 'How to return an asset?',
                'answer': 'Go to your allocations, find the asset, and click the "Return" button.'
            },
            {
                'question': 'What is asset health score?',
                'answer': 'Health score is calculated based on age, maintenance frequency, and usage patterns. Higher score means better condition.'
            },
            {
                'question': 'How to book a meeting room?',
                'answer': 'Go to the Bookings page, select a meeting room, choose date/time, and submit booking request.'
            },
            {
                'question': 'What are the asset statuses?',
                'answer': 'Available (free), Allocated (assigned), Maintenance (being repaired), Lost (cannot be found).'
            }
        ]
        return faqs
    
    def export_knowledge(self):
        """Export knowledge base as JSON"""
        return json.dumps(self.knowledge, indent=2, default=str)
    
    def import_knowledge(self, json_data):
        """Import knowledge from JSON"""
        try:
            data = json.loads(json_data)
            self.knowledge.update(data)
            return True
        except Exception as e:
            print(f"Error importing knowledge: {e}")
            return False