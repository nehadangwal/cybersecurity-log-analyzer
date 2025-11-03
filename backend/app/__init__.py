from flask import Flask, jsonify  # Import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Root route - handles base URL
    @app.route("/")
    def index():
        return jsonify({
            "status": "running", 
            "message": "Log Analysis API is online",
            "endpoints": {
                "login": "/api/login",
                "upload": "/api/upload-log"
            }
        }), 200

    with app.app_context():
        from . import models
        # *** RE-ADD THIS: The ONLY place db.create_all() should be ***
        db.create_all()
        # ************************************************************
        
        # Import and register blueprints
        # *** FIX THE IMPORT BACK TO RELATIVE FOR RUNTIME ***
        from .routes import api
        app.register_blueprint(api, url_prefix="/api")

    return app