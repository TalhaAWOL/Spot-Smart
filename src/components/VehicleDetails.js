import { Flex, Heading, Button, VStack, FormControl, Input, ButtonGroup, Box } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import '@fontsource/roboto';

const MotionBox = motion(Box);

const VehicleDetails = () => {
  const navigate = useNavigate();

  const shapes = [
    { id: 1, size: '100px', initialY: 25, offset: 30 },
    { id: 2, size: '150px', initialY: 35, offset: 40 },
    { id: 3, size: '70px', initialY: 75, offset: 25 },
    { id: 4, size: '120px', initialY: 65, offset: 35 },
  ];

  return (
    <Flex
      position="relative"
      height="100vh"
      alignItems="center"
      justifyContent="center"
      bg="white"
      overflow="hidden"
    >
      {shapes.map((shape) => (
        <MotionBox
          key={shape.id}
          position="absolute"
          w={shape.size}
          h={shape.size}
          bg="yellow.500"
          opacity={0.1}
          borderRadius="full"
          initial={{ 
            y: `${shape.initialY}%`,
            x: `${Math.random() * 80 + 10}%` 
          }}
          animate={{
            y: `${shape.initialY + shape.offset}%`
          }}
          transition={{
            duration: 8,
            delay: shape.id * 0.3,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut'
          }}
        />
      ))}

      <VStack 
        spacing={6} 
        w={["90%", "md"]}
        zIndex="1"
        bg="white"
        p={8}
        borderRadius="xl"
        boxShadow="xl"
      >
        <VStack spacing={2}>
          <Heading 
            fontSize="3xl" 
            color="yellow.500"
            fontWeight="300"
            fontFamily="Roboto"
            letterSpacing="0.05em"
          >
            PLEASE ENTER
          </Heading>
          <Heading 
            fontSize="3xl" 
            color="yellow.500"
            fontWeight="300"
            fontFamily="Roboto"
            letterSpacing="0.05em"
          >
            SOME DETAILS
          </Heading>
          <Heading 
            fontSize="3xl" 
            color="yellow.500"
            fontWeight="300"
            fontFamily="Roboto"
            letterSpacing="0.05em"
          >
            ABOUT YOUR
          </Heading>
          <Heading 
            fontSize="3xl" 
            color="yellow.500"
            fontWeight="300"
            fontFamily="Roboto"
            letterSpacing="0.05em"
          >
            VEHICLE
          </Heading>
        </VStack>

        <FormControl>
          <VStack spacing={4}>
            <Input 
              placeholder="Vehicle Type" 
              size="lg" 
              borderRadius="full"
              borderColor="gray.200"
              _focus={{
                borderColor: "yellow.500",
                boxShadow: "0 0 0 1px #D69E2E"
              }}
            />
            <Input 
              placeholder="License Plate" 
              size="lg" 
              borderRadius="full"
              borderColor="gray.200"
              _focus={{
                borderColor: "yellow.500",
                boxShadow: "0 0 0 1px #D69E2E"
              }}
            />
            <Input 
              placeholder="Vehicle Color" 
              size="lg" 
              borderRadius="full"
              borderColor="gray.200"
              _focus={{
                borderColor: "yellow.500",
                boxShadow: "0 0 0 1px #D69E2E"
              }}
            />
          </VStack>
        </FormControl>

        <ButtonGroup spacing={4}>
          <Button 
            onClick={() => navigate('/app')}
            colorScheme="yellow"
            variant="outline"
            size="lg"
            px={8}
            borderRadius="full"
            fontWeight="300"
            letterSpacing="0.05em"
            _hover={{
              bg: "yellow.50"
            }}
          >
            SKIP
          </Button>
          <Button 
            onClick={() => navigate('/app')}
            colorScheme="yellow"
            size="lg"
            px={8}
            borderRadius="full"
            fontWeight="300"
            letterSpacing="0.05em"
            _hover={{
              transform: 'translateY(-2px)',
              boxShadow: 'lg',
            }}
          >
            NEXT
          </Button>
        </ButtonGroup>
      </VStack>
    </Flex>
  );
};

export default VehicleDetails;