from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import API blueprints
from api.parking_routes import parking_bp
from api.video_routes import video_bp
from api.parking_analysis_routes import parking_analysis_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow React frontend to communicate from any local source
CORS(app, origins=[
    'http://localhost:3000',  # Default React dev server
    'http://localhost:5000',  # Configured React dev server
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5000', 
    'http://0.0.0.0:5000',
    '*'  # Allow all origins for development
], supports_credentials=True)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register API blueprints
app.register_blueprint(parking_bp, url_prefix='/api')
app.register_blueprint(video_bp)
app.register_blueprint(parking_analysis_bp)

@app.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Sheridan Spot Smart AI Backend API',
        'version': '1.0.0'
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'ai_detection': 'ready',
        'endpoints': [
            '/api/detect-parking',
            '/api/parking-status',
            '/api/upload-image',
            '/api/video/info',
            '/api/video/extract-frame',
            '/api/video/detect-cars',
            '/api/video/test',
            '/api/parking/analyze-video',
            '/api/parking/spaces',
            '/api/parking/spaces/create'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)