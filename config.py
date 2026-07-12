import os
from datetime import timedelta

class Config:
    # Basic Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'assetflow-ai-super-secret-key-2024'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///assetflow.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload Folders
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    QR_FOLDER = os.path.join(BASE_DIR, 'generated_qr')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx'}
    
    # Create folders if they don't exist
    for folder in [UPLOAD_FOLDER, QR_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # AI Settings
    AI_ENABLED = True
    AI_MODEL = 'simple'  # 'simple' or 'gpt'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Notification Settings
    NOTIFICATION_TYPES = {
        'allocation': '📋',
        'booking': '📅',
        'maintenance': '🔧',
        'return': '↩️',
        'audit': '📊',
        'transfer': '🔄',
        'overdue': '⚠️',
        'maintenance_complete': '✅',
        'booking_cancelled': '🚫',
        'asset_created': '✨',
        'asset_updated': '📝',
        'asset_deleted': '🗑️'
    }
    
    # Asset Tag Prefix
    ASSET_TAG_PREFIX = 'AF'
    ASSET_TAG_PADDING = 4
    
    # Default Health Score
    DEFAULT_HEALTH_SCORE = 100
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # QR Code Settings
    QR_CODE_SIZE = 300
    QR_CODE_BORDER = 4
    
    # Report Settings
    REPORT_DATE_FORMAT = '%Y-%m-%d %H:%M'
    EXPORT_DATE_FORMAT = '%Y%m%d_%H%M%S'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}