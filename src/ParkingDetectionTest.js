import React, { useState } from 'react';
import { Box, Button, Text, VStack, Alert, AlertIcon, Spinner } from '@chakra-ui/react';

function ParkingDetectionTest() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testParkingDetection = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Test the AI detection with the sample image
      const response = await fetch('http://localhost:8000/api/detect-parking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_path: 'sample_parking_lot.png'
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data);
      } else {
        setError(data.error || 'Detection failed');
      }
    } catch (err) {
      setError('Could not connect to AI backend: ' + err.message);
    }
    
    setLoading(false);
  };

  return (
    <Box p={6} maxW="600px" mx="auto" bg="white" borderRadius="lg" shadow="lg">
      <VStack spacing={4}>
        <Text fontSize="xl" fontWeight="bold" color="blue.600">
          🚗 AI Parking Detection Test
        </Text>
        
        <Button 
          colorScheme="blue" 
          onClick={testParkingDetection}
          isLoading={loading}
          loadingText="Analyzing..."
        >
          Test AI Detection on Sample Parking Lot
        </Button>
        
        {loading && (
          <Box>
            <Spinner size="lg" color="blue.500" />
            <Text mt={2}>AI is analyzing the parking lot image...</Text>
          </Box>
        )}
        
        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}
        
        {results && (
          <Box w="100%" p={4} bg="gray.50" borderRadius="md">
            <Text fontSize="lg" fontWeight="bold" mb={3} color="green.600">
              ✅ AI Detection Results:
            </Text>
            
            <VStack align="start" spacing={2}>
              <Text><strong>Total Parking Spots:</strong> {results.total_spots}</Text>
              <Text><strong>Occupied Spots:</strong> {results.occupied_spots}</Text>
              <Text><strong>Available Spots:</strong> {results.available_spots}</Text>
              <Text><strong>Occupancy Rate:</strong> {(results.occupancy_rate * 100).toFixed(1)}%</Text>
              <Text><strong>Detection Confidence:</strong> {(results.results.detection_confidence * 100).toFixed(1)}%</Text>
              <Text><strong>Analysis Method:</strong> {results.results.analysis_method}</Text>
            </VStack>
            
            <Text fontSize="sm" color="gray.600" mt={3}>
              The AI analyzed {results.total_spots} individual parking spaces using computer vision 
              to detect occupancy based on edge detection, color analysis, and contour recognition.
            </Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
}

export default ParkingDetectionTest;