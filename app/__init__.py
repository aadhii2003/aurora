from flask import Flask
from .config import Config

# Global variable
db = Config.db



def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.db = db

   
    # Register Blueprints
    from .admin.routes import admin_bp
    from .user.routes import user_bp
    # from .user.routes import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/')

    return app




