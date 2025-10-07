# Sheridan Spot Smart - AIM-IT Navigation App

## Overview
A React-based navigation application that provides Google Maps integration for route planning and turn-by-turn navigation simulation. Built for AIM-IT's Sheridan Spot Smart project.

## Project Architecture
- **Frontend**: React 17 with Create React App
- **Backend**: Flask API with Python 3.10
- **UI Framework**: Chakra UI for components and styling
- **Mapping**: Google Maps JavaScript API with React Google Maps API
- **AI Detection**: YOLOv8 with COCO pretrained weights via Ultralytics, PyTorch 2.8.0 (CPU)
- **Database**: MongoDB with in-memory fallback for development
- **Icons**: React Icons (FontAwesome)
- **Animation**: Framer Motion

## Key Features
- Interactive Google Maps interface
- Route calculation between origin and destination
- Step-by-step navigation with car simulation
- Real-time route animation with smooth transitions
- Autocomplete for location search
- Responsive design with mobile-friendly interface
- AI-powered parking space detection system with YOLOv8
- Visual parking lot analysis with annotated images
- Interactive parking lot markers on map with real-time statistics
- Click parking lot markers to view: Cars Detected, Total Spots, Available Spots, Occupancy Rate
- Real-time parking data updates after AI detection

## Environment Setup
- **Host**: 0.0.0.0 (configured for Replit proxy)
- **Port**: 5000
- **Build Tool**: webpack via react-scripts
- **Package Manager**: npm

## Required Secrets
- `REACT_APP_GOOGLE_MAPS_API_KEY`: Google Maps API key with JavaScript API and Places API enabled

## Development
The app runs in development mode with hot reloading enabled. The workflow is configured to:
- Bind to 0.0.0.0:5000 for Replit compatibility
- Disable host checking for proxy support
- Auto-reload on file changes

## Deployment
Configured for autoscale deployment with:
- Build: `npm run build`
- Serve: Static file serving of build folder on port 5000

## Recent Changes

### 2025-10-07: Custom Parking Lot Marker with Navigation
- **Exact Location**: Parking lot marker positioned at 7899 McLaughlin Rd, Brampton, ON L6Y 5H9 (43.7315, -79.7624)
- **Map Center**: Application now opens centered at Sheridan College location instead of Paris
- **Custom Popup**: Clicking marker displays parking lot image with real-time statistics
- **Start Navigation**: Yellow button in popup auto-fills origin (10 Caboose Street) and destination, then calculates route
- **Default Origin**: Origin field pre-populated with "10 Caboose Street Brampton, ON L7A 5B1"
- **Parking Lot Image**: Custom lotimage.png showing AI-detected cars and parking spaces
- **Auto-refresh**: Parking lot statistics update automatically after running AI detection
- **In-Memory Storage**: Implemented fallback storage for development when MongoDB unavailable

### 2025-10-02: YOLOv8 Deep Learning Implementation
- **Upgraded to YOLOv8**: Migrated from OpenCV MOG2 to YOLOv8 deep learning model for superior accuracy
- **COCO Pretrained Weights**: Uses COCO dataset weights for robust car detection (car, truck, bus, motorcycle classes)
- **PyTorch Integration**: Installed PyTorch 2.8.0 CPU and Ultralytics for YOLOv8 support
- **Color-Coded Parking Spaces**: 
  - Blue rectangles for free parking spaces
  - Red rectangles for occupied spaces
  - Yellow rectangles for partially occupied spaces
- **71 Predefined Parking Spaces**: Configured parking lot grid with optimized overlap detection (IoU threshold)
- **Proxy Configuration**: Fixed Replit connectivity with package.json proxy routing /api/* to localhost:3001
- **Improved Detection Pipeline**: Enhanced parking occupancy analysis with confidence-based classification
- **Base64 Image Encoding**: Annotated images returned to frontend for real-time display
- **Database Integration**: Automated parking lot creation and availability logging to MongoDB/in-memory storage

### 2025-09-16: Initial Setup
- Imported from GitHub repository
- Configured for Replit environment
- Set up proper host binding and proxy support
- Secured Google Maps API key in Replit Secrets
- Configured deployment settings

## User Preferences
- Uses standard React/JavaScript patterns
- Maintains existing code structure and conventions
- Focuses on functionality over extensive refactoring