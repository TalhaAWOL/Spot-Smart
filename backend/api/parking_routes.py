from flask import Blueprint, request, jsonify, current_app
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from ai_detection.parking_detector import ParkingDetector

parking_bp = Blueprint('parking', __name__)

# Initialize parking detector
detector = ParkingDetector()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@parking_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload an image for parking detection analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'message': 'File uploaded successfully'
            }), 200
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/detect-parking', methods=['POST'])
def detect_parking():
    """Analyze an uploaded image for parking space detection"""
    try:
        data = request.get_json()
        
        if not data or 'image_path' not in data:
            return jsonify({'error': 'No image path provided'}), 400
        
        image_path = data['image_path']
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'Image file not found'}), 404
        
        # Perform parking detection
        results = detector.detect_parking_spaces(full_path)
        
        return jsonify({
            'success': True,
            'results': results,
            'image_path': image_path,
            'total_spots': results['total_spots'],
            'occupied_spots': results['occupied_spots'],
            'available_spots': results['available_spots'],
            'occupancy_rate': results['occupancy_rate']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/parking-status', methods=['GET'])
def get_parking_status():
    """Get current parking status for all monitored lots"""
    try:
        # For now, return sample data - this would connect to a database in production
        parking_lots = [
            {
                'id': 'lot_1',
                'name': 'Main Parking Lot',
                'location': {
                    'lat': 43.6532,
                    'lng': -79.3832
                },
                'total_spots': 50,
                'available_spots': 23,
                'occupied_spots': 27,
                'occupancy_rate': 0.54,
                'last_updated': '2025-09-16T08:15:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'parking_lots': parking_lots,
            'timestamp': '2025-09-16T08:15:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/define-spots', methods=['POST'])
def define_parking_spots():
    """Define parking spot coordinates for a specific lot"""
    try:
        data = request.get_json()
        
        if not data or 'spots' not in data:
            return jsonify({'error': 'No parking spots data provided'}), 400
        
        lot_id = data.get('lot_id', 'default')
        spots = data['spots']
        
        # Save spot definitions (in production, this would go to a database)
        detector.save_spot_definitions(lot_id, spots)
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(spots)} parking spot definitions for lot {lot_id}',
            'lot_id': lot_id,
            'spots_count': len(spots)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500