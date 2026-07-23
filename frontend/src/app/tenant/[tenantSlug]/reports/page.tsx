'use client';

import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Line, ComposedChart, LineChart, Cell, LabelList
} from 'recharts';
import { 
  Building2, TrendingUp, FileBarChart, PieChart as PieChartIcon, Search, Download, 
  RotateCcw, RefreshCw, ChevronDown, Table, Users, AlertTriangle, CheckCircle2, Settings
} from 'lucide-react';
import Link from 'next/link';
import React, { use, useState, useEffect } from 'react';

const BUCKET_COLORS: { [key: string]: string } = {
  '0-30 Days': '#10b981',
  '31-60 Days': '#00b4d8',
  '61-90 Days': '#ffb703',
  '91-180 Days': '#ff758f',
  '181-365 Days': '#b5179e',
  '1 Year+': '#ef4444'
};

export default function ReportsPage({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [mounted, setMounted] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState<'chart' | 'table' | 'customer' | 'vendor'>('chart');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter States
  const [selectedCompany, setSelectedCompany] = useState<string>('Unique Steel Products');
  const [quickSelect, setQuickSelect] = useState<string>('12 Months');
  const [fromMonth, setFromMonth] = useState<string>('Aug-25');
  const [toMonth, setToMonth] = useState<string>('Jul-26');

  // Dynamic Data from Backend API
  const [reportsData, setReportsData] = useState<{
    companyName: string;
    dateRange: string;
    months: string[];
    chartData: any[];
    plRecords: any[];
    detailedGroups: any;
    customerSummary: any;
    customerAgeing: any[];
    vendorSummary: any;
    vendorAgeing: any[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tenantFeatures, setTenantFeatures] = useState<string[]>([]);
  const [authUser, setAuthUser] = useState<{ username: string; full_name: string; role: string } | null>(null);

  useEffect(() => {
    setMounted(true);
    const userStr = localStorage.getItem('user');
    if (userStr) { try { setAuthUser(JSON.parse(userStr)); } catch (e) {} }
    const fetchReportsData = async () => {
      try {
        const res = await fetch(`http://localhost:5001/api/financial/reports/${tenantSlug}`);
        if (res.ok) {
          const json = await res.json();
          setReportsData(json);
        }
      } catch (err) {
        console.error('Error fetching MIS reports data from backend:', err);
      } finally {
        setIsLoading(false);
      }
    };
    if (tenantSlug) {
      fetchReportsData();
      // Fetch tenant features for feature-gated nav
      fetch(`http://localhost:5001/api/financial/tenant-info/${tenantSlug}`)
        .then(r => r.ok ? r.json() : null)
        .then(info => { if (info?.features) setTenantFeatures(Array.isArray(info.features) ? info.features : []); })
        .catch(() => {});
    }
  }, [tenantSlug]);

  const companyName = reportsData?.companyName || selectedCompany || (tenantSlug ? tenantSlug.replace(/_/g, ' ').toUpperCase() : "Unique Steel Products");

  const defaultMonths = ['Aug-25', 'Sep-25', 'Oct-25', 'Nov-25', 'Dec-25', 'Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26', 'Jul-26'];
  const months = reportsData?.months?.length ? reportsData.months : defaultMonths;

  // Formatting helpers matching Python (Cr / L / —)
  const formatCellVal = (val: number) => {
    if (!val || val === 0) return '—';
    const absVal = Math.abs(val);
    if (absVal >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (absVal >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const formatCurrency = (val: number) => {
    if (!val && val !== 0) return '₹0 Cr';
    const absVal = Math.abs(val);
    if (absVal >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (absVal >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const handleResetFilters = () => {
    setQuickSelect('12 Months');
    setFromMonth('Aug-25');
    setToMonth('Jul-26');
  };

  // Fallback Data Matching Python Screenshots
  const chartData = reportsData?.chartData?.length ? reportsData.chartData : [
    { name: 'Aug-25', revenue: 45000000, gp: 44000000, np: 42000000, cogs: 3000000, overhead: 4200000, gpPct: 96.4, npPct: 93.7 },
    { name: 'Sep-25', revenue: 51000000, gp: 50000000, np: 48000000, cogs: 4800000, overhead: 4600000, gpPct: 99.8, npPct: 97.0 },
    { name: 'Oct-25', revenue: 68000000, gp: 67000000, np: 60000000, cogs: 4400000, overhead: 7400000, gpPct: 91.2, npPct: 82.0 },
    { name: 'Nov-25', revenue: 62000000, gp: 61000000, np: 58000000, cogs: 5200000, overhead: 7300000, gpPct: 100.4, npPct: 91.0 },
    { name: 'Dec-25', revenue: 59000000, gp: 58000000, np: 55000000, cogs: 3200000, overhead: 5300000, gpPct: 102.4, npPct: 95.5 },
    { name: 'Jan-26', revenue: 92000000, gp: 91000000, np: 87000000, cogs: 4800000, overhead: 7100000, gpPct: 101.0, npPct: 94.6 },
    { name: 'Feb-26', revenue: 71000000, gp: 70000000, np: 65000000, cogs: 6100000, overhead: 20500000, gpPct: 96.0, npPct: 95.4 },
    { name: 'Mar-26', revenue: 38000000, gp: 37000000, np: 35000000, cogs: 1400000, overhead: 4500000, gpPct: 102.4, npPct: 87.2 },
    { name: 'Apr-26', revenue: 2000000, gp: 1900000, np: 0, cogs: 500000, overhead: 400000, gpPct: 95.5, npPct: 94.7 },
    { name: 'May-26', revenue: 2000000, gp: 1900000, np: 1800000, cogs: 300000, overhead: 200000, gpPct: 98.9, npPct: 98.2 },
    { name: 'Jun-26', revenue: 2000000, gp: 1900000, np: 1800000, cogs: 200000, overhead: 100000, gpPct: 0.0, npPct: 0.0 },
    { name: 'Jul-26', revenue: 2000000, gp: 1900000, np: 1800000, cogs: 200000, overhead: 100000, gpPct: 100.0, npPct: 100.0 }
  ];

  // Customer Summary & Ageing Data (Python Screenshot 2)
  const custSummary = reportsData?.customerSummary || {
    totalOutstanding: 244600000,
    current: 0,
    overdue: 244600000,
    partiesCount: 212,
    buckets: [
      { bucket: '31-60 Days', amount: 847000 },
      { bucket: '61-90 Days', amount: 59200000 },
      { bucket: '91-180 Days', amount: 150600000 },
      { bucket: '181-365 Days', amount: 23600000 },
      { bucket: '1 Year+', amount: 268500 }
    ]
  };

  const customerAgeingParties = reportsData?.customerAgeing?.length ? reportsData.customerAgeing : [
    { partyName: '10 Cut of Cheese', b0_30: 0, b31_60: 0, b61_90: 0, b91_180: 35400000, b181_365: 0, b1year: 0, total: 35400000 },
    { partyName: 'Indian Customs Duty Tax', b0_30: 0, b31_60: 0, b61_90: 0, b91_180: 15400000, b181_365: 11100000, b1year: 137300, total: 27900000 },
    { partyName: 'Western Refrigeration Pvt Ltd - S/Crs.', b0_30: 0, b31_60: 0, b61_90: 1931000, b91_180: 25100000, b181_365: 0, b1year: 0, total: 27000000 },
    { partyName: 'Mukunda Foods Private Limited - Crs.', b0_30: 0, b31_60: 0, b61_90: 7145000, b91_180: 12200000, b181_365: 1988000, b1year: 0, total: 21300000 },
    { partyName: 'Absolute RG Equipments Private Limited', b0_30: 0, b31_60: 0, b61_90: 3451000, b91_180: 8768000, b181_365: 1568000, b1year: 0, total: 13800000 }
  ];

  // Vendor Summary & Ageing Data (Python Screenshot 3)
  const vendSummary = reportsData?.vendorSummary || {
    totalOutstanding: 312100000,
    current: 213000,
    overdue: 311900000,
    partiesCount: 313,
    buckets: [
      { bucket: '0-30 Days', amount: 213000 },
      { bucket: '31-60 Days', amount: 78700000 },
      { bucket: '61-90 Days', amount: 74300000 },
      { bucket: '91-180 Days', amount: 119900000 },
      { bucket: '181-365 Days', amount: 32700000 },
      { bucket: '1 Year+', amount: 633900 }
    ]
  };

  const vendorAgeingParties = reportsData?.vendorAgeing?.length ? reportsData.vendorAgeing : [
    { partyName: 'Sushant Purchase', b0_30: 0, b31_60: 75000000, b61_90: 0, b91_180: 0, b181_365: 0, b1year: 0, total: 75000000 },
    { partyName: 'Western Refrigeration Pvt Ltd - S/Crs.', b0_30: 0, b31_60: 0, b61_90: 0, b91_180: 25800000, b181_365: 0, b1year: 0, total: 25800000 },
    { partyName: 'Mukunda Foods Private Limited - Crs.', b0_30: 0, b31_60: 0, b61_90: 5274000, b91_180: 12100000, b181_365: 1988000, b1year: 0, total: 19400000 }
  ];

  // Detailed Table Mock Fallback (Python Screenshot 1)
  const detailedSections = [
    {
      title: '📈 SALES ACCOUNTS (Revenue)',
      rows: [
        { ledger: 'EXPORT SALES', months: { 'Sep-25': 258000, 'Nov-25': 738000, 'Dec-25': 226000, 'Mar-26': 30000000 } },
        { ledger: 'GST SALES', months: { 'Aug-25': 28500000, 'Sep-25': 27600000, 'Oct-25': 32700000, 'Nov-25': 49700000, 'Dec-25': 48300000, 'Jan-26': 36300000, 'Feb-26': 35500000, 'Mar-26': 67100000, 'Apr-26': 37200000, 'May-26': 18800000 } },
        { ledger: 'Goods Sold As Free of Cost', months: { 'Mar-26': 36540 } },
        { ledger: 'IGST SALES', months: { 'Aug-25': 13500000, 'Sep-25': 21600000, 'Oct-25': 15400000, 'Nov-25': 21400000, 'Dec-25': 16200000, 'Jan-26': 21500000, 'Feb-26': 27700000, 'Mar-26': 26700000, 'Apr-26': 50300000, 'May-26': 696700 } },
        { ledger: 'Sales Bills to Make', months: { 'Aug-25': 1566000, 'Nov-25': 350000, 'Dec-25': 325000, 'Mar-26': 33240, 'Apr-26': 120000, 'May-26': 14200 } }
      ],
      subTotal: { 'Aug-25': 43600000, 'Sep-25': 49500000, 'Oct-25': 48100000, 'Nov-25': 72200000, 'Dec-25': 65000000, 'Jan-26': 57800000, 'Feb-26': 63200000, 'Mar-26': 123900000, 'Apr-26': 87600000, 'May-26': 25800000 }
    },
    {
      title: '➕ DIRECT INCOMES',
      rows: [
        { ledger: 'AMC Service Charges', months: { 'Nov-25': 76298, 'Jan-26': 543000, 'Apr-26': 551000 } },
        { ledger: 'Foundation Scheme Income', months: { 'Sep-25': 400000 } },
        { ledger: 'Installation Charges', months: { 'Aug-25': 31500, 'Sep-25': 4500, 'Oct-25': 16500, 'Nov-25': 4500, 'Dec-25': 31000, 'Jan-26': 7500, 'Feb-26': 42157, 'Mar-26': 260000, 'Apr-26': 3500 } },
        { ledger: 'Job Work Charges Received', months: { 'Aug-25': 1242000, 'Nov-25': 827000, 'Dec-25': 2157000, 'Jan-26': 841000, 'Feb-26': 3535000, 'Mar-26': 4345000 } }
      ],
      subTotal: { 'Aug-25': 1274000, 'Sep-25': 405000, 'Oct-25': 16500, 'Nov-25': 908000, 'Dec-25': 2188000, 'Jan-26': 1392000, 'Feb-26': 3577000, 'Mar-26': 4605000, 'Apr-26': 554000 }
    },
    {
      title: '📦 COST OF GOODS SOLD',
      subtitle: 'Add: Direct Expenses',
      rows: [
        { ledger: 'Customs Duty', months: { 'Nov-25': 34728, 'Feb-26': 2900000, 'Apr-26': 3906000 } },
        { ledger: 'Factory Maintenance', months: { 'Aug-25': 25262, 'Sep-25': 107000, 'Oct-25': 41584, 'Nov-25': 23529, 'Dec-25': 28925, 'Jan-26': 24850, 'Feb-26': 136000, 'Mar-26': 39581, 'Apr-26': 96283, 'May-26': 5913 } }
      ]
    }
  ];

  // Dynamically compute detailedSections from API response if present
  const dynamicSections = (reportsData?.detailedGroups && Object.keys(reportsData.detailedGroups).length > 0) ? Object.keys(reportsData.detailedGroups).map(sectionTitle => {
    const ledgersObj = reportsData.detailedGroups[sectionTitle] || {};
    const rows = Object.values(ledgersObj).map((lObj: any) => ({
      ledger: lObj.ledger_name,
      months: lObj.months || {}
    }));

    const subTotal: { [key: string]: number } = {};
    months.forEach(m => {
      let sum = 0;
      rows.forEach(r => {
        sum += (r.months[m] || 0);
      });
      subTotal[m] = sum;
    });

    return {
      title: sectionTitle,
      rows: rows.length > 0 ? rows : (detailedSections.find(s => s.title === sectionTitle)?.rows || []),
      subTotal
    };
  }) : detailedSections;

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-[#070913] text-slate-200 font-sans selection:bg-indigo-500/30 flex">
      
      {/* ---------------- SIDEBAR ---------------- */}
      <aside className="w-64 bg-[#0d1326] border-r border-white/10 p-4 flex flex-col justify-between shrink-0 min-h-screen">
        <div>
          {/* Brand Header */}
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <PieChartIcon className="w-5 h-5 text-indigo-400" />
              MIS Portal
            </h2>
            <button title="Refresh" onClick={() => window.location.reload()} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-white/10">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* User Badge with Settings Dropdown */}
          <div className="bg-[#151c33] border border-white/10 rounded-xl p-3 mb-6 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm border ${
                  authUser?.role === 'admin'
                    ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                }`}>
                  👤
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">{authUser?.full_name || authUser?.username || 'User'}</p>
                  <span className={`inline-block mt-0.5 px-2 py-0.5 text-[10px] font-bold rounded-md tracking-wider border ${
                    authUser?.role === 'admin'
                      ? 'text-indigo-300 bg-indigo-500/20 border-indigo-500/30'
                      : 'text-emerald-300 bg-emerald-500/20 border-emerald-500/30'
                  }`}>
                    {authUser?.role?.toUpperCase() || 'USER'}
                  </span>
                </div>
              </div>

              {/* Settings gear — only for admins */}
              {authUser?.role === 'admin' && (
                <div className="relative">
                  <button 
                    onClick={() => setShowSettings(!showSettings)}
                    className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-white/10 transition-colors"
                    title="Settings"
                  >
                    <Settings className="w-3.5 h-3.5 text-indigo-400" />
                  </button>

                  {showSettings && (
                    <div className="absolute right-0 top-9 w-48 bg-[#0f1629] border border-white/15 rounded-xl shadow-2xl p-1.5 z-50 space-y-1">
                      <Link 
                        href={`/tenant/${tenantSlug}/admin`} 
                        onClick={() => setShowSettings(false)}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-indigo-600/20 text-xs font-semibold text-slate-200 transition-colors"
                      >
                        ⚙️ Admin Panel
                      </Link>
                      <Link 
                        href={`/tenant/${tenantSlug}/subscription`} 
                        onClick={() => setShowSettings(false)}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-indigo-600/20 text-xs font-semibold text-slate-200 transition-colors"
                      >
                        💳 Subscription
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Navigation Links */}
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">Navigation</p>
          <nav className="space-y-1 mb-6">
            <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📈 Dashboard
            </Link>
            {(tenantFeatures.length === 0 || tenantFeatures.includes('reports')) && (
              <Link href={`/tenant/${tenantSlug}/reports`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all">
                📄 MIS Reports
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('cash_flow')) && (
              <Link href={`/tenant/${tenantSlug}/cash-flow`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                💵 Cash Flow
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('downloads')) && (
              <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                📥 Downloads
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('sync')) && (
              <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                🔄 Sync Status
              </Link>
            )}
          </nav>

          {/* Company Selector */}
          <div className="pt-4 border-t border-white/10 mb-4">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">🏢 Company</p>
            <div className="relative">
              <select 
                value={selectedCompany} 
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full bg-[#151c33] border border-white/10 rounded-xl px-3 py-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500 appearance-none cursor-pointer pr-8"
              >
                <option value="Unique Steel Products">Unique Steel Products</option>
                <option value="Demo Enterprise">Demo Enterprise</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
            </div>
          </div>

          {/* Date Range Filters */}
          <div className="pt-4 border-t border-white/10">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">📅 Date Range</p>
            <div className="space-y-3">
              <div>
                <label className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1 block">Quick Select</label>
                <select 
                  value={quickSelect} 
                  onChange={(e) => setQuickSelect(e.target.value)}
                  className="w-full bg-[#151c33] border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="12 Months">12 Months</option>
                  <option value="6 Months">6 Months</option>
                  <option value="YTD">YTD</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1 block">From</label>
                <select 
                  value={fromMonth} 
                  onChange={(e) => setFromMonth(e.target.value)}
                  className="w-full bg-[#151c33] border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Aug-25">Aug-25</option>
                  <option value="Sep-25">Sep-25</option>
                  <option value="Oct-25">Oct-25</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1 block">To</label>
                <select 
                  value={toMonth} 
                  onChange={(e) => setToMonth(e.target.value)}
                  className="w-full bg-[#151c33] border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Jul-26">Jul-26</option>
                  <option value="Jun-26">Jun-26</option>
                  <option value="May-26">May-26</option>
                </select>
              </div>

              <button 
                onClick={handleResetFilters}
                className="w-full mt-2 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Reset
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* ---------------- MAIN CONTENT AREA ---------------- */}
      <main className="flex-1 p-6 overflow-y-auto">
        
        {/* Top Header Row */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              📄 MIS Reports
            </h1>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <Building2 className="w-3.5 h-3.5 text-indigo-400" /> {companyName}
            </p>
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300">
              🗓️ {fromMonth} ➔ {toMonth} | 12 months
            </div>
          </div>

          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* Sub-Navigation Tabs (Chart View | Detailed Table | Customer Ageing | Vendor Ageing) */}
        <div className="flex border-b border-white/10 mb-6 gap-2">
          <button 
            onClick={() => setActiveTab('chart')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'chart' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            📊 Chart View
          </button>
          <button 
            onClick={() => setActiveTab('table')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'table' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            📋 Detailed Table
          </button>
          <button 
            onClick={() => setActiveTab('customer')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'customer' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            👤 Customer Ageing
          </button>
          <button 
            onClick={() => setActiveTab('vendor')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'vendor' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            🏢 Vendor Ageing
          </button>
        </div>

        {/* TAB 1: CHART VIEW */}
        {activeTab === 'chart' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Revenue vs GP vs NP */}
              <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
                <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                  📈 Revenue vs GP vs NP
                </h3>
                <div className="h-72 w-full">
                  {mounted ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatCurrency(val)} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                        <Bar dataKey="revenue" name="Revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={30} />
                        <Line type="monotone" dataKey="gp" name="Gross Profit" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} />
                        <Line type="monotone" dataKey="np" name="Net Profit" stroke="#a855f7" strokeDasharray="4 4" strokeWidth={2.5} dot={{ r: 3 }} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : null}
                </div>
              </div>

              {/* COGS vs Overhead Trend */}
              <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
                <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                  💸 COGS vs Overhead Trend
                </h3>
                <div className="h-72 w-full">
                  {mounted ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatCurrency(val)} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                        <Bar dataKey="cogs" name="COGS" fill="#f59e0b" radius={[4, 4, 0, 0]} maxBarSize={20} />
                        <Bar dataKey="overhead" name="Overhead" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={20} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Bottom Row: GP% and NP% Monthly Trend */}
            <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                📊 GP% and NP% Monthly Trend
              </h3>
              <div className="h-72 w-full">
                {mounted ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                      <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => `${val}%`} />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                      <Line type="monotone" dataKey="gpPct" name="GP%" stroke="#818cf8" strokeWidth={2.5} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="npPct" name="NP%" stroke="#c084fc" strokeDasharray="4 4" strokeWidth={2.5} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : null}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: DETAILED TABLE (P&L Detailed — Monthly Breakup - Python Screenshot 1) */}
        {activeTab === 'table' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-base font-extrabold text-slate-100 flex items-center gap-2">
                📋 P&L Detailed — Monthly Breakup
              </h3>
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-colors">
                <Download className="w-4 h-4" /> Export
              </button>
            </div>

            <div className="bg-[#0f1629] border border-white/10 rounded-2xl overflow-x-auto shadow-2xl">
              <table className="w-full text-left text-xs text-slate-300 border-collapse">
                <thead className="bg-[#151c33] text-slate-300 uppercase text-[11px] font-bold border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3 border-r border-white/10 min-w-[240px]">Particulars</th>
                    {months.map(m => (
                      <th key={m} className="px-3 py-3 border-r border-white/10 text-center min-w-[85px]">{m}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {dynamicSections.map((sec: any, sIdx: number) => (
                    <React.Fragment key={sIdx}>
                      {/* Section Banner Header */}
                      <tr className="bg-[#1e293b] font-extrabold text-slate-100">
                        <td colSpan={months.length + 1} className="px-4 py-2.5 text-xs text-indigo-300 tracking-wide border-y border-white/10">
                          {sec.title}
                        </td>
                      </tr>
                      {sec.subtitle && (
                        <tr className="bg-white/[0.02] font-bold text-slate-400">
                          <td colSpan={months.length + 1} className="px-6 py-2 text-[11px] text-slate-400 border-b border-white/5">
                            {sec.subtitle}
                          </td>
                        </tr>
                      )}
                      {/* Ledger Rows */}
                      {sec.rows.map((r, rIdx) => (
                        <tr key={rIdx} className="hover:bg-white/[0.02] transition-colors">
                          <td className="px-4 py-2.5 text-slate-300 font-medium border-r border-white/10 pl-6">{r.ledger}</td>
                          {months.map(m => (
                            <td key={m} className="px-3 py-2.5 text-center font-mono border-r border-white/10 text-slate-300">
                              {formatCellVal((r.months as any)[m] || 0)}
                            </td>
                          ))}
                        </tr>
                      ))}
                      {/* Sub-Total Row */}
                      {sec.subTotal && (
                        <tr className="bg-[#151c33]/80 font-black text-indigo-300 border-t border-b border-indigo-500/30">
                          <td className="px-4 py-2.5 border-r border-white/10 pl-6 text-indigo-300">Sub-Total</td>
                          {months.map(m => (
                            <td key={m} className="px-3 py-2.5 text-center font-mono border-r border-white/10 font-bold text-indigo-300">
                              {formatCellVal((sec.subTotal as any)[m] || 0)}
                            </td>
                          ))}
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: CUSTOMER AGEING (Python Screenshot 2) */}
        {activeTab === 'customer' && (
          <div className="space-y-6">
            {/* Top 4 KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  👤 Total Outstanding
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCurrency(custSummary.totalOutstanding)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  ✅ Current (0-30 Days)
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCellVal(custSummary.current)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  ⚠️ Overdue (31+ Days)
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCurrency(custSummary.overdue)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  👥 Parties
                </p>
                <h3 className="text-2xl font-black text-slate-100">{custSummary.partiesCount}</h3>
              </div>
            </div>

            {/* Bucket Bar Chart */}
            <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-200 mb-6">Amount (Cr)</h3>
              <div className="h-64 w-full">
                {mounted ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={custSummary.buckets} margin={{ top: 20, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="bucket" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                      <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/10000000).toFixed(0)}`} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatCurrency(val)} />
                      <Bar dataKey="amount" radius={[4, 4, 0, 0]} maxBarSize={90}>
                        {custSummary.buckets.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={BUCKET_COLORS[entry.bucket] || '#3b82f6'} />
                        ))}
                        <LabelList dataKey="amount" position="top" formatter={(val: number) => formatCellVal(val)} style={{ fill: '#f1f5f9', fontSize: '11px', fontWeight: 'bold' }} />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : null}
              </div>
            </div>

            {/* Bottom Table: Party-wise Breakup */}
            <div className="bg-[#0f1629] border border-white/10 rounded-2xl overflow-hidden shadow-xl">
              <div className="p-4 border-b border-white/10 font-bold text-sm text-slate-100 flex items-center gap-2">
                👤 Customer Ageing — Party-wise Breakup
              </div>
              <table className="w-full text-left text-xs text-slate-300 border-collapse">
                <thead className="bg-[#151c33] text-slate-400 uppercase text-[10px] font-bold border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3">Party Name</th>
                    <th className="px-3 py-3 text-center">0-30 Days</th>
                    <th className="px-3 py-3 text-center">31-60 Days</th>
                    <th className="px-3 py-3 text-center">61-90 Days</th>
                    <th className="px-3 py-3 text-center">91-180 Days</th>
                    <th className="px-3 py-3 text-center">181-365 Days</th>
                    <th className="px-3 py-3 text-center">1 Year+</th>
                    <th className="px-4 py-3 text-right font-bold">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono">
                  {customerAgeingParties.map((p, idx) => (
                    <tr key={idx} className="hover:bg-white/[0.02] transition-colors font-sans">
                      <td className="px-4 py-3 font-semibold text-slate-200">{p.partyName}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b0_30)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b31_60)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b61_90)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b91_180)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b181_365)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b1year)}</td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-slate-100">{formatCurrency(p.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: VENDOR AGEING (Python Screenshot 3) */}
        {activeTab === 'vendor' && (
          <div className="space-y-6">
            {/* Top 4 KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  🏢 Total Outstanding
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCurrency(vendSummary.totalOutstanding)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  ✅ Current (0-30 Days)
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCellVal(vendSummary.current)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  ⚠️ Overdue (31+ Days)
                </p>
                <h3 className="text-2xl font-black text-slate-100">{formatCurrency(vendSummary.overdue)}</h3>
              </div>
              <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  👥 Parties
                </p>
                <h3 className="text-2xl font-black text-slate-100">{vendSummary.partiesCount}</h3>
              </div>
            </div>

            {/* Bucket Bar Chart */}
            <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-200 mb-6">Amount (Cr)</h3>
              <div className="h-64 w-full">
                {mounted ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={vendSummary.buckets} margin={{ top: 20, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="bucket" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                      <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/10000000).toFixed(0)}`} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatCurrency(val)} />
                      <Bar dataKey="amount" radius={[4, 4, 0, 0]} maxBarSize={90}>
                        {vendSummary.buckets.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={BUCKET_COLORS[entry.bucket] || '#3b82f6'} />
                        ))}
                        <LabelList dataKey="amount" position="top" formatter={(val: number) => formatCellVal(val)} style={{ fill: '#f1f5f9', fontSize: '11px', fontWeight: 'bold' }} />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : null}
              </div>
            </div>

            {/* Bottom Table: Party-wise Breakup */}
            <div className="bg-[#0f1629] border border-white/10 rounded-2xl overflow-hidden shadow-xl">
              <div className="p-4 border-b border-white/10 font-bold text-sm text-slate-100 flex items-center gap-2">
                🏢 Vendor Ageing — Party-wise Breakup
              </div>
              <table className="w-full text-left text-xs text-slate-300 border-collapse">
                <thead className="bg-[#151c33] text-slate-400 uppercase text-[10px] font-bold border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3">Party Name</th>
                    <th className="px-3 py-3 text-center">0-30 Days</th>
                    <th className="px-3 py-3 text-center">31-60 Days</th>
                    <th className="px-3 py-3 text-center">61-90 Days</th>
                    <th className="px-3 py-3 text-center">91-180 Days</th>
                    <th className="px-3 py-3 text-center">181-365 Days</th>
                    <th className="px-3 py-3 text-center">1 Year+</th>
                    <th className="px-4 py-3 text-right font-bold">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono">
                  {vendorAgeingParties.map((p, idx) => (
                    <tr key={idx} className="hover:bg-white/[0.02] transition-colors font-sans">
                      <td className="px-4 py-3 font-semibold text-slate-200">{p.partyName}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b0_30)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b31_60)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b61_90)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b91_180)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b181_365)}</td>
                      <td className="px-3 py-3 text-center font-mono">{formatCellVal(p.b1year)}</td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-slate-100">{formatCurrency(p.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
