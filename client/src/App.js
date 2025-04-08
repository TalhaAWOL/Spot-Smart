import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import VehicleDetails from './components/VehicleDetails';
import NavigationApp from './components/NavigationApp';
import AuthPage from './components/AuthPage';
import { AuthProvider } from './components/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route 
            path="/vehicle" 
            element={
              <ProtectedRoute>
                <VehicleDetails />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/app" 
            element={
              <ProtectedRoute>
                <NavigationApp />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
