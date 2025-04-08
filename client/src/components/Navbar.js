import {
  Flex,
  Text,
  IconButton,
  useDisclosure,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
  Stack,
  useBreakpointValue,
  Icon,
  Box,
} from "@chakra-ui/react";
import { FaBars } from "react-icons/fa";
import { MdCarCrash } from "react-icons/md";
import { Link } from "react-router-dom";

const Navbar = ({ color = "yellow.500" }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  return (
    <>
      <Flex
        p={4}
        boxShadow="md"
        position="fixed"
        width="100%"
        top={0}
        zIndex={1000}
        backdropFilter="blur(5px)"
        color={color}
      >
        <Flex flex={1} justify="space-between" align="center">
          <Link to="/" onClick={onClose}>
            <Flex align="center" mr={8}>
              <Icon as={MdCarCrash} w={8} h={8} color="yellow.500" mr={2} />
              <Text fontSize="xl" fontWeight="bold" color="yellow.500">
                Spot Smart
              </Text>
            </Flex>
          </Link>

          {!isMobile && (
            <Flex gap={6}>
              <Link to="/">Home</Link>
              <Link to="/app">Navigate</Link>
              <Link to="/vehicle">Vehicle</Link>
            </Flex>
          )}

          

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

      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay>
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>
              <Flex align="center">
                <Icon as={MdCarCrash} w={6} h={6} color="yellow.500" mr={2} />
                <Text color="yellow.500">Spot Smart</Text>
              </Flex>
            </DrawerHeader>
            <DrawerBody>
              <Stack spacing={4}>
                <Link to="/" onClick={onClose}>
                  Home
                </Link>
                <Link to="/app" onClick={onClose}>
                  Navigate
                </Link>
                <Link to="/vehicle" onClick={onClose}>
                  Vehicle
                </Link>
              </Stack>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>
    </>
  );
};

export default Navbar;
