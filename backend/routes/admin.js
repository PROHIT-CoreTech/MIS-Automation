const express = require('express');
const router = express.Router();
// const { authenticateToken } = require('./auth');
const Tenant = require('../models/Tenant');
const User = require('../models/User');

// Middleware to check for super_admin (disabled for dev demo)
const requireSuperAdmin = (req, res, next) => {
  next(); // Bypassing auth for frontend integration demo
};

const authenticateToken = (req, res, next) => {
  next(); // Bypassing auth for frontend integration demo
};

// Get Dashboard Data (Tenants + Stats)
router.get('/dashboard', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const tenants = await Tenant.find().sort({ created_at: -1 });
    const totalUsers = await User.countDocuments();
    
    // MRR Mapping based on official plan prices
    const mrrMap = { 'Gold': 9999, 'Silver': 4999, 'Bronze': 2999 };
    let totalMrr = 0;
    
    const activeSubscriptions = tenants.filter(t => t.is_active !== false).length;
    
    const formattedTenants = tenants.map(t => {
      const plan = t.plan_name || 'Silver';
      const mrr = mrrMap[plan] || 4999;
      const isActive = t.is_active !== false;
      if (isActive) totalMrr += mrr;
      
      return {
        id: t._id.toString(),
        name: t.name,
        slug: t.slug,
        plan: plan,
        status: isActive ? 'active' : 'suspended',
        mrr: mrr
      };
    });

    res.json({
      tenants: formattedTenants,
      stats: {
        total_mrr: totalMrr,
        active_subscriptions: activeSubscriptions,
        total_users: totalUsers
      }
    });
  } catch (error) {
    console.error('Error fetching admin dashboard data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all tenants (Legacy endpoint)
router.get('/tenants', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const tenants = await Tenant.find().sort({ created_at: -1 });
    res.json(tenants);
  } catch (error) {
    console.error('Error fetching tenants:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Suspend or Activate Tenant
router.put('/tenants/:id/status', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { is_active } = req.body;
    const tenant = await Tenant.findByIdAndUpdate(
      req.params.id,
      { is_active },
      { new: true }
    );
    if (!tenant) return res.status(404).json({ error: 'Tenant not found' });
    res.json(tenant);
  } catch (error) {
    console.error('Error updating tenant:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
