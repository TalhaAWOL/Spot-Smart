import React, { useState, useEffect } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { Box, Text, VStack, HStack, Image, Button } from '@chakra-ui/react';

function ParkingLotMarkers({ map, onStartNavigation }) {
  const [parkingLots, setParkingLots] = useState([]);
  const [selectedLot, setSelectedLot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchParkingLots();
  }, []);

  const fetchParkingLots = async () => {
    try {
      const response = await fetch('/api/parking/lots');
      const data = await response.json();
      
      if (data.success) {
        setParkingLots(data.parking_lots);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching parking lots:', error);
      setLoading(false);
    }
  };

  // Refresh parking lot data
  const refreshParkingLots = () => {
    fetchParkingLots();
  };

  // Expose refresh function globally so other components can call it
  useEffect(() => {
    window.refreshParkingLots = refreshParkingLots;
    return () => {
      delete window.refreshParkingLots;
    };
  }, []);

  const parkingIcon = {
    path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
    fillColor: '#1E88E5',
    fillOpacity: 1,
    strokeWeight: 2,
    strokeColor: '#ffffff',
    scale: 1.5,
  };

  if (loading || !parkingLots.length) {
    return null;
  }

  return (
    <>
      {parkingLots.map((lot) => (
        <React.Fragment key={lot.lot_id}>
          <Marker
            position={lot.coordinates}
            onClick={() => setSelectedLot(lot)}
            icon={parkingIcon}
            title={lot.name}
          />
          
          {selectedLot && selectedLot.lot_id === lot.lot_id && (
            <InfoWindow
              position={lot.coordinates}
              onCloseClick={() => setSelectedLot(null)}
            >
              <Box p={2} maxW="280px">
                <VStack align="stretch" spacing={2}>
                  <Text fontWeight="bold" fontSize="lg" color="blue.600">
                    {lot.name}
                  </Text>
                  
                  <Box 
                    borderRadius="md" 
                    overflow="hidden" 
                    border="2px solid" 
                    borderColor="gray.200"
                  >
                    <Image 
                      src="/lotimage.png" 
                      alt="Parking lot"
                      w="100%"
                      h="120px"
                      objectFit="cover"
                    />
                  </Box>
                  
                  <Box 
                    bg="blue.50" 
                    p={3} 
                    borderRadius="md"
                    border="1px solid"
                    borderColor="blue.200"
                  >
                    <Text fontWeight="bold" mb={2} color="blue.700">
                      Detection Statistics
                    </Text>
                    <VStack align="stretch" spacing={1}>
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">Cars Detected:</Text>
                        <Text fontSize="sm" fontWeight="semibold" color="orange.600">
                          {lot.stats.cars_detected}
                        </Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">Total Parking Spots:</Text>
                        <Text fontSize="sm" fontWeight="semibold">
                          {lot.stats.total_spaces}
                        </Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">Available Spots:</Text>
                        <Text fontSize="sm" fontWeight="semibold" color="green.600">
                          {lot.stats.available_spaces}
                        </Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">Occupancy Rate:</Text>
                        <Text fontSize="sm" fontWeight="semibold" color="red.600">
                          {(lot.stats.occupancy_rate * 100).toFixed(0)}%
                        </Text>
                      </HStack>
                    </VStack>
                  </Box>
                  
                  {lot.stats.last_updated && (
                    <Text fontSize="xs" color="gray.500" textAlign="center">
                      Last updated: {new Date(lot.stats.last_updated).toLocaleTimeString()}
                    </Text>
                  )}
                  
                  <Button
                    colorScheme="yellow"
                    size="md"
                    width="100%"
                    onClick={() => {
                      if (onStartNavigation) {
                        onStartNavigation('7899 McLaughlin Rd, Brampton, ON L6Y 5H9');
                        setSelectedLot(null);
                      }
                    }}
                  >
                    Start Navigation
                  </Button>
                </VStack>
              </Box>
            </InfoWindow>
          )}
        </React.Fragment>
      ))}
    </>
  );
}

export default ParkingLotMarkers;
