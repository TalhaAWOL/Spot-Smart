"""
Advanced Parking Analysis API Routes
Combines video processing, car detection, and parking space mapping
"""

from flask import Blueprint, request, jsonify
import os
import cv2
from ai_detection.video_processor import VideoProcessor
from ai_detection.parking_mapper import ParkingMapper
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
        
        processor.close()
        
        return jsonify({
            'success': True,
            'frame_analyzed': frame_number,
            'video_info': load_result,
            'detected_cars': detected_cars,
            'car_count': len(detected_cars),
            'parking_analysis': occupancy_analysis,
            'annotated_image': result_filename,
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