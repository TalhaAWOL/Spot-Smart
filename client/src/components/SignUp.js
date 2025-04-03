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
  useToast
} from '@chakra-ui/react';
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
        // Show detailed error
        toast({
          title: 'Signup Failed',
          description: result.message || 'Unknown error',
          status: 'error',
          duration: 9000, // Longer visibility
          isClosable: true,
        });
      }
    } catch (err) {
      console.error('Signup error:', err); // Check browser console
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
    <Box p={8} maxWidth="500px" mx="auto">
      <VStack spacing={4} align="flex-start" w="full">
        <Heading size="lg" color="yellow.500">Create an account</Heading>
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <VStack spacing={4} align="flex-start">
            <FormControl isInvalid={errors.name}>
              <FormLabel>Full Name</FormLabel>
              <Input
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
              />
              {errors.name && <Text color="red.500" fontSize="sm">{errors.name}</Text>}
            </FormControl>
            <FormControl isInvalid={errors.email}>
              <FormLabel>Email</FormLabel>
              <Input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
              />
              {errors.email && <Text color="red.500" fontSize="sm">{errors.email}</Text>}
            </FormControl>
            <FormControl isInvalid={errors.password}>
              <FormLabel>Password</FormLabel>
              <Input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
              />
              {errors.password && <Text color="red.500" fontSize="sm">{errors.password}</Text>}
            </FormControl>
            <FormControl isInvalid={errors.confirmPassword}>
              <FormLabel>Confirm Password</FormLabel>
              <Input
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              {errors.confirmPassword && <Text color="red.500" fontSize="sm">{errors.confirmPassword}</Text>}
            </FormControl>
            <Button 
              type="submit" 
              colorScheme="yellow" 
              width="full"
              isLoading={isSubmitting}
              loadingText="Signing Up..."
            >
              Sign Up
            </Button>
          </VStack>
        </form>
        <Text>
          Already have an account?{' '}
          <Link color="yellow.500" onClick={() => navigate('/auth')}>
            Sign In
          </Link>
        </Text>
      </VStack>
    </Box>
  );
};

export default SignUp;