from database.models import Asset, AssetAllocation, MaintenanceRequest
from database.database import db
from datetime import datetime, timedelta
from collections import defaultdict
import math

class AssetPredictor:
    """Predict asset usage, maintenance needs, and lifespan"""
    
    def __init__(self):
        self.assets = Asset.query.all()
        self.allocations = AssetAllocation.query.all()
        self.maintenance = MaintenanceRequest.query.all()
    
    def predict_usage(self, asset_id):
        """Predict future usage pattern for an asset"""
        asset = Asset.query.get(asset_id)
        if not asset:
            return None
        
        # Get allocation history
        allocations = AssetAllocation.query.filter_by(asset_id=asset_id).all()
        
        if not allocations:
            return {
                'asset': asset.tag,
                'name': asset.name,
                'usage_prediction': 'No usage history available',
                'recommended_action': 'Start using this asset to track patterns'
            }
        
        # Calculate average usage
        total_days = 0
        for alloc in allocations:
            if alloc.return_date and alloc.allocated_date:
                days = (alloc.return_date - alloc.allocated_date).days
                total_days += max(days, 0)
        
        avg_usage_days = total_days / len(allocations) if allocations else 0
        
        # Predict next allocation
        last_allocation = allocations[-1] if allocations else None
        if last_allocation and last_allocation.return_date:
            last_return = last_allocation.return_date
            days_since = (datetime.now() - last_return).days
        else:
            days_since = 0
        
        # Predict next allocation based on average interval
        avg_interval = self._calculate_avg_allocation_interval(asset_id)
        
        if avg_interval > 0:
            predicted_allocation = datetime.now() + timedelta(days=avg_interval)
        else:
            predicted_allocation = None
        
        return {
            'asset': asset.tag,
            'name': asset.name,
            'avg_usage_days': round(avg_usage_days, 1),
            'total_allocations': len(allocations),
            'avg_interval_days': round(avg_interval, 1) if avg_interval > 0 else 'N/A',
            'days_since_last_return': days_since,
            'predicted_next_allocation': predicted_allocation.strftime('%b %d, %Y') if predicted_allocation else 'Unknown',
            'recommended_action': self._get_usage_recommendation(avg_usage_days, days_since)
        }
    
    def _calculate_avg_allocation_interval(self, asset_id):
        """Calculate average interval between allocations"""
        allocations = AssetAllocation.query.filter_by(asset_id=asset_id)\
            .order_by(AssetAllocation.allocated_date).all()
        
        if len(allocations) < 2:
            return 0
        
        intervals = []
        for i in range(1, len(allocations)):
            prev = allocations[i-1]
            curr = allocations[i]
            if prev.allocated_date and curr.allocated_date:
                interval = (curr.allocated_date - prev.allocated_date).days
                if interval > 0:
                    intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else 0
    
    def _get_usage_recommendation(self, avg_usage_days, days_since):
        """Get recommendation based on usage patterns"""
        if avg_usage_days == 0:
            return "Asset hasn't been used. Consider reallocation."
        elif avg_usage_days < 7:
            return "High usage asset. Ensure regular maintenance."
        elif avg_usage_days < 30:
            return "Moderate usage. Good performance."
        elif days_since > 60:
            return "Asset might be idle. Consider reallocation."
        else:
            return "Normal usage pattern. Continue monitoring."
    
    def predict_maintenance(self, asset_id):
        """Predict when asset might need maintenance"""
        asset = Asset.query.get(asset_id)
        if not asset:
            return None
        
        # Get maintenance history
        maintenance_history = MaintenanceRequest.query.filter_by(asset_id=asset_id)\
            .order_by(MaintenanceRequest.created_at).all()
        
        if not maintenance_history:
            return {
                'asset': asset.tag,
                'name': asset.name,
                'maintenance_prediction': 'No maintenance history available',
                'recommended_action': 'Regular maintenance recommended'
            }
        
        # Calculate average time between maintenance
        intervals = []
        for i in range(1, len(maintenance_history)):
            prev = maintenance_history[i-1]
            curr = maintenance_history[i]
            if prev.created_at and curr.created_at:
                interval = (curr.created_at - prev.created_at).days
                if interval > 0:
                    intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Predict next maintenance
        last_maintenance = maintenance_history[-1]
        if last_maintenance.created_at:
            days_since = (datetime.now() - last_maintenance.created_at).days
            predicted_days = int(avg_interval - days_since) if avg_interval > 0 else 0
            
            if predicted_days <= 0:
                status = 'Overdue'
                action = 'Schedule maintenance immediately'
            elif predicted_days <= 7:
                status = 'Due soon'
                action = 'Plan maintenance in the next few days'
            else:
                status = 'Normal'
                action = 'Continue regular maintenance schedule'
        else:
            status = 'Unknown'
            action = 'Update maintenance records'
        
        return {
            'asset': asset.tag,
            'name': asset.name,
            'maintenance_count': len(maintenance_history),
            'avg_interval_days': round(avg_interval, 1) if avg_interval > 0 else 'N/A',
            'days_since_last': days_since if 'days_since' in locals() else 'N/A',
            'predicted_days': predicted_days if 'predicted_days' in locals() else 'N/A',
            'status': status,
            'recommended_action': action
        }
    
    def predict_lifespan(self, asset_id):
        """Predict remaining lifespan of an asset"""
        asset = Asset.query.get(asset_id)
        if not asset:
            return None
        
        # Base lifespan by category
        category_lifespan = {
            'Laptop': 4,
            'Desktop': 5,
            'Printer': 3,
            'Projector': 5,
            'Tablet': 3,
            'Phone': 3,
            'Chair': 8,
            'Vehicle': 10,
            'Monitor': 5,
            'Scanner': 4
        }
        
        category_name = asset.category.name if asset.category else 'Unknown'
        base_lifespan = category_lifespan.get(category_name, 5)  # Default 5 years
        
        # Adjust based on health score
        health = asset.health_score or 80
        health_factor = health / 100
        
        # Adjust based on maintenance frequency
        maintenance_count = MaintenanceRequest.query.filter_by(asset_id=asset_id).count()
        maintenance_penalty = min(maintenance_count * 0.1, 0.5)  # Max 50% reduction
        
        # Adjust based on usage frequency
        allocation_count = AssetAllocation.query.filter_by(asset_id=asset_id).count()
        usage_factor = min(allocation_count * 0.05, 0.3)  # Max 30% reduction
        
        # Calculate remaining lifespan
        if asset.purchase_date:
            age = (datetime.now() - asset.purchase_date).days / 365
            adjusted_lifespan = base_lifespan * health_factor * (1 - maintenance_penalty) * (1 - usage_factor * 0.1)
            remaining = max(adjusted_lifespan - age, 0)
        else:
            # If no purchase date, estimate based on health
            remaining = base_lifespan * health_factor * 0.5
        
        return {
            'asset': asset.tag,
            'name': asset.name,
            'category': category_name,
            'base_lifespan_years': base_lifespan,
            'health_factor': round(health_factor, 2),
            'maintenance_penalty': round(maintenance_penalty, 2),
            'estimated_remaining_years': round(remaining, 1),
            'estimated_remaining_months': round(remaining * 12, 1),
            'status': 'Good' if remaining > 2 else ('Warning' if remaining > 1 else 'Critical'),
            'recommendation': self._get_lifespan_recommendation(remaining)
        }
    
    def _get_lifespan_recommendation(self, remaining_years):
        """Get recommendation based on remaining lifespan"""
        if remaining_years > 3:
            return "Asset is in good condition. Continue regular maintenance."
        elif remaining_years > 1.5:
            return "Asset is aging. Plan for replacement within the next 2 years."
        elif remaining_years > 0.5:
            return "Asset near end of life. Start budget planning for replacement."
        else:
            return "Asset needs immediate replacement. Emergency action required."
    
    def predict_demand(self, category_id=None, department_id=None):
        """Predict demand for assets based on usage patterns"""
        query = Asset.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        assets = query.all()
        
        if not assets:
            return {'prediction': 'No assets found for analysis'}
        
        # Calculate demand metrics
        total_allocations = 0
        total_demand = 0
        high_demand_assets = []
        
        for asset in assets:
            allocations = AssetAllocation.query.filter_by(asset_id=asset.id).count()
            total_allocations += allocations
            
            # Calculate demand as allocations per day since creation
            if asset.created_at:
                days = (datetime.now() - asset.created_at).days
                if days > 0:
                    demand = allocations / days
                    total_demand += demand
                    
                    if demand > 0.05:  # More than 1 allocation per 20 days
                        high_demand_assets.append({
                            'tag': asset.tag,
                            'name': asset.name,
                            'demand_score': round(demand, 3)
                        })
        
        avg_demand = total_demand / len(assets) if assets else 0
        
        return {
            'total_assets': len(assets),
            'total_allocations': total_allocations,
            'avg_demand_score': round(avg_demand, 3),
            'high_demand_assets': high_demand_assets[:5],
            'prediction': self._get_demand_prediction(avg_demand, len(assets)),
            'recommendation': self._get_demand_recommendation(avg_demand, len(assets))
        }
    
    def _get_demand_prediction(self, avg_demand, asset_count):
        """Get demand prediction text"""
        if avg_demand > 0.1:
            return "High demand for these assets. Consider increasing inventory."
        elif avg_demand > 0.03:
            return "Moderate demand. Maintain current inventory levels."
        else:
            return "Low demand. Consider reducing inventory or reallocating."
    
    def _get_demand_recommendation(self, avg_demand, asset_count):
        """Get demand recommendation"""
        if avg_demand > 0.1:
            return f"Purchase additional {asset_count} assets to meet demand."
        elif avg_demand > 0.03:
            return "Maintain current asset levels. Monitor usage patterns."
        else:
            return "Consider reducing asset count or reallocating to other departments."