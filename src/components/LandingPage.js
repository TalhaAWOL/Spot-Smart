import React from 'react';
import { 
  Box, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  Input, 
  InputGroup, 
  InputLeftElement,
  IconButton,
  useDisclosure,
  SimpleGrid,
  Stack,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useBreakpointValue
} from '@chakra-ui/react';
import { FaApple, FaGooglePlay, FaSearch, FaBars } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  const parkingSpots = [
    { address: "115 N. Michigan Ave.", price: "$49.04" },
    { address: "200 E Randolph St", price: "$42.50" },
    { address: "300 N State St", price: "$38.75" },
    { address: "500 W Madison St", price: "$45.00" },
  ];

  const NavBar = () => (
    <Flex
      bg="rgba(255, 255, 255, 0.8)"
      p={4}
      boxShadow="md"
      position="fixed"
      width="100%"
      top={0}
      zIndex={1000}
      backdropFilter="blur(5px)"
    >
      <Flex flex={1} justify="space-between" align="center">
        {!isMobile && (
          <Flex gap={6}>
            <Link to="/">Home</Link>
            <Link to="/app">Navigate</Link>
            <Link to="/vehicle">Vehicle</Link>
          </Flex>
        )}
        
        <Flex gap={6} ml="auto">
          <Text>Our Apps</Text>
          <Text>Help</Text>
          <Text>Sign In</Text>
        </Flex>

        {isMobile && (
          <IconButton
            icon={<FaBars />}
            onClick={onOpen}
            ml="auto"
            aria-label="Open menu"
            variant="ghost"
          />
        )}
      </Flex>
    </Flex>
  );

  const MobileMenu = () => (
    <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
      <DrawerOverlay>
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody>
            <Stack spacing={4}>
              <Link to="/" onClick={onClose}>Home</Link>
              <Link to="/app" onClick={onClose}>Navigate</Link>
              <Link to="/vehicle" onClick={onClose}>Vehicle</Link>
            </Stack>
          </DrawerBody>
        </DrawerContent>
      </DrawerOverlay>
    </Drawer>
  );

  return (
    <Box position="relative" minH="100vh" overflow="hidden">
      <Box
        position="absolute"
        top={0}
        left={0}
        width="100%"
        height="100%"
        zIndex={0}
        overflow="hidden"
      >
        <video
          autoPlay
          loop
          muted
          playsInline
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.7
          }}
        >
          <source src="carsNight.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <Box
          position="absolute"
          top={0}
          left={0}
          width="100%"
          height="100%"
          bg="rgba(0, 0, 0, 0.3)"
        />
      </Box>

      <Box position="relative" zIndex={1}>
        <NavBar />
        <MobileMenu />

        <Flex
          direction="column"
          align="center"
          justify="center"
          minH="100vh"
          pt={20}
          px={4}
        >
          <Heading fontSize="4xl" textAlign="center" mb={4} color="white" textShadow="0 2px 4px rgba(0,0,0,0.5)">
            PARKING JUST GOT A LOT SIMPLER
          </Heading>
          
          <Text fontSize="xl" color="white" mb={8} textShadow="0 1px 3px rgba(0,0,0,0.5)">
            Book the Best Spaces for FREE!
          </Text>

          <InputGroup maxW="600px" mb={8}>
            <InputLeftElement pointerEvents="none">
              <FaSearch color="gray.500" />
            </InputLeftElement>
            <Input 
              placeholder="Search Address, Place or Event" 
              size="lg"
              borderRadius="full"
              bg="rgba(255, 255, 255, 0.9)"
              _focus={{
                bg: "white"
              }}
            />
          </InputGroup>

          <Flex gap={4} mb={12}>
            <Button 
              leftIcon={<FaApple />} 
              colorScheme="blackAlpha"
              bg="rgba(0, 0, 0, 0.7)"
              _hover={{ bg: "rgba(0, 0, 0, 0.9)" }}
            >
              App Store
            </Button>
            <Button 
              leftIcon={<FaGooglePlay />} 
              colorScheme="blackAlpha"
              bg="rgba(0, 0, 0, 0.7)"
              _hover={{ bg: "rgba(0, 0, 0, 0.9)" }}
            >
              Google Play
            </Button>
          </Flex>

          {/* <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} mb={16} w="100%" maxW="1200px">
            {parkingSpots.map((spot, index) => (
              <Box 
                key={index} 
                bg="rgba(255, 255, 255, 0.9)"
                p={6} 
                borderRadius="xl" 
                boxShadow="lg"
                _hover={{
                  transform: "translateY(-5px)",
                  transition: "transform 0.3s ease"
                }}
              >
                <Text fontWeight="bold" mb={2}>{spot.address}</Text>
                <Text fontSize="2xl" color="yellow.500" mb={4}>{spot.price} today</Text>
                <Button colorScheme="yellow" w="100%">Book Now</Button>
              </Box>
            ))}
          </SimpleGrid> */}

          <Box textAlign="center" mb={16} color="white" textShadow="0 1px 3px rgba(0,0,0,0.5)">
            <Heading fontSize="2xl" mb={4}>
              DISCOVER AMAZING SPACES
            </Heading>
            <Text mb={6}>
              Find parking anywhere, for now or for later<br />
              Compare prices & pick the place that's best for you
            </Text>
          </Box>
        </Flex>
      </Box>
    </Box>
  );
};

export default LandingPage;