# Sheridan Spot Smart - AIM-IT Navigation App

## Overview
A React-based navigation application that provides Google Maps integration for route planning and turn-by-turn navigation simulation. Built for AIM-IT's Sheridan Spot Smart project.

## Project Architecture
- **Frontend**: React 17 with Create React App
- **UI Framework**: Chakra UI for components and styling
- **Mapping**: Google Maps JavaScript API with React Google Maps API
- **Icons**: React Icons (FontAwesome)
- **Animation**: Framer Motion

## Key Features
- Interactive Google Maps interface
- Route calculation between origin and destination
- Step-by-step navigation with car simulation
- Real-time route animation with smooth transitions
- Autocomplete for location search
- Responsive design with mobile-friendly interface

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

## Recent Changes (2025-09-16)
- Imported from GitHub repository
- Configured for Replit environment
- Set up proper host binding and proxy support
- Secured Google Maps API key in Replit Secrets
- Configured deployment settings

## User Preferences
- Uses standard React/JavaScript patterns
- Maintains existing code structure and conventions
- Focuses on functionality over extensive refactoring