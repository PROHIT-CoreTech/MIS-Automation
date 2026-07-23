const dns = require('dns');
try { dns.setDefaultResultOrder('ipv4first'); } catch (e) {}
require('dotenv').config({ path: '../.env' }); // Load .env from root
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Global API Request & Response Debug Logger Middleware
app.use((req, res, next) => {
  const startTime = Date.now();
  const { method, originalUrl, query, body } = req;

  console.log(`\n==================================================`);
  console.log(`📥 [REQUEST] ${method} ${originalUrl}`);
  if (query && Object.keys(query).length > 0) {
    console.log(`   Query Params :`, JSON.stringify(query, null, 2));
  }
  if (body && Object.keys(body).length > 0) {
    const safeBody = { ...body };
    if (safeBody.password) safeBody.password = '***HIDDEN***';
    console.log(`   Request Body :`, JSON.stringify(safeBody, null, 2));
  }

  // Intercept res.json to log output payload and duration
  const originalJson = res.json;
  res.json = function (data) {
    const duration = Date.now() - startTime;
    console.log(`📤 [RESPONSE] ${method} ${originalUrl} | Status: ${res.statusCode} (${duration}ms)`);
    console.log(`   Response Body:`, JSON.stringify(data, null, 2));
    console.log(`==================================================\n`);
    return originalJson.call(this, data);
  };

  next();
});

// Database Connection
const MONGO_URI = process.env.MONGO_URI_DEVELOPMENT;

const connectWithRetry = () => {
  mongoose.connect(MONGO_URI)
    .then(() => console.log('✅ Connected to MongoDB Atlas'))
    .catch((err) => {
      console.error('❌ MongoDB Connection Error:', err.message || err);
      console.log('🔄 Retrying MongoDB connection in 10 seconds...');
      setTimeout(connectWithRetry, 10000);
    });
};

connectWithRetry();

// Routes
const authRoutes = require('./routes/auth').router;
const adminRoutes = require('./routes/admin');
const financialRoutes = require('./routes/financial');

app.use('/api/auth', authRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/financial', financialRoutes);

// Basic Health Check Route
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Backend is running correctly.' });
});

// Start Server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`🚀 Express server running on http://localhost:${PORT}`);
});
