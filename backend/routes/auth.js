const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const User = require('../models/User');

const JWT_SECRET = process.env.JWT_SECRET || 'fallback_secret_key_123';

// Login Route
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // Find user
    const user = await User.findOne({ username }).populate('tenant');
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const tenantObj = user.tenant || user.tenant_id;

    // Verify password hash
    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Create JWT Payload
    const payload = {
      userId: user._id,
      username: user.username,
      role: user.role,
      tenantId: tenantObj ? tenantObj._id : null,
      tenantSlug: tenantObj ? tenantObj.slug : null
    };

    // Sign Token
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '1d' });

    res.json({
      message: 'Login successful',
      token,
      user: {
        username: user.username,
        full_name: user.full_name,
        role: user.role,
        tenant: tenantObj ? { name: tenantObj.name, slug: tenantObj.slug } : null
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Middleware to verify JWT for protected routes
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) return res.status(401).json({ error: 'Access denied' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid token' });
    req.user = user;
    next();
  });
};

router.get('/me', authenticateToken, async (req, res) => {
  res.json({ user: req.user });
});

module.exports = { router, authenticateToken };
