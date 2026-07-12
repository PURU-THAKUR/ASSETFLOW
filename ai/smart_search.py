from database.models import Asset, AssetAllocation, User, Department, AssetCategory
from database.database import db
from difflib import SequenceMatcher
import re

class SmartSearch:
    """Intelligent search across all asset data"""
    
    def __init__(self):
        self.searchable_fields = [
            'assets', 'users', 'departments', 'categories', 'allocations'
        ]
    
    def search(self, query, limit=20):
        """Perform intelligent search across all data"""
        if not query or len(query) < 2:
            return []
        
        query = query.strip()
        results = []
        
        # Search assets
        assets = self._search_assets(query)
        for asset in assets[:limit]:
            results.append({
                'type': 'asset',
                'id': asset.id,
                'title': f"{asset.tag} - {asset.name}",
                'subtitle': f"{asset.status} | {asset.location or 'N/A'}",
                'category': asset.category.name if asset.category else 'N/A',
                'department': asset.dept.name if asset.dept else 'N/A',
                'icon': '💻',
                'url': f'/assets/view/{asset.id}',
                'relevance': self._calculate_relevance(asset, query)
            })
        
        # Search users
        users = self._search_users(query)
        for user in users[:limit]:
            results.append({
                'type': 'user',
                'id': user.id,
                'title': user.fullname,
                'subtitle': f"{user.department or 'N/A'} | {user.role}",
                'employee_id': user.employee_id,
                'icon': '👤',
                'url': f'/profile/{user.id}',
                'relevance': self._calculate_relevance(user, query)
            })
        
        # Search departments
        departments = self._search_departments(query)
        for dept in departments[:limit]:
            results.append({
                'type': 'department',
                'id': dept.id,
                'title': dept.name,
                'subtitle': f"{dept.description or 'No description'}",
                'asset_count': Asset.query.filter_by(department_id=dept.id).count(),
                'icon': '🏢',
                'url': f'/departments/{dept.id}',
                'relevance': self._calculate_relevance(dept, query)
            })
        
        # Search categories
        categories = self._search_categories(query)
        for cat in categories[:limit]:
            results.append({
                'type': 'category',
                'id': cat.id,
                'title': cat.name,
                'subtitle': f"{cat.description or 'No description'}",
                'asset_count': Asset.query.filter_by(category_id=cat.id).count(),
                'icon': '📂',
                'url': f'/categories/{cat.id}',
                'relevance': self._calculate_relevance(cat, query)
            })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:limit]
    
    def _search_assets(self, query):
        """Search assets by various fields"""
        query_lower = query.lower()
        
        # Try exact tag match first
        if query.startswith('AF-'):
            asset = Asset.query.filter_by(tag=query.upper()).first()
            if asset:
                return [asset]
        
        # Search by name, tag, serial, location
        assets = Asset.query.filter(
            (Asset.name.ilike(f'%{query}%')) |
            (Asset.tag.ilike(f'%{query}%')) |
            (Asset.serial_number.ilike(f'%{query}%')) |
            (Asset.location.ilike(f'%{query}%'))
        ).limit(10).all()
        
        # If no results, try fuzzy search
        if not assets:
            all_assets = Asset.query.limit(50).all()
            fuzzy_results = []
            for asset in all_assets:
                score = max(
                    SequenceMatcher(None, asset.name.lower(), query_lower).ratio(),
                    SequenceMatcher(None, asset.tag.lower(), query_lower).ratio()
                )
                if score > 0.6:
                    fuzzy_results.append((score, asset))
            
            fuzzy_results.sort(key=lambda x: x[0], reverse=True)
            assets = [asset for _, asset in fuzzy_results[:5]]
        
        return assets
    
    def _search_users(self, query):
        """Search users by name, email, employee_id"""
        users = User.query.filter(
            (User.fullname.ilike(f'%{query}%')) |
            (User.email.ilike(f'%{query}%')) |
            (User.employee_id.ilike(f'%{query}%')) |
            (User.department.ilike(f'%{query}%'))
        ).limit(10).all()
        
        if not users:
            all_users = User.query.limit(50).all()
            fuzzy_results = []
            for user in all_users:
                score = max(
                    SequenceMatcher(None, user.fullname.lower(), query.lower()).ratio(),
                    SequenceMatcher(None, user.email.lower(), query.lower()).ratio()
                )
                if score > 0.6:
                    fuzzy_results.append((score, user))
            
            fuzzy_results.sort(key=lambda x: x[0], reverse=True)
            users = [user for _, user in fuzzy_results[:5]]
        
        return users
    
    def _search_departments(self, query):
        """Search departments by name"""
        depts = Department.query.filter(
            Department.name.ilike(f'%{query}%')
        ).all()
        
        if not depts:
            all_depts = Department.query.limit(20).all()
            fuzzy_results = []
            for dept in all_depts:
                score = SequenceMatcher(None, dept.name.lower(), query.lower()).ratio()
                if score > 0.6:
                    fuzzy_results.append((score, dept))
            
            fuzzy_results.sort(key=lambda x: x[0], reverse=True)
            depts = [dept for _, dept in fuzzy_results[:3]]
        
        return depts
    
    def _search_categories(self, query):
        """Search categories by name"""
        cats = AssetCategory.query.filter(
            AssetCategory.name.ilike(f'%{query}%')
        ).all()
        
        if not cats:
            all_cats = AssetCategory.query.limit(20).all()
            fuzzy_results = []
            for cat in all_cats:
                score = SequenceMatcher(None, cat.name.lower(), query.lower()).ratio()
                if score > 0.6:
                    fuzzy_results.append((score, cat))
            
            fuzzy_results.sort(key=lambda x: x[0], reverse=True)
            cats = [cat for _, cat in fuzzy_results[:3]]
        
        return cats
    
    def _calculate_relevance(self, item, query):
        """Calculate relevance score for a search result"""
        query_lower = query.lower()
        
        if hasattr(item, 'name'):
            if item.name and item.name.lower() == query_lower:
                return 1.0
            elif item.name and query_lower in item.name.lower():
                return 0.8
        
        if hasattr(item, 'tag') and item.tag:
            if item.tag.lower() == query_lower:
                return 1.0
            elif query_lower in item.tag.lower():
                return 0.9
        
        if hasattr(item, 'fullname') and item.fullname:
            if item.fullname.lower() == query_lower:
                return 1.0
            elif query_lower in item.fullname.lower():
                return 0.8
        
        if hasattr(item, 'email') and item.email:
            if query_lower in item.email.lower():
                return 0.7
        
        return 0.5
    
    def search_command_palette(self, query):
        """Optimized search for command palette (UI)"""
        results = self.search(query, limit=10)
        
        # Format for command palette UI
        formatted = []
        for result in results:
            formatted.append({
                'icon': result['icon'],
                'title': result['title'],
                'description': result['subtitle'],
                'url': result['url'],
                'type': result['type']
            })
        
        return formatted