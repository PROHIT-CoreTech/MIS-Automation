const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');
const PLData = require('../models/PLData');
const BSData = require('../models/BSData');
const AgeingData = require('../models/AgeingData');
const Company = require('../models/Company');

// Middleware to ensure user is accessing their own tenant data
const requireTenantAccess = (req, res, next) => {
  if (req.user && req.user.tenantId) {
    next();
  } else if (req.user && req.user.role === 'super_admin') {
    next();
  } else {
    res.status(403).json({ error: 'Tenant access required' });
  }
};

// Get P&L Data for a tenant's companies
router.get('/pl-data', authenticateToken, requireTenantAccess, async (req, res) => {
  try {
    const { year, month } = req.query;
    
    // Find all companies for this tenant
    const companies = await Company.find({ tenant: req.user.tenantId });
    const companyIds = companies.map(c => c._id);

    let filter = { company: { $in: companyIds } };
    if (year) filter.year = Number(year);
    if (month) filter.month = Number(month);

    const plData = await PLData.find(filter).populate('company');
    res.json(plData);
  } catch (error) {
    console.error('Error fetching P&L data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get BS Data for a tenant's companies
router.get('/bs-data', authenticateToken, requireTenantAccess, async (req, res) => {
  try {
    const { year, month } = req.query;
    
    const companies = await Company.find({ tenant: req.user.tenantId });
    const companyIds = companies.map(c => c._id);

    let filter = { company: { $in: companyIds } };
    if (year) filter.year = Number(year);
    if (month) filter.month = Number(month);

    const bsData = await BSData.find(filter).populate('company');
    res.json(bsData);
  } catch (error) {
    console.error('Error fetching BS data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get Tenant Dashboard Financial Summary directly from MongoDB
router.get('/dashboard/:tenantSlug', async (req, res) => {
  try {
    const { tenantSlug } = req.params;
    const Tenant = require('../models/Tenant');
    const tenant = await Tenant.findOne({ slug: tenantSlug });
    if (!tenant) {
      return res.status(404).json({ error: 'Tenant not found' });
    }

    const company = await Company.findOne({ tenant: tenant._id });
    if (!company) {
      return res.json({
        companyName: tenant.name,
        dateRange: "No company linked yet",
        stats: { totalRevenue: 0, grossProfit: 0, netProfit: 0, cashBank: 0, overhead: 0, gpPct: 0, npPct: 0 },
        chartData: [],
        overheadData: []
      });
    }

    // Query PL Data for this company
    const plRecords = await PLData.find({ company: company._id }).sort({ year: 1, month: 1 });
    
    // Group monthly PL metrics
    const monthMap = {};
    let totalRevenue = 0;
    let totalGP = 0;
    let totalNP = 0;
    let totalOverhead = 0;
    const overheadCategories = {};

    plRecords.forEach(rec => {
      const monthKey = rec.month_label || `${rec.year}-${String(rec.month).padStart(2, '0')}`;
      if (!monthMap[monthKey]) {
        monthMap[monthKey] = { name: monthKey, revenue: 0, gp: 0, np: 0, cash: 0 };
      }
      
      const group = (rec.mis_group || rec.tally_group || '').toLowerCase();
      
      if (group.includes('sales') || group.includes('revenue') || group.includes('income')) {
        monthMap[monthKey].revenue += (rec.credit - rec.debit);
        totalRevenue += (rec.credit - rec.debit);
      } else if (group.includes('direct expense') || group.includes('cost of sales') || group.includes('cogs')) {
        monthMap[monthKey].gp -= (rec.debit - rec.credit);
      } else if (group.includes('expense') || group.includes('overhead')) {
        monthMap[monthKey].np -= (rec.debit - rec.credit);
        totalOverhead += (rec.debit - rec.credit);
        
        const cat = rec.mis_group || rec.tally_group || 'Overhead';
        overheadCategories[cat] = (overheadCategories[cat] || 0) + (rec.debit - rec.credit);
      }
    });

    // Calculate GP & NP net totals
    Object.keys(monthMap).forEach(k => {
      monthMap[k].gp = monthMap[k].revenue - Math.abs(monthMap[k].gp);
      monthMap[k].np = monthMap[k].gp - Math.abs(monthMap[k].np);
      monthMap[k].gpPct = monthMap[k].revenue > 0 ? Number(((monthMap[k].gp / monthMap[k].revenue) * 100).toFixed(1)) : 0;
      monthMap[k].npPct = monthMap[k].revenue > 0 ? Number(((monthMap[k].np / monthMap[k].revenue) * 100).toFixed(1)) : 0;
    });

    // Query BS Data for Cash & Bank balance
    const bsRecords = await BSData.find({ company: company._id });
    let cashBankTotal = 0;
    bsRecords.forEach(b => {
      const gName = (b.group_name || b.parent_group || '').toLowerCase();
      if (gName.includes('cash') || gName.includes('bank')) {
        cashBankTotal += b.closing_balance;
      }
    });

    const chartData = Object.values(monthMap);
    const overheadData = Object.keys(overheadCategories).map(cat => ({
      name: cat,
      value: Math.abs(overheadCategories[cat])
    }));

    totalGP = chartData.reduce((acc, curr) => acc + curr.gp, 0);
    totalNP = chartData.reduce((acc, curr) => acc + curr.np, 0);
    const overallGpPct = totalRevenue > 0 ? Number(((totalGP / totalRevenue) * 100).toFixed(1)) : 0;
    const overallNpPct = totalRevenue > 0 ? Number(((totalNP / totalRevenue) * 100).toFixed(1)) : 0;

    res.json({
      companyName: company.display_name || company.tally_name || tenant.name,
      dateRange: `Synced ${plRecords.length} records across ${chartData.length} period(s)`,
      stats: {
        totalRevenue,
        grossProfit: totalGP,
        netProfit: totalNP,
        cashBank: cashBankTotal,
        overhead: totalOverhead,
        gpPct: overallGpPct,
        npPct: overallNpPct
      },
      chartData,
      overheadData
    });
  } catch (error) {
    console.error('Error fetching tenant dashboard financial data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
