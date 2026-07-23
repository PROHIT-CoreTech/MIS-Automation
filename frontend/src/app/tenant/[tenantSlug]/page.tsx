'use client';

import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Line, ComposedChart, Area, AreaChart, PieChart, Pie, Cell, LineChart
} from 'recharts';
import { 
  Building2, TrendingUp, TrendingDown, DollarSign, Wallet, FileBarChart, PieChart as PieChartIcon, Target, Lightbulb, 
  RotateCcw, Download, CreditCard, LogOut, Settings, RefreshCw, Calendar, ChevronDown
} from 'lucide-react';
import Link from 'next/link';
import { use, useState, useEffect } from 'react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6', '#14b8a6', '#f43f5e'];

export default function TenantDashboard({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;
  
  const [mounted, setMounted] = useState(false);
  const [dashboardData, setDashboardData] = useState<{
    companyName: string;
    dateRange: string;
    stats: { totalRevenue: number; grossProfit: number; netProfit: number; cashBank: number; overhead: number; gpPct: number; npPct: number };
    chartData: any[];
    overheadData: any[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [authUser, setAuthUser] = useState<{ username: string; full_name: string; role: string } | null>(null);
  const [tenantFeatures, setTenantFeatures] = useState<string[]>([]);

  // Filter States (matching Python sidebar)
  const [selectedCompany, setSelectedCompany] = useState<string>('Unique Steel Products');
  const [quickSelect, setQuickSelect] = useState<string>('12 Months');
  const [fromMonth, setFromMonth] = useState<string>('Aug-25');
  const [toMonth, setToMonth] = useState<string>('Jul-26');

  useEffect(() => {
    setMounted(true);
    // Load user from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        setAuthUser(JSON.parse(userStr));
      } catch (e) {
        console.warn('Could not parse user from localStorage');
      }
    }
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`http://localhost:5001/api/financial/dashboard/${tenantSlug}`);
        if (res.ok) {
          const json = await res.json();
          setDashboardData(json);
        }
      } catch (err) {
        console.error('Error fetching tenant financial data from MongoDB:', err);
      } finally {
        setIsLoading(false);
      }
    };
    // Fetch tenant features to gate nav items
    const fetchTenantInfo = async () => {
      try {
        const res = await fetch(`http://localhost:5001/api/financial/tenant-info/${tenantSlug}`);
        if (res.ok) {
          const info = await res.json();
          setTenantFeatures(Array.isArray(info.features) ? info.features : []);
        }
      } catch (err) {
        console.error('Error fetching tenant info:', err);
      }
    };
    if (tenantSlug) {
      fetchDashboard();
      fetchTenantInfo();
    }
  }, [tenantSlug]);

  const companyName = dashboardData?.companyName || selectedCompany || (tenantSlug ? tenantSlug.replace(/_/g, ' ').toUpperCase() : "Unique Steel Products");
  const dateRangeStr = dashboardData?.dateRange || `${fromMonth} ➔ ${toMonth} | 12 months`;
  const stats = dashboardData?.stats || { 
    totalRevenue: 632100000, 
    grossProfit: 624800000, 
    netProfit: 580200000, 
    cashBank: 51600000, 
    overhead: 61700000, 
    gpPct: 98.8, 
    npPct: 91.8 
  };
  const chartData = dashboardData?.chartData?.length ? dashboardData.chartData : [
    { name: 'Aug-25', revenue: 45000000, gp: 44000000, np: 42000000, cash: 12000000, gpPct: 97.7, npPct: 93.3 },
    { name: 'Sep-25', revenue: 51000000, gp: 50000000, np: 48000000, cash: 98000000, gpPct: 98.0, npPct: 94.1 },
    { name: 'Oct-25', revenue: 68000000, gp: 67000000, np: 60000000, cash: 18000000, gpPct: 98.5, npPct: 88.2 },
    { name: 'Nov-25', revenue: 62000000, gp: 61000000, np: 58000000, cash: 21000000, gpPct: 98.3, npPct: 93.5 },
    { name: 'Dec-25', revenue: 59000000, gp: 58000000, np: 55000000, cash: 24000000, gpPct: 98.3, npPct: 93.2 },
    { name: 'Jan-26', revenue: 92000000, gp: 91000000, np: 87000000, cash: 49000000, gpPct: 98.9, npPct: 94.5 },
    { name: 'Feb-26', revenue: 71000000, gp: 70000000, np: 65000000, cash: 48000000, gpPct: 98.5, npPct: 91.5 },
    { name: 'Mar-26', revenue: 38000000, gp: 37000000, np: 35000000, cash: 49000000, gpPct: 97.3, npPct: 92.1 },
    { name: 'Apr-26', revenue: 2000000, gp: 1900000, np: 0, cash: 49500000, gpPct: 95.0, npPct: 0.0 },
    { name: 'May-26', revenue: 2000000, gp: 1900000, np: 1800000, cash: 49800000, gpPct: 95.0, npPct: 90.0 },
    { name: 'Jun-26', revenue: 2000000, gp: 1900000, np: 1800000, cash: 50000000, gpPct: 95.0, npPct: 90.0 },
    { name: 'Jul-26', revenue: 2000000, gp: 1900000, np: 1800000, cash: 50200000, gpPct: 95.0, npPct: 90.0 }
  ];

  const overheadData = dashboardData?.overheadData?.length ? dashboardData.overheadData : [
    { name: 'Admin Expenses', value: 1746110 },
    { name: 'Direct Expenses', value: 3319460 },
    { name: 'Interest/Fees/Penalty Paid', value: 40105 },
    { name: 'Finance Cost', value: 7220 },
    { name: 'Employee Benefits', value: 399818 },
    { name: 'Partner Remuneration', value: 962520 },
    { name: 'Petrol and Travelling Expenses', value: 7000 }
  ];

  // Formatting helpers matching Python (Cr / L)
  const formatCurrency = (val: number) => {
    if (!val && val !== 0) return '₹0 Cr';
    const absVal = Math.abs(val);
    if (absVal >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Cr`;
    } else if (absVal >= 100000) {
      return `₹${(val / 100000).toFixed(2)} L`;
    }
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const handleResetFilters = () => {
    setQuickSelect('12 Months');
    setFromMonth('Aug-25');
    setToMonth('Jul-26');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-[#070913] text-slate-200 font-sans selection:bg-indigo-500/30 flex">
      
      {/* ---------------- SIDEBAR (Matches Python Navigation & Date Filter) ---------------- */}
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

              {/* Settings gear — only visible to tenant admins */}
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
            {/* Dashboard — always visible */}
            <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all">
              📈 Dashboard
            </Link>
            {/* MIS Reports */}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('reports')) && (
              <Link href={`/tenant/${tenantSlug}/reports`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                📄 MIS Reports
              </Link>
            )}
            {/* Cash Flow */}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('cash_flow')) && (
              <Link href={`/tenant/${tenantSlug}/cash-flow`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                💵 Cash Flow
              </Link>
            )}
            {/* Downloads */}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('downloads')) && (
              <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                📥 Downloads
              </Link>
            )}
            {/* Sync Status */}
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
              📊 Management Dashboard
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

        {/* 5 Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          {/* Revenue */}
          <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10 shadow-sm hover:border-white/20 transition-all">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              📈 Revenue
            </p>
            <h3 className="text-2xl font-black text-slate-100">{formatCurrency(stats.totalRevenue)}</h3>
          </div>

          {/* Gross Profit */}
          <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10 shadow-sm hover:border-white/20 transition-all">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              🛒 Gross Profit
            </p>
            <h3 className="text-2xl font-black text-slate-100">{formatCurrency(stats.grossProfit)}</h3>
            <p className="text-xs text-emerald-400 font-bold mt-1">{stats.gpPct}%</p>
          </div>

          {/* Net Profit */}
          <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10 shadow-sm hover:border-white/20 transition-all">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              💰 Net Profit
            </p>
            <h3 className="text-2xl font-black text-slate-100">{formatCurrency(stats.netProfit)}</h3>
            <p className="text-xs text-emerald-400 font-bold mt-1">{stats.npPct}%</p>
          </div>

          {/* Cash & Bank */}
          <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10 shadow-sm hover:border-white/20 transition-all">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              🏦 Cash & Bank
            </p>
            <h3 className="text-2xl font-black text-slate-100">{formatCurrency(stats.cashBank)}</h3>
          </div>

          {/* Overhead */}
          <div className="bg-[#0f1629] p-5 rounded-2xl border border-white/10 shadow-sm hover:border-white/20 transition-all">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              💸 Overhead
            </p>
            <h3 className="text-2xl font-black text-slate-100">{formatCurrency(stats.overhead)}</h3>
          </div>
        </div>

        {/* Middle Charts Row (Revenue vs Profit Trend & Overhead Breakdown) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Revenue vs Profit Trend */}
          <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
              📈 Revenue vs Profit Trend
            </h3>
            <div className="h-72 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(value) => `${(value/1000000).toFixed(0)}M`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f1f5f9' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar dataKey="revenue" name="Revenue" fill="#4f46e5" radius={[4, 4, 0, 0]} maxBarSize={30} />
                    <Line type="monotone" dataKey="gp" name="Gross Profit" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="np" name="Net Profit" stroke="#38bdf8" strokeDasharray="4 4" strokeWidth={2.5} dot={{ r: 3 }} />
                  </ComposedChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>

          {/* Overhead Breakdown Donut Chart */}
          <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
              💸 Overhead Breakdown
            </h3>
            <div className="h-72 w-full flex items-center justify-center relative">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={overheadData}
                      cx="40%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                      stroke="none"
                    >
                      {overheadData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f1f5f9' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend verticalAlign="middle" align="right" layout="vertical" wrapperStyle={{ fontSize: '11px', paddingLeft: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : null}
              {/* Donut Center Total Label */}
              <div className="absolute left-[40%] top-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
                <p className="text-xs text-slate-400 font-medium">Total</p>
                <p className="text-sm font-black text-slate-100">{formatCurrency(stats.overhead)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Charts Row (Cash & Bank Trend & GP% vs NP% Trend) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Cash & Bank Trend */}
          <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
              🏦 Cash & Bank Trend
            </h3>
            <div className="h-64 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(value) => `${(value/1000000).toFixed(0)}M`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f1f5f9' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Area type="monotone" dataKey="cash" stroke="#38bdf8" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCash)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>

          {/* GP% vs NP% Trend */}
          <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
              📊 GP% vs NP% Trend
            </h3>
            <div className="h-64 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f1f5f9' }}
                      formatter={(value: number) => `${value}%`}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                    <Line type="monotone" dataKey="gpPct" name="GP%" stroke="#a855f7" strokeWidth={2.5} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="npPct" name="NP%" stroke="#818cf8" strokeDasharray="4 4" strokeWidth={2.5} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
