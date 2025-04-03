import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Box, Button, ButtonGroup, VStack } from '@chakra-ui/react';
import SignIn from './SignIn';
import SignUp from './SignUp';

const AuthPage = () => {
  const [searchParams] = useSearchParams();
  const initialMode = searchParams.get('mode') || 'signin';
  const [mode, setMode] = useState(initialMode);

  return (
    <Box p={8} maxWidth="500px" mx="auto">
      <VStack spacing={8} align="center" w="full">
        <ButtonGroup size="lg" isAttached variant="outline">
          <Button 
            onClick={() => setMode('signin')}
            colorScheme={mode === 'signin' ? 'yellow' : 'gray'}
          >
            Sign In
          </Button>
          <Button 
            onClick={() => setMode('signup')}
            colorScheme={mode === 'signup' ? 'yellow' : 'gray'}
          >
            Sign Up
          </Button>
        </ButtonGroup>
        
        {mode === 'signin' ? <SignIn /> : <SignUp />}
      </VStack>
    </Box>
  );
};

export default AuthPage;