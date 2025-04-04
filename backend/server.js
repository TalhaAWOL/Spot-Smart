require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();

app.use((req, res, next) => {
  console.log(`Incoming ${req.method} request to ${req.url}`);
  next();
});

// Middleware
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// MongoDB Connection
// In server.js, add better MongoDB connection logging:
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('MongoDB connected successfully'))
.catch(err => console.error('MongoDB connection FAILED:', err.message));

// User Model
const UserSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  vehicleType: { type: String, default: '' },
  licensePlate: { type: String, default: '' },
  vehicleColor: { type: String, default: '' },
  searchHistory: {
    origins: { type: [String], default: [] },
    destinations: { type: [String], default: [] }
  },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', UserSchema);

// Auth Routes
// In server.js signup route:
app.post('/api/auth/signup', async (req, res) => {
  console.log('Request body:', req.body);
  try {
    console.log('Signup request:', req.body); // Log incoming data
    
    const { name, email, password } = req.body;
    if (!name || !email || !password) {
      console.log('Validation failed - missing fields');
      return res.status(400).json({ message: 'All fields are required' });
    }

    // Check for existing user
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      console.log('User already exists:', email);
      return res.status(400).json({ message: 'Email already registered' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    console.log('Password hashed successfully');

    // Create user
    const user = new User({ name, email, password: hashedPassword });
    await user.save();
    console.log('User saved to DB:', user._id);

    // Generate token
    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: '1d' }
    );

    res.status(201).json({ 
      token,
      user: { id: user._id, name, email }
    });
    
  } catch (err) {
    console.error('Signup error:', err.stack); // Full error stack
    res.status(500).json({ 
      message: err.message || 'Registration failed' 
    });
  }
});

// Signin Route
app.post('/api/auth/signin', async (req, res) => {
  try {
    const { email, password } = req.body;
    console.log('Signin attempt for:', email);

    // 1. Find user
    const user = await User.findOne({ email });
    if (!user) {
      console.log('User not found');
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // 2. Debug password comparison
    console.log('Input password:', password);
    console.log('Stored hash:', user.password);
    const isMatch = await bcrypt.compare(password, user.password);
    console.log('Password match result:', isMatch);

    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // 3. Create token
    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: '1d' }
    );

    console.log('Successful login for:', email);
    res.json({ 
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        vehicleType: user.vehicleType,
        licensePlate: user.licensePlate,
        vehicleColor: user.vehicleColor
      }
    });
    
  } catch (err) {
    console.error('Signin error:', err);
    res.status(500).json({ message: 'Login failed' });
  }
});

// Protected route example
app.get('/api/auth/user', async (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ message: 'No token provided' });

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.id).select('-password');

    if (!user) return res.status(404).json({ message: 'User not found' });

    res.json(user);
  } catch (err) {
    res.status(500).json({ message: 'Invalid token' });
  }
});

// Update vehicle details
app.put('/api/user/vehicle', async (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ message: 'No token provided' });

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const { vehicleType, licensePlate, vehicleColor } = req.body;

    const updatedUser = await User.findByIdAndUpdate(
      decoded.id,
      { vehicleType, licensePlate, vehicleColor },
      { new: true }
    ).select('-password');

    res.json(updatedUser);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Save search location
app.post('/api/search/save', async (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ message: 'No token provided' });

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const { origin, destination } = req.body;

    // Update user's search history (keeping only last 5 entries)
    const user = await User.findById(decoded.id);
    
    if (origin && origin !== "Current Location") {
      user.searchHistory.origins = [
        origin,
        ...user.searchHistory.origins.filter(item => item !== origin)
      ].slice(0, 5);
    }

    if (destination) {
      user.searchHistory.destinations = [
        destination,
        ...user.searchHistory.destinations.filter(item => item !== destination)
      ].slice(0, 5);
    }

    await user.save();
    res.json({ message: 'Search history updated' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get search history
app.get('/api/search/history', async (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ message: 'No token provided' });

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.id).select('searchHistory');

    res.json({
      origins: ["Current Location", ...user.searchHistory.origins],
      destinations: user.searchHistory.destinations
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));