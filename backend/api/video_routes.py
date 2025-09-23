"""
Video Processing API Routes
Handles video upload, processing, and real-time parking detection
"""

from flask import Blueprint, request, jsonify
import os
import cv2
from werkzeug.utils import secure_filename
from ai_detection.video_processor import VideoProcessor
from ai_detection.parking_detector import ParkingDetector
import json

video_bp = Blueprint('video', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@video_bp.route('/api/video/info', methods=['POST'])
def get_video_info():
    """Get basic information about uploaded video"""
    try:
        data = request.get_json()
        video_filename = data.get('video_filename', 'parking_video.mp4')
        
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_filename}'}), 404
        
        processor = VideoProcessor()
        result = processor.load_video(video_path)
        processor.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Error processing video info: {str(e)}'}), 500

@video_bp.route('/api/video/extract-frame', methods=['POST'])
def extract_frame():
    """Extract a specific frame from video"""
    try:
        data = request.get_json()
        video_filename = data.get('video_filename', 'parking_video.mp4')
        frame_number = data.get('frame_number', 0)
        
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_filename}'}), 404
        
        processor = VideoProcessor()
        load_result = processor.load_video(video_path)
        
        if not load_result.get('success'):
            processor.close()
            return jsonify(load_result), 400
        
        # Extract the requested frame
        ret, frame = processor.extract_frame(frame_number)
        
        if not ret or frame is None:
            processor.close()
            return jsonify({'error': f'Could not extract frame {frame_number}'}), 400
        
        # Save frame as image
        frame_filename = f'frame_{frame_number}.jpg'
        frame_path = os.path.join(UPLOAD_FOLDER, frame_filename)
        cv2.imwrite(frame_path, frame)
        
        processor.close()
        
        return jsonify({
            'success': True,
            'frame_number': frame_number,
            'frame_filename': frame_filename,
            'frame_path': frame_path
        })
        
    except Exception as e:
        return jsonify({'error': f'Error extracting frame: {str(e)}'}), 500

@video_bp.route('/api/video/detect-cars', methods=['POST'])
def detect_cars_in_frame():
    """Detect cars in a specific video frame"""
    try:
        data = request.get_json()
        video_filename = data.get('video_filename', 'parking_video.mp4')
        frame_number = data.get('frame_number', 0)
        
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_filename}'}), 404
        
        processor = VideoProcessor()
        load_result = processor.load_video(video_path)
        
        if not load_result.get('success'):
            processor.close()
            return jsonify(load_result), 400
        
        # Extract the requested frame
        ret, frame = processor.extract_frame(frame_number)
        
        if not ret or frame is None:
            processor.close()
            return jsonify({'error': f'Could not extract frame {frame_number}'}), 400
        
        # Detect cars in the frame
        cars = processor.detect_cars_basic(frame)
        
        # Create annotated frame with bounding boxes
        annotated_frame = frame.copy()
        for car in cars:
            x, y, w, h = car['bbox']
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Car {car['confidence']:.2f}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Save annotated frame
        annotated_filename = f'cars_detected_frame_{frame_number}.jpg'
        annotated_path = os.path.join(UPLOAD_FOLDER, annotated_filename)
        cv2.imwrite(annotated_path, annotated_frame)
        
        processor.close()
        
        return jsonify({
            'success': True,
            'frame_number': frame_number,
            'detected_cars': cars,
            'car_count': len(cars),
            'annotated_image': annotated_filename,
            'video_info': load_result
        })
        
    except Exception as e:
        return jsonify({'error': f'Error detecting cars: {str(e)}'}), 500

@video_bp.route('/api/video/test', methods=['GET'])
def test_video_processing():
    """Test endpoint to verify video processing works"""
    try:
        processor = VideoProcessor()
        
        # Test with default parking video
        result = processor.load_video("uploads/parking_video.mp4")
        
        if result.get("success"):
            # Extract first frame and detect cars
            ret, frame = processor.extract_frame(0)
            if ret:
                cars = processor.detect_cars_basic(frame)
                result['test_car_detection'] = {
                    'cars_detected': len(cars),
                    'frame_extracted': True
                }
            else:
                result['test_car_detection'] = {
                    'frame_extracted': False
                }
        
        processor.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

@video_bp.route('/api/video/upload', methods=['POST'])
def upload_video():
    """Upload a new video file for processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Get video info
            processor = VideoProcessor()
            video_info = processor.load_video(filepath)
            processor.close()
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'video_info': video_info
            })
        else:
            return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv, flv'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error uploading video: {str(e)}'}), 500