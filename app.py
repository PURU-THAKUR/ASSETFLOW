from flask import Flask, render_template, session, jsonify, redirect, url_for
from database.database import db
from flask_migrate import Migrate
from datetime import datetime
import os

# ============================================
# SINGLE GLOBAL db INSTANCE - IMPORTANT!
# ============================================
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = 'assetflow-ai-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assetflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    
    # Initialize db with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # ============================================
    # IMPORTANT: Import models AFTER db is initialized
    # ============================================
    from database.models import User, Asset, AssetAllocation, Notification
    
    # ============================================
    # Register blueprints
    # ============================================
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.assets import assets_bp
    from routes.allocation import allocation_bp
    from routes.booking import booking_bp
    from routes.maintenance import maintenance_bp
    from routes.reports import reports_bp
    from routes.notification import notifications_bp
    from routes.qr import qr_bp
    from routes.ai import ai_bp
    from routes.health import health_bp
    from routes.digital_twin import digital_twin_bp
    from routes.settings import settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(allocation_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(digital_twin_bp)
    app.register_blueprint(settings_bp)
    
    # Context processor
    @app.context_processor
    def inject_globals():
        count = 0
        if 'user_id' in session:
            try:
                from database.models import Notification
                count = Notification.query.filter_by(
                    user_id=session['user_id'],
                    read=False
                ).count()
            except:
                count = 0
        return {
            'app_name': 'AssetFlow AI',
            'current_year': datetime.now().year,
            'notifications_count': count
        }
    
    # CLI Commands
    @app.cli.command('init-db')
    def init_db():
        with app.app_context():
            db.create_all()
            print('✅ Database initialized!')
    
    @app.cli.command('seed-db')
    def seed_db():
        from database.seed_data import seed_data
        with app.app_context():
            seed_data()
            print('✅ Database seeded!')
    
    return app

# Create app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)