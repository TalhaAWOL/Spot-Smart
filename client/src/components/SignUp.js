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
import { FaCar, FaKey, FaUser, FaEnvelope,FaCheckCircle } from 'react-icons/fa';
import { useAuth } from './AuthContext';

const SignUp = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signUp } = useAuth();
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
    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
  
    setIsSubmitting(true);
    const { confirmPassword, ...userData } = formData;
    
    try {
      const result = await signUp(userData);
      
      if (result.success) {
        toast({ title: 'Account created!', status: 'success' });
      } else {
        
        toast({
          title: 'Signup Failed',
          description: result.message || 'Unknown error',
          status: 'error',
          duration: 9000, 
          isClosable: true,
        });
      }
    } catch (err) {
      console.error('Signup error:', err); 
      toast({
        title: 'Network Error',
        description: 'Could not reach server',
        status: 'error',
      });
    } finally {
      setIsSubmitting(false);
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
      >
        <Flex 
          maxWidth="1400px" 
          width="60%"
          mx="auto"
          bg="white"
          borderRadius="xl"
          boxShadow="lg"
          minH="80vh" 
        >
          
          <Box 
            width={{ base: "100%", md: "50%" }}
            bg="gray.50"
            p={8}
            display={{ base: "none", md: "block" }}
            position="relative"
          >
            
            <Box 
              textAlign="center" 
              mb={8}
              h="350px" 
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <img 
                src="/images/car2.jpeg" 
                alt="Car illustration"
                style={{ 
                  maxWidth: "100%",
                  maxHeight: "100%",
                  objectFit: "contain"
                }}
              />
            </Box>
  
            
            <Box>
              <Heading size="lg" mb={4} color="yellow.500">
                Book With <span style={{ fontWeight: "bold" }}>Sheridan Spot</span>
              </Heading>
              <Text mb={6} fontSize="lg">We'll save a spot for ya!</Text>
  
              <VStack align="flex-start" spacing={5}>
                <Flex align="center">
                  <Box color="green.500" mr={3}>
                    <FaCheckCircle size="20px" />
                  </Box>
                  <Text fontSize="sm">Save up to 50% off drive-up rates</Text>
                </Flex>
  
                <Flex align="center">
                  <Box color="green.500" mr={3}>
                    <FaCheckCircle size="20px" />
                  </Box>
                  <Text fontSize="sm">Book your space in advance</Text>
                </Flex>
  
                <Flex align="center">
                  <Box color="green.500" mr={3}>
                    <FaCheckCircle size="20px" />
                  </Box>
                  <Text fontSize="sm">Get a parking pass on your phone</Text>
                </Flex>
              </VStack>
            </Box>
  
           
            <Box position="absolute" top="-50px" right="-50px" opacity="0.1">
              <FaCar size="150px" color="yellow.400" />
            </Box>
            <Box position="absolute" bottom="-50px" left="-50px" opacity="0.1" transform="rotate(180deg)">
              <FaCar size="150px" color="yellow.400" />
            </Box>
          </Box>
  
         
          <Box 
            width={{ base: "100%", md: "50%" }}
            p={8}
          >
            <VStack spacing={6} align="flex-start" w="full">
              <Flex align="center">
                <Box color="yellow.500" mr={3}>
                  <FaCar size="24px" />
                </Box>
                <Heading size="xl" color="yellow.500">Create Account</Heading>
              </Flex>
              
              <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                <VStack spacing={5} align="flex-start">
                  
                  <FormControl isInvalid={errors.name}>
                    <FormLabel color="gray.600" fontSize="sm" fontWeight="normal" mb={1}>
                      Full Name
                    </FormLabel>
                    <Input
                      name="name"
                      type="text"
                      value={formData.name}
                      onChange={handleChange}
                      borderColor="gray.300"
                      focusBorderColor="yellow.500"
                      h="45px"
                    />
                    {errors.name && (
                      <Text color="red.500" fontSize="xs" mt={1}>
                        {errors.name}
                      </Text>
                    )}
                  </FormControl>
    
                
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
    
               
                <FormControl isInvalid={errors.confirmPassword}>
                  <FormLabel color="gray.600" fontSize="sm" fontWeight="normal" mb={1}>
                    Confirm Password
                  </FormLabel>
                  <Input
                    name="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    borderColor="gray.300"
                    focusBorderColor="yellow.500"
                    h="45px"
                  />
                  {errors.confirmPassword && (
                    <Text color="red.500" fontSize="xs" mt={1}>
                      {errors.confirmPassword}
                    </Text>
                  )}
                </FormControl>
    
                
                <Text fontSize="sm" color="gray.600" mt={2}>
                  By continuing, you agree to our{' '}
                  <Link color="yellow.600" fontWeight="600">
                    Terms
                  </Link>{' '}
                  and{' '}
                  <Link color="yellow.600" fontWeight="600">
                    Privacy Policy
                  </Link>
                  .
                </Text>
    
                
                <Button
                  type="submit"
                  colorScheme="yellow"
                  width="full"
                  size="lg"
                  mt={4}
                  isLoading={isSubmitting}
                  loadingText="Signing Up..."
                  leftIcon={<FaCar />}
                >
                  Sign Up
                </Button>
              </VStack>
            </form>

            <Text textAlign="center" w="full" mt={4}>
              Already have an account?{' '}
              <Link 
                color="yellow.600" 
                fontWeight="600"
                onClick={() => navigate('/auth')}
              >
                Sign In
              </Link>
            </Text>
          </VStack>
        </Box>
      </Flex>
    </Flex>
  </Box>
);
};

export default SignUp;