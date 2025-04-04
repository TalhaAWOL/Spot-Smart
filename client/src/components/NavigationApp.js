/* eslint-disable no-undef */
import {
    Box,
    Button,
    ButtonGroup,
    Flex,
    HStack,
    IconButton,
    Input,
    SkeletonText,
    Text,
    VStack,
    Heading
  } from '@chakra-ui/react'
  import { FaLocationArrow, FaTimes } from 'react-icons/fa'
  
  import {
    useJsApiLoader,
    GoogleMap,
    Marker,
    Autocomplete,
    DirectionsRenderer,
  } from '@react-google-maps/api'
  import { useRef, useState, useEffect } from 'react'
  
  const center = { lat: 48.8584, lng: 2.2945 }
  
  function App() {
    const { isLoaded } = useJsApiLoader({
      googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
      libraries: ['places', 'geometry'],
    })
  
    const [map, setMap] = useState(/** @type google.maps.Map */ (null))
    const [directionsResponse, setDirectionsResponse] = useState(null)
    const [distance, setDistance] = useState('')
    const [duration, setDuration] = useState('')
    const [steps, setSteps] = useState([])
    const [currentStepIndex, setCurrentStepIndex] = useState(0)
    const [showSteps, setShowSteps] = useState(false)
  
    const [isNavigating, setIsNavigating] = useState(false)
    const navigationIntervalRef = useRef(null)
    const [progress, setProgress] = useState(0);
    const [carMarker, setCarMarker] = useState(null)
    const carMarkerRef = useRef(null);
    const currentPositionRef = useRef(null);
  
    const [center, setCenter] = useState(null) 
    const [currentLocation, setCurrentLocation] = useState(null)
    const [searchHistory, setSearchHistory] = useState({
      origins: ["Current Location"],
      destinations: []
    });
    
  
  
    /** @type React.MutableRefObject<HTMLInputElement> */
    const originRef = useRef()
    /** @type React.MutableRefObject<HTMLInputElement> */
    const destiantionRef = useRef()

    useEffect(() => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            };
            setCenter(pos);
            setCurrentLocation(pos);
            if (originRef.current) {
              originRef.current.value = "Current Location";
            }
          },
          () => {
            // Default to Eiffel Tower if geolocation fails
            const defaultPos = { lat: 48.8584, lng: 2.2945 };
            setCenter(defaultPos);
            setCurrentLocation(defaultPos);
          }
        );
      } else {
        // Browser doesn't support Geolocation
        const defaultPos = { lat: 48.8584, lng: 2.2945 };
        setCenter(defaultPos);
        setCurrentLocation(defaultPos);
      }
    }, []);

    useEffect(() => {
      const loadSearchHistory = async () => {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('/api/search/history', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          const data = await response.json();
          setSearchHistory(data);
        } catch (err) {
          console.error('Failed to load search history:', err);
        }
      };
    
      loadSearchHistory();
    }, []);
  
    if (!isLoaded || !center) {
      return <SkeletonText />
    }

    function centerMap() {
      if (map && currentLocation) {
        map.panTo(currentLocation);
        map.setZoom(15);
      }
    }
  
    async function calculateRoute() {
      if (originRef.current.value === '' || destiantionRef.current.value === '') {
        return
      }

      try {
        // First save the search to history
        const token = localStorage.getItem('token');
        await fetch('/api/search/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            origin: originRef.current.value,
            destination: destiantionRef.current.value
          })
        });

      // Replace "Current Location" with actual coordinates
      let origin = originRef.current.value;
      if (origin === "Current Location" && currentLocation) {
        origin = `${currentLocation.lat},${currentLocation.lng}`;
      }

      // eslint-disable-next-line no-undef
      const directionsService = new google.maps.DirectionsService()
      const results = await directionsService.route({
        origin: origin,
        destination: destiantionRef.current.value,
        // eslint-disable-next-line no-undef
        travelMode: google.maps.TravelMode.DRIVING,
      })
      setDirectionsResponse(results)
      setDistance(results.routes[0].legs[0].distance.text)
      setDuration(results.routes[0].legs[0].duration.text)
  
      // Extract step-by-step directions
      const routeSteps = results.routes[0].legs[0].steps.map((step, index) => ({
        id: index,
        instructions: step.instructions,
        distance: step.distance.text,
      }))
      setSteps(routeSteps)
      setCurrentStepIndex(0)
      setShowSteps(false)
    }catch (err) {
      console.error('Failed to save search history:', err);
    }
  }
  
    function clearRoute() {

      if (navigationIntervalRef.current) {
        cancelAnimationFrame(navigationIntervalRef.current);
        navigationIntervalRef.current = null;
      }
      
      if (carMarkerRef.current) {
        carMarkerRef.current.setMap(null);
        carMarkerRef.current = null;
      }
      
      setDirectionsResponse(null);
      setDistance('');
      setDuration('');
      setSteps([]);
      setCurrentStepIndex(0);
      setShowSteps(false);
      setProgress(0);
      setIsNavigating(false);
      
      originRef.current.value = '';
      destiantionRef.current.value = '';
      
      if (map) {
        map.setCenter(center);
        map.setZoom(15);
        map.setTilt(0);
        map.setHeading(0);
      }
    }
  
    function goToNextStep(){
      setCurrentStepIndex((prev) => (prev < steps.length-1 ? prev+1 : prev))
    }
  
    function goToPreviousStep(){
      setCurrentStepIndex((prev) => (prev > 0 ? prev-1: prev))
    }
  
    function startNavigation() {
      if (!window.google || !directionsResponse || !map) {
        console.error("Google Maps API is not loaded or not available.");
        return;
      }
    
      const route = directionsResponse.routes[0];
      const path = route.overview_path;
    
      if (navigationIntervalRef.current) {
        clearInterval(navigationIntervalRef.current);
      }
    
      setIsNavigating(true);
      setCurrentStepIndex(0);
      setProgress(0);
    
      if (!carMarkerRef.current) {
        carMarkerRef.current = new google.maps.Marker({
          position: path[0],
          map: map,
          icon: {
            path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            scale: 5,
            fillColor: "#4285F4",
            fillOpacity: 1,
            strokeWeight: 2,
            rotation: 0,
          },
        });
        setCarMarker(carMarkerRef.current);
      } else {
        carMarkerRef.current.setPosition(path[0]);
        carMarkerRef.current.setMap(map);
      }
    
      const totalPoints = path.length;
      const animationDuration = 60000;
      const intervalTime = 16;
      const pointsPerSecond = totalPoints / (animationDuration / 1000);
      const pointsPerInterval = pointsPerSecond * (intervalTime / 1000);
    
      let currentIndex = 0;
      let fractionalIndex = 0;
      let lastUpdateTime = performance.now();
    
      const animate = () => {
        const now = performance.now();
        const deltaTime = now - lastUpdateTime;
        lastUpdateTime = now;
    
        fractionalIndex += (deltaTime / 1000) * pointsPerSecond;
        currentIndex = Math.min(fractionalIndex, totalPoints - 1);
    
        const idx1 = Math.floor(currentIndex);
        const idx2 = Math.min(idx1 + 1, totalPoints - 1);
        const ratio = currentIndex - idx1;
        
        const currentPoint = {
          lat: path[idx1].lat() + (path[idx2].lat() - path[idx1].lat()) * ratio,
          lng: path[idx1].lng() + (path[idx2].lng() - path[idx1].lng()) * ratio
        };
    
        const nextIdx = Math.min(Math.floor(currentIndex) + 1, totalPoints - 1);
        const nextPoint = path[nextIdx];
    
        if (carMarkerRef.current) {
          const latLng = new google.maps.LatLng(currentPoint.lat, currentPoint.lng);
          carMarkerRef.current.setPosition(latLng);
    
          if (nextPoint) {
            const heading = google.maps.geometry.spherical.computeHeading(
              latLng,
              nextPoint
            );
            carMarkerRef.current.setIcon({
              path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
              scale: 5,
              fillColor: "#4285F4",
              fillOpacity: 1,
              strokeWeight: 2,
              rotation: heading,
            });
          }
    
          const zoomLevel = map.getZoom();
          const targetZoom = zoomLevel > 18 ? zoomLevel : 18;
          if (zoomLevel !== targetZoom) {
            map.setZoom(targetZoom);
          }
          
          map.panTo(latLng);
          
          if (map.getTilt() !== 45) {
            map.setTilt(45);
          }
        }
    
        setProgress(currentIndex / (totalPoints - 1));
        updateCurrentStepBasedOnPosition(currentPoint);
    
        if (currentIndex < totalPoints - 1) {
          navigationIntervalRef.current = requestAnimationFrame(animate);
        } else {
          setIsNavigating(false);
        }
      };
    
      map.setCenter(path[0]);
      map.setZoom(18);
      map.setTilt(45);
    
      navigationIntervalRef.current = requestAnimationFrame(animate);
    }
  
    function updateCurrentStepBasedOnPosition(currentPosition) {
      if (!directionsResponse) return;
    
      const leg = directionsResponse.routes[0].legs[0];
      for (let i = 0; i < leg.steps.length; i++) {
        const step = leg.steps[i];
        const stepPath = step.path;
     
        for (let j = 0; j < stepPath.length; j++) {
          if (google.maps.geometry.spherical.computeDistanceBetween(
            currentPosition,
            stepPath[j]
          ) < 10) { 
            setCurrentStepIndex(i);
            return;
          }
        }
      }
    }
    
  
    function pauseResumeNavigation() {
      if (isNavigating) {

        if (navigationIntervalRef.current) {
          clearInterval(navigationIntervalRef.current);
          navigationIntervalRef.current = null;
        }
      } else {

        if (steps.length > 0) {
          startNavigation();
        } else {
          alert("No route to resume. Please calculate a route first.");
        }
      }
      setIsNavigating(!isNavigating);
    }
    
  
    return (
      <Flex
        position='relative'
        flexDirection='column'
        alignItems='center'
        h='100vh'
        w='100vw'
      >
        <Flex
          position='absolute'
          top={4}
          left={4}
          right={4}
          justifyContent='space-between'
          zIndex='1'
          pointerEvents='none' 
        >
          <VStack 
            alignItems='flex-start'
            bg='whiteAlpha.800'
            p={3}
            borderRadius='md'
            spacing={0}
          >
            <Heading as="h1" size="lg" color={"yellow.500"} lineHeight="1">Sheridan</Heading>
            <Heading as="h1" size="lg" color={"yellow.500"} lineHeight="1">Spot</Heading>
            <Heading as="h1" size="lg" color={"yellow.500"} lineHeight="1">Smart</Heading>
          </VStack>
            <Heading as="h1" size="lg" color={"yellow.500"} lineHeight="1">AIM-IT</Heading>
        </Flex>
  
        <Box position='absolute' left={0} top={0} h='100%' w='100%'>
          <GoogleMap
            center={center}
            zoom={15}
            mapContainerStyle={{ width: '100%', height: '100%' }}
            options={{
              zoomControl: false,
              streetViewControl: false,
              mapTypeControl: false,
              fullscreenControl: false,
            }}
            onLoad={map => setMap(map)}
          >
            {currentLocation && (
              <Marker 
                position={currentLocation}
                icon={{
                  path: google.maps.SymbolPath.CIRCLE,
                  scale: 7,
                  fillColor: '#4285F4',
                  fillOpacity: 1,
                  strokeWeight: 2,
                  strokeColor: 'white',
                }}
              />
            )}

            {directionsResponse && (
              <>
                <DirectionsRenderer directions={directionsResponse} />
                <Marker
                  position={{
                    lat: directionsResponse.routes[0].legs[0].end_location.lat(),
                    lng: directionsResponse.routes[0].legs[0].end_location.lng()
                  }}
                  icon={{
                    url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
                    scaledSize: new google.maps.Size(32, 32)
                  }}
                />
              </>
            )}
          </GoogleMap>
        </Box>
  
        <IconButton
          aria-label="Center on current location"
          icon={<FaLocationArrow />}
          position="absolute"
          bottom={75}
          right={2}
          zIndex="1"
          onClick={centerMap}
          colorScheme="yellow"
          isRound
        />    

        <Box
          p={4}
          borderRadius='lg'
          m={4}
          bgColor='white'
          shadow='base'
          minW='container.md'
          zIndex='1'
        >
          <HStack spacing={2} justifyContent='space-between'>
          <Box flexGrow={1}>
            <Autocomplete>
              <Input 
                type='text' 
                placeholder='Origin' 
                ref={originRef}
                list='origin-history'
              />
            </Autocomplete>
            <datalist id='origin-history'>
              {searchHistory.origins.map((item, index) => (
                <option key={`origin-${index}`} value={item} />
              ))}
            </datalist>
          </Box>

          <Box flexGrow={1}>
            <Autocomplete>
              <Input 
                type='text' 
                placeholder='Destination' 
                ref={destiantionRef}
                list='destination-history'
              />
            </Autocomplete>
            <datalist id='destination-history'>
              {searchHistory.destinations.map((item, index) => (
                <option key={`destination-${index}`} value={item} />
              ))}
            </datalist>
          </Box>
  
            <ButtonGroup>
              <Button colorScheme='yellow' type='submit' onClick={calculateRoute}>
                Find Route
              </Button>
              <IconButton
                aria-label='center back'
                icon={<FaTimes />}
                onClick={clearRoute}
              />
            </ButtonGroup>
          </HStack>
          <HStack spacing={4} mt={4} justifyContent='space-between'>
            <Text>Distance: {distance} </Text>
            <Text>Time Required: {duration} </Text>
            <IconButton
              aria-label='Start Navigation'
              icon={<FaLocationArrow />}
              isRound
              onClick={() => {
                if (steps.length === 0) {
                  alert("No route calculated yet. Please enter locations and find the route first.")
                  return
                }
                setShowSteps(true)
                startNavigation()
              }}
            />
  
          </HStack>
          {showSteps && steps.length > 0 && (
            <Box mt={4} p={4} bg="whiteAlpha.900" borderRadius="lg" shadow="base">
              <Heading size="md" mb={2}>Step-by-Step Directions</Heading>
  
              <VStack spacing={2} align="center">
                <Text textAlign="center" dangerouslySetInnerHTML={{ __html: `🚗 ${steps[currentStepIndex].instructions} (${steps[currentStepIndex].distance})` }} />
  
                <HStack>
                  <Button
                    onClick={goToPreviousStep}
                    isDisabled={currentStepIndex === 0}
                    colorScheme="yellow"
                  >
                    ◀️ Previous
                  </Button>
  
                  <Button onClick={pauseResumeNavigation} colorScheme="blue">
                    {isNavigating ? "Pause" : "Resume"}
                  </Button>
  
                  <Button
                    onClick={goToNextStep}
                    isDisabled={currentStepIndex === steps.length - 1}
                    colorScheme="yellow"
                  >
                    Next ▶️
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
        </Box>
        
      </Flex>
    )
  }
  
  export default App