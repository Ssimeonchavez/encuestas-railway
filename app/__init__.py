from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/')
    
    # Crear tablas automáticamente
    with app.app_context():
        db.create_all()
    
    return app