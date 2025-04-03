import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Box, Flex, Heading, Text, Button, Icon } from '@chakra-ui/react';
import { FaCar } from 'react-icons/fa';
import '@fontsource/inter';

const LandingPage = () => {
    const navigate = useNavigate();
    const floatingElements = [
        { id: 1, text: '<', size: '80px', color: 'rgba(255, 0, 0, 0.7)' },
        { id: 2, text: '>', size: '60px', color: 'rgba(0, 255, 0, 0.7)' },
        { id: 3, text: '^', size: '70px', color: 'rgba(0, 0, 255, 0.7)' },
        { id: 4, text: '<', size: '90px', color: 'rgba(255, 255, 0, 0.7)' },
        { id: 5, text: '>', size: '50px', color: 'rgba(255, 0, 255, 0.7)' },
        { id: 6, text: '^', size: '65px', color: 'rgba(0, 255, 255, 0.7)' },
        { id: 7, text: '<', size: '75px', color: 'rgba(255, 165, 0, 0.7)' },
        { id: 8, text: '>', size: '85px', color: 'rgba(128, 0, 128, 0.7)' },
        { id: 9, text: '^', size: '85px', color: 'rgba(128, 0, 128, 0.7)' },
        { id: 10, text: '<', size: '85px', color: 'rgba(128, 0, 128, 0.7)' },
        { id: 11, text: '>', size: '85px', color: 'rgba(128, 0, 128, 0.7)' },
        { id: 12, text: '^', size: '50px', color: 'rgba(255, 0, 255, 0.7)' },
        { id: 13, text: '>', size: '50px', color: 'rgba(255, 0, 255, 0.7)' },
        { id: 14, text: '>', size: '50px', color: 'rgba(255, 0, 255, 0.7)' }
    ];

  const floatVariants = {
    initial: {
      y: 0,
      x: 0,
      rotate: 0
    },
    animate: (i) => ({
      y: [0, -100, 100, 0],
      x: [0, 100, -100, 0],
      rotate: [0, 180, 360],
      transition: {
        duration: 20 + Math.random() * 20,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'linear',
        delay: i * 2
      }
    })
  };

  return (
    <Box
        position="relative"
        width="100vw"
        height="100vh"
        overflow="hidden"
        bg="white"
        color="black"
        fontFamily="Roboto, sans-serif"
    >
      {floatingElements.map((element, i) => (
        <motion.div
          key={element.id}
          style={{
            position: 'absolute',
            top: `${Math.random() * 80 + 10}%`,
            left: `${Math.random() * 80 + 10}%`,
            fontSize: element.size,
            color: element.color,
            fontWeight: 'bold',
            zIndex: 1
          }}
          variants={floatVariants}
          initial="initial"
          animate="animate"
          custom={i}
        >
          {element.text}
        </motion.div>
      ))}

<Flex
                position="absolute"
                width="100%"
                height="100%"
                alignItems="center"
                justifyContent="center"
                flexDirection="column"
                zIndex="2"
                textAlign="center"
                px={4}
            >
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1 }}
                >
                    {/* Added Car Icon */}
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        <Icon
                            as={FaCar}
                            w={20}
                            h={20}
                            color="yellow.500"
                            mb={8}
                            _hover={{
                                transform: 'translateY(-5px)',
                                transition: 'transform 0.3s ease'
                            }}
                        />
                    </motion.div>

                    <Heading 
                        fontSize={["5xl", "6xl", "7xl"]} 
                        color="yellow.500"
                        fontWeight="300"
                        fontFamily="Roboto"
                        letterSpacing="0.1em"
                        mb={6}
                    >
                        SHERIDAN SPOT SMART
                    </Heading>
                    
                    <Button 
                        onClick={() => navigate('/auth')}
                        colorScheme="yellow" 
                        size="lg"
                        px={12}
                        py={6}
                        borderRadius="full"
                        boxShadow="xl"
                        _hover={{
                            transform: 'translateY(-2px)',
                            boxShadow: '2xl',
                        }}
                        transition="all 0.3s ease"
                        fontWeight="300"
                        letterSpacing="0.1em"
                    >
                        GET STARTED
                    </Button>
                </motion.div>
            </Flex>
        </Box>
    );
};

export default LandingPage;