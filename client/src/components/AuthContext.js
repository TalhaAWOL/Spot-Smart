import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const isAuthenticated = () => {
    return !!user; // or more sophisticated authentication check
  };

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const res = await axios.get(`/api/auth/user`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          setUser(res.data);
        }
      } catch (err) {
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const signUp = async (formData) => {
    try {
      const res = await axios.post(`/api/auth/signup`, formData);
      localStorage.setItem('token', res.data.token);
      setUser(res.data.user);
      navigate('/vehicle');
      return { success: true };
    } catch (err) {
      return { 
        success: false, 
        message: err.response?.data?.message || 'Signup failed' 
      };
    }
  };

  const signIn = async (formData) => {
    try {
      const res = await axios.post(`/api/auth/signin`, formData);
      localStorage.setItem('token', res.data.token);
      setUser(res.data.user);
      navigate('/vehicle');
      return { success: true };
    } catch (err) {
      return { 
        success: false, 
        message: err.response?.data?.message || 'Invalid credentials' 
      };
    }
  };

  const signOut = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/auth');
  };

  const updateVehicleDetails = async (details) => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.put(`/api/user/vehicle`, details, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setUser(res.data);
      return { success: true };
    } catch (err) {
      return { 
        success: false, 
        message: err.response?.data?.message || 'Update failed' 
      };
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signUp,
        signIn,
        signOut,
        updateVehicleDetails,
        isAuthenticated
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);