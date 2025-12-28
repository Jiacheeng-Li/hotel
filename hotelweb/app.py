import os
import logging
from flask import Flask
from .config import Config
from .extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Context processor to make brands available in all templates
    @app.context_processor
    def inject_brands():
        from .models import Brand
        brands = Brand.query.all()
        return dict(brands=brands)

    # Setup Logging
    configure_logging(app)

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.create_all()

    return app

def configure_logging(app):
    # Requirement 7.2: Logging
    app.logger.setLevel(logging.INFO)
    
    # Create handler (e.g., to console or file)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.info('HotelWeb startup')

if __name__ == '__main__':
    app = create_app()
    app.run()
