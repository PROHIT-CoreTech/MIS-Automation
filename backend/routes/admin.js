const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { authenticateToken } = require('./auth');
const Tenant = require('../models/Tenant');
const User = require('../models/User');
const Company = require('../models/Company');

// Middleware to check for super_admin
const requireSuperAdmin = (req, res, next) => {
  if (req.user && req.user.role === 'super_admin') {
    next();
  } else {
    res.status(403).json({ error: 'Super Admin access required' });
  }
};

// Get Dashboard Data (Tenants + Stats)
router.get('/dashboard', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const tenants = await Tenant.find().sort({ created_at: -1 });
    const totalUsers = await User.countDocuments();
    
    // Aggregate client count per tenant (role = 'client' or 'user')
    const clientCountsByTenant = await User.aggregate([
      { $match: { role: { $in: ['client', 'user'] }, tenant: { $ne: null } } },
      { $group: { _id: '$tenant', count: { $sum: 1 } } }
    ]);
    const clientCountMap = {};
    clientCountsByTenant.forEach(item => {
      clientCountMap[item._id.toString()] = item.count;
    });

    // MRR Mapping based on official plan prices
    const mrrMap = { 'Gold': 9999, 'Silver': 4999, 'Bronze': 2999 };
    let totalMrr = 0;
    
    const activeSubscriptions = tenants.filter(t => t.is_active !== false).length;
    
    const formattedTenants = tenants.map(t => {
      const plan = t.plan_name || 'Silver';
      const mrr = mrrMap[plan] || 4999;
      const isActive = t.is_active !== false;
      if (isActive) totalMrr += mrr;

      // features may be stored as a JSON string (from Python) or as an array
      let features = t.features || [];
      if (typeof features === 'string') {
        try { features = JSON.parse(features); } catch (e) { features = []; }
      }
      if (!Array.isArray(features)) features = [];

      // Format created_at
      const createdAt = t.created_at
        ? new Date(t.created_at).toISOString().replace('T', ' ').substring(0, 19)
        : '—';
      
      return {
        id: t._id.toString(),
        name: t.name,
        slug: t.slug,
        plan: plan,
        status: isActive ? 'active' : 'suspended',
        mrr: mrr,
        features: features,
        is_active: isActive,
        created_at: createdAt,
        client_count: clientCountMap[t._id.toString()] || 0
      };
    });

    res.json({
      tenant: formattedTenants,
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

// Suspend or Activate Tenant (Legacy endpoint)
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

// Register Tenant + Tenant Admin
router.post('/tenants', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { name, slug, plan_name, features, admin_name, admin_user, admin_pass } = req.body;
    
    // Check if tenant slug already exists
    const existingTenant = await Tenant.findOne({ slug });
    if (existingTenant) {
      return res.status(400).json({ error: 'Tenant slug already exists' });
    }

    // Check if admin username already exists
    const existingUser = await User.findOne({ username: admin_user });
    if (existingUser) {
      return res.status(400).json({ error: 'Admin username already exists' });
    }

    // Create tenant
    const tenant = new Tenant({
      name,
      slug,
      plan_name,
      features: features || [],
      is_active: true
    });
    await tenant.save();

    // Hash admin password
    const salt = await bcrypt.genSalt(12);
    const password_hash = await bcrypt.hash(admin_pass, salt);

    // Create admin user
    const user = new User({
      tenant: tenant._id,
      username: admin_user,
      password_hash,
      full_name: admin_name,
      role: 'admin',
      can_download_excel: true,
      can_download_ppt: true,
      is_active: true
    });
    await user.save();

    res.status(201).json({
      message: 'Tenant and Admin created successfully',
      tenant,
      user: {
        id: user._id,
        username: user.username,
        full_name: user.full_name,
        role: user.role
      }
    });
  } catch (error) {
    console.error('Error creating tenant:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update Tenant details
router.put('/tenants/:id', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { plan_name, features, is_active } = req.body;
    const updateData = {};
    if (plan_name !== undefined) updateData.plan_name = plan_name;
    if (features !== undefined) updateData.features = features;
    if (is_active !== undefined) updateData.is_active = is_active;

    const tenant = await Tenant.findByIdAndUpdate(
      req.params.id,
      updateData,
      { new: true }
    );
    if (!tenant) return res.status(404).json({ error: 'Tenant not found' });
    res.json(tenant);
  } catch (error) {
    console.error('Error updating tenant:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get users under a specific tenant
router.get('/tenants/:id/users', authenticateToken, async (req, res) => {
  try {
    // Check if requester is super_admin OR admin of this tenant
    if (req.user.role !== 'super_admin' && req.user.tenantId !== req.params.id) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const users = await User.find({ tenant: req.params.id }).populate('companies');
    res.json(users);
  } catch (error) {
    console.error('Error fetching tenant users:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a user under a tenant
router.post('/users', authenticateToken, async (req, res) => {
  try {
    const { username, password, full_name, role, tenantId, companies, can_download_excel, can_download_ppt } = req.body;

    // Check if requester is super_admin OR admin of this tenant
    if (req.user.role !== 'super_admin' && req.user.tenantId !== tenantId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Check if username exists
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(12);
    const password_hash = await bcrypt.hash(password, salt);

    const user = new User({
      tenant: tenantId,
      username,
      password_hash,
      full_name,
      role: role || 'client',
      can_download_excel: can_download_excel !== undefined ? can_download_excel : true,
      can_download_ppt: can_download_ppt !== undefined ? can_download_ppt : false,
      companies: companies || [],
      is_active: true
    });
    await user.save();

    res.status(201).json(user);
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user permissions / assigned companies
router.put('/users/:id/permissions', authenticateToken, async (req, res) => {
  try {
    const { can_download_excel, can_download_ppt, companies } = req.body;
    
    // Find user to check tenant
    const user = await User.findById(req.params.id);
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Check permission
    if (req.user.role !== 'super_admin' && req.user.tenantId !== user.tenant?.toString()) {
      return res.status(403).json({ error: 'Access denied' });
    }

    if (can_download_excel !== undefined) user.can_download_excel = can_download_excel;
    if (can_download_ppt !== undefined) user.can_download_ppt = can_download_ppt;
    if (companies !== undefined) user.companies = companies;

    await user.save();
    res.json(user);
  } catch (error) {
    console.error('Error updating user permissions:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a tenant user
router.delete('/users/:id', authenticateToken, async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Check permission
    if (req.user.role !== 'super_admin' && req.user.tenantId !== user.tenant?.toString()) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await User.findByIdAndDelete(req.params.id);
    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get companies for a specific tenant
router.get('/tenants/:id/companies', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'super_admin' && req.user.tenantId !== req.params.id) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const companies = await Company.find({ tenant: req.params.id });
    res.json(companies);
  } catch (error) {
    console.error('Error fetching tenant companies:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
