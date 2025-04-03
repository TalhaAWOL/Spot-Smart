import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Input, 
  VStack, 
  Heading, 
  Text,
  Link,
  Flex,
  useToast
} from '@chakra-ui/react';
import { FaCar, FaKey, FaEnvelope } from 'react-icons/fa';
import { useAuth } from './AuthContext';

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    const result = await signIn(formData);
    setIsSubmitting(false);

    if (!result.success) {
      toast({
        title: 'Error',
        description: result.message,
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box 
      minH="100vh" 
      bg="yellow.400" 
      w="100vw"
      overflowX="hidden"
    >
      <Flex
        justify="center"
        align="center"
        minH="100vh"
        py={8}
        px={4}
      >
        <Flex 
          maxWidth="1200px"
          width="60%"
          mx="auto"
          bg="white"
          borderRadius="xl"
          boxShadow="lg"
          minH="70vh"
          overflow="hidden"
        >
          
          <Box 
            width={{ base: "100%", md: "40%" }}
            bg="gray.50"
            p={8}
            display={{ base: "none", md: "block" }}
            position="relative"
          >
           
            <Box 
              textAlign="center" 
              h="100%"
              display="flex"
              flexDirection="column"
              justifyContent="center"
              alignItems="center"
            >
              <img 
                src="/images/car1.jpeg" 
                alt="Parking illustration"
                style={{ 
                  maxWidth: "100%",
                  maxHeight: "300px",
                  objectFit: "contain"
                }}
              />
              <Heading size="lg" mt={8} color="yellow.500">
                Welcome Back!
              </Heading>
              <Text mt={4} fontSize="lg" color="gray.600">
                Ready to find your perfect spot?
              </Text>
            </Box>
  
           
            <Box position="absolute" top="-50px" right="-50px" opacity="0.1">
              <FaCar size="150px" color="yellow.400" />
            </Box>
            <Box position="absolute" bottom="-50px" left="-50px" opacity="0.1" transform="rotate(180deg)">
              <FaCar size="150px" color="yellow.400" />
            </Box>
          </Box>
  
          
          <Box 
            width={{ base: "100%", md: "60%" }}
            p={10}
            display="flex"
            flexDirection="column"
            justifyContent="center"
          >
            <VStack spacing={6} align="flex-start" w="full">
              <Flex align="center">
                <Box color="yellow.500" mr={3}>
                  <FaCar size="24px" />
                </Box>
                <Heading size="xl" color="yellow.500">Sign In</Heading>
              </Flex>
              
              <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                <VStack spacing={5} align="flex-start">
                 
                  <FormControl isInvalid={errors.email}>
                    <FormLabel color="gray.600" fontSize="sm" fontWeight="normal" mb={1}>
                      Email
                    </FormLabel>
                    <Input
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      borderColor="gray.300"
                      focusBorderColor="yellow.500"
                      h="45px"
                    />
                    {errors.email && (
                      <Text color="red.500" fontSize="xs" mt={1}>
                        {errors.email}
                      </Text>
                    )}
                  </FormControl>
  
                 
                  <FormControl isInvalid={errors.password}>
                    <FormLabel color="gray.600" fontSize="sm" fontWeight="normal" mb={1}>
                      Password
                    </FormLabel>
                    <Input
                      name="password"
                      type="password"
                      value={formData.password}
                      onChange={handleChange}
                      borderColor="gray.300"
                      focusBorderColor="yellow.500"
                      h="45px"
                    />
                    {errors.password && (
                      <Text color="red.500" fontSize="xs" mt={1}>
                        {errors.password}
                      </Text>
                    )}
                  </FormControl>
  
                
                  <Button
                    type="submit"
                    colorScheme="yellow"
                    width="full"
                    size="lg"
                    mt={4}
                    isLoading={isSubmitting}
                    loadingText="Signing In..."
                    leftIcon={<FaCar />}
                  >
                    Continue to Parking
                  </Button>
                </VStack>
              </form>
  
              <Text textAlign="center" w="full" mt={4}>
                Don't have an account?{' '}
                <Link 
                  color="yellow.600" 
                  fontWeight="600"
                  onClick={() => navigate('/auth?mode=signup')}
                >
                  Sign Up
                </Link>
              </Text>
            </VStack>
          </Box>
        </Flex>
      </Flex>
    </Box>
  );
};

export default SignIn;