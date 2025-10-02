import React, { useState } from 'react';
import { Box, Button, Text, VStack, Alert, AlertIcon, Spinner, Image, Heading } from '@chakra-ui/react';

function ParkingDetectionTest() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [annotatedImage, setAnnotatedImage] = useState(null);

  const testParkingDetection = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setAnnotatedImage(null);
    
    try {
      // Use relative URL - the proxy in package.json will route it to the backend
      const apiUrl = '/api/parking/analyze-video';
      
      console.log('Frontend URL:', window.location.href);
      console.log('Fetching from:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_filename: 'parking_video.mp4',
          frame_number: 0
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('API Response:', {
        success: data.success,
        hasImage: !!data.annotated_image_base64,
        imageLength: data.annotated_image_base64 ? data.annotated_image_base64.length : 0
      });
      
      if (data.success) {
        // Set results first
        setResults({
          total_spots: data.parking_analysis.total_spaces,
          occupied_spots: data.parking_analysis.occupied_spaces,
          available_spots: data.parking_analysis.available_spaces,
          occupancy_rate: data.parking_analysis.occupancy_rate,
          car_count: data.car_count,
        });
        
        // Then set the image
        if (data.annotated_image_base64) {
          const imageDataUrl = `data:image/jpeg;base64,${data.annotated_image_base64}`;
          console.log('Setting annotated image, length:', imageDataUrl.length);
          setAnnotatedImage(imageDataUrl);
        } else {
          console.error('No annotated_image_base64 in response');
          setError('Backend did not return annotated image');
        }
      } else {
        setError(data.error || 'Detection failed');
      }
    } catch (err) {
      console.error('Error:', err);
      setError(`Failed to connect: ${err.message}`);
    }
    
    setLoading(false);
  };

  return (
    <Box p={6} maxW="1200px" mx="auto" bg="white" borderRadius="lg" shadow="lg" maxH="90vh" overflowY="auto">
      <VStack spacing={6}>
        <Heading size="lg" color="blue.600">
          AI Parking Detection - Visual Analysis
        </Heading>
        
        <Button 
          colorScheme="blue" 
          size="lg"
          onClick={testParkingDetection}
          isLoading={loading}
          loadingText="Analyzing parking lot..."
        >
          Test AI Detection on Sample Parking Lot
        </Button>
        
        {loading && (
          <VStack>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text mt={2} fontSize="lg">AI is analyzing the parking lot...</Text>
          </VStack>
        )}
        
        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            <Text>{error}</Text>
          </Alert>
        )}
        
        {annotatedImage && (
          <Box w="100%" borderRadius="lg" overflow="hidden" border="4px solid" borderColor="green.500" boxShadow="2xl">
            <Box bg="green.50" p={3} borderBottom="2px solid" borderColor="green.300">
              <Heading size="md" color="green.700" textAlign="center">
                ANNOTATED PARKING LOT IMAGE
              </Heading>
            </Box>
            <Image 
              src={annotatedImage} 
              alt="Annotated parking lot with detected cars and parking spaces"
              w="100%"
              h="auto"
              objectFit="contain"
              onLoad={() => console.log('Image loaded successfully!')}
              onError={(e) => {
                console.error('Image load error:', e);
                setError('Failed to display image');
              }}
            />
            <Box p={4} bg="blue.50" borderTop="2px solid" borderColor="blue.300">
              <VStack spacing={2}>
                <Text fontSize="lg" fontWeight="bold" color="blue.800" textAlign="center">
                  VISUAL AI DETECTION RESULTS
                </Text>
                <Text fontSize="md" color="gray.700" textAlign="center">
                  Yellow rectangles = Detected cars with confidence scores
                </Text>
                <Text fontSize="md" color="gray.700" textAlign="center">
                  Blue rectangles = Parking spaces with occupancy status
                </Text>
              </VStack>
            </Box>
          </Box>
        )}
        
        {results && (
          <Box w="100%" p={6} bg="gray.50" borderRadius="lg" border="2px solid" borderColor="gray.300">
            <Heading size="md" mb={4} color="green.600">
              Detection Statistics:
            </Heading>
            
            <VStack align="start" spacing={3}>
              <Text fontSize="lg"><strong>Cars Detected:</strong> {results.car_count}</Text>
              <Text fontSize="lg"><strong>Total Parking Spots:</strong> {results.total_spots}</Text>
              <Text fontSize="lg"><strong>Occupied Spots:</strong> {results.occupied_spots}</Text>
              <Text fontSize="lg"><strong>Available Spots:</strong> {results.available_spots}</Text>
              <Text fontSize="lg"><strong>Occupancy Rate:</strong> {(results.occupancy_rate * 100).toFixed(1)}%</Text>
              <Text fontSize="sm" color="gray.600" mt={2}>
                Detection Method: Advanced OpenCV with MOG2 Background Subtraction
              </Text>
            </VStack>
          </Box>
        )}
        
        {!annotatedImage && results && (
          <Alert status="warning" borderRadius="md">
            <AlertIcon />
            <Text>Statistics loaded but image not available. Check browser console for details.</Text>
          </Alert>
        )}
      </VStack>
    </Box>
  );
}

export default ParkingDetectionTest;
