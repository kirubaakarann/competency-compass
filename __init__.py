from flask import Flask
from routes.ai_recommendations import ai_recommendations

def create_app():
    app = Flask(__name__)
    
    # Register the AI recommendations blueprint
    app.register_blueprint(ai_recommendations, url_prefix='/ai-recommendations')
    
    return app
