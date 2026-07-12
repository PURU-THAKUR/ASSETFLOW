"""
AssetFlow AI - Intelligent Asset Management
This package contains all AI-related functionality
"""

from .assistant import AIAssistant
from .recommendation import RecommendationEngine
from .asset_prediction import AssetPredictor
from .smart_search import SmartSearch
from .rule_engine import RuleEngine
from .knowledge import KnowledgeBase

__all__ = [
    'AIAssistant',
    'RecommendationEngine',
    'AssetPredictor',
    'SmartSearch',
    'RuleEngine',
    'KnowledgeBase'
]