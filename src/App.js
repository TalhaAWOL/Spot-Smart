import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import VehicleDetails from './components/VehicleDetails';
import NavigationApp from './components/NavigationApp';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/vehicle" element={<VehicleDetails />} />
        <Route path="/app" element={<NavigationApp />} />
      </Routes>
    </Router>
  );
}

export default App;