"""
Advanced Parking Analysis API Routes
Combines video processing, car detection, and parking space mapping
"""

from flask import Blueprint, request, jsonify
import os
import cv2
import base64
from ai_detection.video_processor import VideoProcessor
from ai_detection.parking_mapper import ParkingMapper
from database.parking_database import parking_db
import json

parking_analysis_bp = Blueprint('parking_analysis', __name__)

@parking_analysis_bp.route('/api/parking/analyze-video', methods=['POST'])
def analyze_parking_video():
    """Complete parking analysis: detect cars and determine space occupancy"""
    try:
        data = request.get_json()
        video_filename = data.get('video_filename', 'parking_video.mp4')
        frame_number = data.get('frame_number', 100)
        
        # Security: Sanitize filename to prevent path traversal
        video_filename = os.path.basename(video_filename)
        if not video_filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            return jsonify({'error': 'Invalid video file type'}), 400
        
        video_path = os.path.join('uploads', video_filename)
        config_path = 'uploads/parking_spaces_config.json'
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_filename}'}), 404
        
        # Initialize components
        processor = VideoProcessor()
        mapper = ParkingMapper()
        
        # Load video
        load_result = processor.load_video(video_path)
        if not load_result.get('success'):
            processor.close()
            return jsonify(load_result), 400
        
        # Load or create parking space configuration
        if not mapper.load_parking_spaces(config_path):
            print("Creating new parking space configuration...")
            mapper.define_parking_spaces_manual(load_result['width'], load_result['height'])
            mapper.save_parking_spaces(config_path)
        
        # Extract multiple frames for background modeling
        sample_frames = processor.extract_sample_frames(5)
        if not sample_frames:
            processor.close()
            return jsonify({'error': 'Could not extract frames for analysis'}), 400
        
        # Build background model for MOG2
        bg_subtractor = None
        for frame in sample_frames:
            _, bg_subtractor = processor.detect_cars_mog2(frame, bg_subtractor)
        
        # Analyze specific frame
        ret, target_frame = processor.extract_frame(frame_number)
        if not ret or target_frame is None:
            target_frame = sample_frames[-1]
            frame_number = 'last_sample'
        
        # Detect cars using ADVANCED detection for ALL cars including stationary ones
        detected_cars = processor.detect_cars_advanced(target_frame)
        
        # Analyze parking occupancy
        occupancy_analysis = mapper.analyze_parking_occupancy(target_frame, detected_cars)
        
        # Create annotated visualization
        annotated_frame = mapper.draw_parking_spaces(target_frame, occupancy_analysis)
        
        # Draw detected car bounding boxes
        for car in detected_cars:
            x, y, w, h = car['bbox']
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (255, 255, 0), 3)
            cv2.putText(annotated_frame, f"Car: {car['confidence']:.2f}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Save annotated result
        result_filename = f'parking_analysis_frame_{frame_number}.jpg'
        result_path = os.path.join('uploads', result_filename)
        cv2.imwrite(result_path, annotated_frame)
        
        # Convert annotated image to base64 for frontend display
        success, buffer = cv2.imencode('.jpg', annotated_frame)
        if not success:
            processor.close()
            return jsonify({'error': 'Failed to encode annotated image'}), 500
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # ============ DATABASE OPERATIONS ============
        try:
            # Create or get parking lot
            lot_name = f"Sheridan College Parking Lot"
            lot_location = "Sheridan College, Brampton, ON"
            
            # Check if lot exists, if not create it
            existing_lots = parking_db.get_all_parking_lots()
            lot_id = None
            
            for lot in existing_lots:
                if lot['name'] == lot_name:
                    lot_id = lot['lot_id']
                    break
            
            if not lot_id:
                # Create new parking lot
                lot_data = parking_db.create_parking_lot(
                    name=lot_name,
                    location=lot_location,
                    total_spaces=occupancy_analysis['total_spaces']
                )
                lot_id = lot_data['lot_id']
                print(f"Created new parking lot: {lot_id}")
                
                # Create parking spots for the lot
                spots_data = []
                for i, space in enumerate(mapper.parking_spaces):
                    spots_data.append({
                        'spot_number': i + 1,
                        'coordinates': space
                    })
                
                if spots_data:
                    parking_db.create_parking_spots(lot_id, spots_data)
                    print(f"Created {len(spots_data)} parking spots")
            
            # Log the availability analysis
            analysis_log_data = {
                'total_spaces': occupancy_analysis['total_spaces'],
                'occupied_spaces': occupancy_analysis['occupied_spaces'],
                'available_spaces': occupancy_analysis['available_spaces'],
                'detection_data': {
                    'method': 'advanced_opencv_with_morphological',
                    'confidence': 0.95,
                    'car_count': len(detected_cars),
                    'detected_cars': detected_cars,
                    'analysis_duration': 0,
                    'frame_analyzed': frame_number
                }
            }
            
            log_result = parking_db.log_availability_analysis(lot_id, analysis_log_data)
            print(f"Logged availability analysis: {log_result.get('log_id', 'unknown')}")
            
        except Exception as db_error:
            print(f"Database operation failed: {db_error}")
            # Continue execution even if database fails
        
        processor.close()
        
        return jsonify({
            'success': True,
            'frame_analyzed': frame_number,
            'video_info': load_result,
            'detected_cars': detected_cars,
            'car_count': len(detected_cars),
            'parking_analysis': occupancy_analysis,
            'annotated_image': result_filename,
            'annotated_image_base64': annotated_image_base64,
            'detection_method': 'mog2_with_parking_mapping'
        })
        
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