
from flask_mongoengine import MongoEngine
import os

db = MongoEngine()

def initialize_db(app):
    """Initialize MongoDB connection if MONGO_URI is provided."""
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        print("⚠️  Warning: MONGO_URI not found. Running without MongoDB. Data persistence features will be disabled.")
        return
    
    try:
        app.config["mongo_uri"] = mongo_uri
        app.config['MONGODB_SETTINGS'] = {
            'db': 'interview_tool_db',
            'host': mongo_uri
        }
        db.init_app(app)
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to connect to MongoDB: {e}")
        print("Running without database. Data persistence features will be disabled.")