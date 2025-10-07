"""
Advanced Parking Analysis API Routes
Combines video processing, car detection, and parking space mapping
"""

from flask import Blueprint, request, jsonify
import os
import cv2
import base64
from ai_detection.yolo_video_processor import YOLOVideoProcessor
from database.parking_database import parking_db
import json

parking_analysis_bp = Blueprint('parking_analysis', __name__)

@parking_analysis_bp.route('/api/parking/analyze-video', methods=['POST'])
def analyze_parking_video():
    """Complete parking analysis using YOLO detector with COCO pretrained weights"""
    try:
        data = request.get_json()
        video_filename = data.get('video_filename', 'parking_video.mp4')
        frame_number = data.get('frame_number', 100)
        
        video_filename = os.path.basename(video_filename)
        if not video_filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            return jsonify({'error': 'Invalid video file type'}), 400
        
        video_path = os.path.join('uploads', video_filename)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_filename}'}), 404
        
        processor = YOLOVideoProcessor(model_name='yolov8s.pt', confidence_threshold=0.35)
        
        results = processor.analyze_video_frame(video_path, frame_number)
        
        try:
            lot_name = "Sheridan College Parking Lot"
            lot_location = "Sheridan College, Brampton, ON"
            
            existing_lots = parking_db.get_all_parking_lots()
            lot_id = None
            
            for lot in existing_lots:
                if lot['name'] == lot_name:
                    lot_id = lot['lot_id']
                    break
            
            if not lot_id:
                lot_data = parking_db.create_parking_lot(
                    name=lot_name,
                    location=lot_location,
                    total_spaces=results['parking_analysis']['total_spaces'],
                    coordinates={'lat': 43.7315, 'lng': -79.7624}
                )
                lot_id = lot_data['lot_id']
                print(f"Created new parking lot: {lot_id}")
            
            analysis_log_data = {
                'total_spaces': results['parking_analysis']['total_spaces'],
                'occupied_spaces': results['parking_analysis']['occupied_spaces'],
                'available_spaces': results['parking_analysis']['available_spaces'],
                'detection_data': {
                    'method': 'YOLOv8 with COCO pretrained weights',
                    'confidence': 0.35,
                    'car_count': results['car_count'],
                    'analysis_duration': 0,
                    'frame_analyzed': frame_number
                }
            }
            
            log_result = parking_db.log_availability_analysis(lot_id, analysis_log_data)
            print(f"Logged availability analysis: {log_result.get('log_id', 'unknown')}")
            
        except Exception as db_error:
            print(f"Database operation failed: {db_error}")
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@parking_analysis_bp.route('/api/parking/spaces', methods=['GET'])
def get_parking_spaces():
    """Get parking space configuration"""
    try:
        mapper = ParkingMapper()
        config_path = 'uploads/parking_spaces_config.json'
        
        if mapper.load_parking_spaces(config_path):
            return jsonify({
                'success': True,
                'total_spaces': len(mapper.parking_spaces),
                'video_dimensions': {
                    'width': mapper.video_width,
                    'height': mapper.video_height
                },
                'parking_spaces': mapper.parking_spaces
            })
        else:
            return jsonify({'error': 'No parking configuration found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error loading parking spaces: {str(e)}'}), 500

@parking_analysis_bp.route('/api/parking/spaces/create', methods=['POST'])
def create_parking_spaces():
    """Create or update parking space configuration"""
    try:
        data = request.get_json()
        width = data.get('width', 1280)
        height = data.get('height', 720)
        
        mapper = ParkingMapper()
        spaces = mapper.define_parking_spaces_manual(width, height)
        
        config_path = 'uploads/parking_spaces_config.json'
        if mapper.save_parking_spaces(config_path):
            return jsonify({
                'success': True,
                'total_spaces': len(spaces),
                'parking_spaces': spaces,
                'config_saved': config_path
            })
        else:
            return jsonify({'error': 'Failed to save parking configuration'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error creating parking spaces: {str(e)}'}), 500

@parking_analysis_bp.route('/api/parking/test-analysis', methods=['GET'])
def test_parking_analysis():
    """Test complete parking analysis system"""
    try:
        return analyze_parking_video.__wrapped__()  # Call the main analysis function
        
    except Exception as e:
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

@parking_analysis_bp.route('/api/parking/lots', methods=['GET'])
def get_parking_lots_with_stats():
    """Get all parking lots with their latest detection statistics"""
    try:
        lots = parking_db.get_all_parking_lots()
        
        lots_with_stats = []
        for lot in lots:
            recent_logs = parking_db.get_recent_availability(lot['lot_id'], hours=24)
            
            latest_stats = None
            if recent_logs and len(recent_logs) > 0:
                latest_log = recent_logs[0]
                latest_stats = {
                    'total_spaces': latest_log.get('total_spaces', lot.get('total_spaces', 0)),
                    'occupied_spaces': latest_log.get('occupied_spaces', 0),
                    'available_spaces': latest_log.get('available_spaces', 0),
                    'occupancy_rate': latest_log.get('occupancy_rate', 0),
                    'cars_detected': latest_log.get('detection_data', {}).get('car_count', 0),
                    'last_updated': latest_log.get('timestamp', '').isoformat() if latest_log.get('timestamp') else None
                }
            else:
                latest_stats = {
                    'total_spaces': lot.get('total_spaces', 0),
                    'occupied_spaces': 0,
                    'available_spaces': lot.get('total_spaces', 0),
                    'occupancy_rate': 0,
                    'cars_detected': 0,
                    'last_updated': None
                }
            
            lot_data = {
                'lot_id': lot['lot_id'],
                'name': lot['name'],
                'location': lot['location'],
                'coordinates': lot.get('coordinates', {'lat': 43.7315, 'lng': -79.7624}),
                'stats': latest_stats
            }
            lots_with_stats.append(lot_data)
        
        return jsonify({
            'success': True,
            'parking_lots': lots_with_stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch parking lots: {str(e)}'}), 500