'use client';

import React, { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  PieChart as PieChartIcon, Building2, Download, RotateCcw, RefreshCw, ChevronDown, 
  Wallet, ArrowUpRight, ArrowDownRight, TrendingUp, AlertTriangle, CheckCircle2, Settings
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, 
  Line, AreaChart, Area, ComposedChart, Cell
} from 'recharts';

export default function CashFlowPage({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [mounted, setMounted] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState<'chart' | 'statement'>('chart');
  
  // Filter States
  const [selectedCompany, setSelectedCompany] = useState<string>('Unique Steel Products');
  const [quickSelect, setQuickSelect] = useState<string>('12 Months');
  const [fromMonth, setFromMonth] = useState<string>('Aug-25');
  const [toMonth, setToMonth] = useState<string>('Jul-26');

  // Backend Data
  const [cfData, setCfData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    const fetchCashFlowData = async () => {
      try {
        const res = await fetch(`http://localhost:5001/api/financial/cash-flow/${tenantSlug}`);
        if (res.ok) {
          const json = await res.json();
          setCfData(json);
        }
      } catch (err) {
        console.error('Error fetching cash flow data from backend:', err);
      } finally {
        setIsLoading(false);
      }
    };
    if (tenantSlug) {
      fetchCashFlowData();
    }
  }, [tenantSlug]);

  const companyName = cfData?.companyName || selectedCompany || "Unique Steel Products";

  // Formatting helpers matching Python (Cr / L / —)
  const formatINR = (val: number) => {
    if (val === 0 || !val) return '—';
    const absVal = Math.abs(val);
    const prefix = val < 0 ? '-' : '';
    if (absVal >= 10000000) return `${prefix}₹${(absVal / 10000000).toFixed(2)}Cr`;
    if (absVal >= 100000) return `${prefix}₹${(absVal / 100000).toFixed(2)}L`;
    return `${prefix}₹${absVal.toLocaleString('en-IN')}`;
  };

  const handleResetFilters = () => {
    setQuickSelect('12 Months');
    setFromMonth('Aug-25');
    setToMonth('Jul-26');
  };

  // Python Screenshot 1:1 Fallback Data
  const months = ['Aug-25', 'Sep-25', 'Oct-25', 'Nov-25', 'Dec-25', 'Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26', 'Jul-26'];

  const chartData = cfData?.chartData?.length ? cfData.chartData : [
    { name: 'Aug-25', cfo: 24000000, cfi: -6000000, cff: -34000000, actualClosing: 7800000, computedClosing: -2500000 },
    { name: 'Sep-25', cfo: 26000000, cfi: -5000000, cff: -41000000, actualClosing: 6500000, computedClosing: -1200000 },
    { name: 'Oct-25', cfo: 25000000, cfi: -4000000, cff: -36000000, actualClosing: 3200000, computedClosing: 1800000 },
    { name: 'Nov-25', cfo: 62000000, cfi: -3000000, cff: -68000000, actualClosing: 11200000, computedClosing: 2100000 },
    { name: 'Dec-25', cfo: 38000000, cfi: -2000000, cff: -55000000, actualClosing: 12100000, computedClosing: -2400000 },
    { name: 'Jan-26', cfo: 37000000, cfi: -2000000, cff: -48000000, actualClosing: 12800000, computedClosing: 3800000 },
    { name: 'Feb-26', cfo: 35000000, cfi: -1000000, cff: -63000000, actualClosing: 13900000, computedClosing: -3100000 },
    { name: 'Mar-26', cfo: 72000000, cfi: -2000000, cff: -94000000, actualClosing: 48500000, computedClosing: -3200000 },
    { name: 'Apr-26', cfo: 64000000, cfi: -1000000, cff: -82000000, actualClosing: 46200000, computedClosing: 34500000 },
    { name: 'May-26', cfo: 24000000, cfi: 0, cff: -33000000, actualClosing: 50800000, computedClosing: 44200000 },
    { name: 'Jun-26', cfo: 500000, cfi: 0, cff: 0, actualClosing: 51200000, computedClosing: 50800000 },
    { name: 'Jul-26', cfo: 500000, cfi: 0, cff: 0, actualClosing: 51600000, computedClosing: 51600000 }
  ];

  // Cash Bridge Waterfall Bar Data for Jul-26
  const cashBridgeData = [
    { name: 'Opening Cash', val: 50800000, fill: '#00b4d8' },
    { name: 'EBITDA', val: 42000000, fill: '#10b981' },
    { name: 'Working Capital', val: -41500000, fill: '#ef4444' },
    { name: 'CFO', val: 500000, fill: '#6366f1' },
    { name: 'CFI', val: 0, fill: '#f59e0b' },
    { name: 'CFF', val: 0, fill: '#8b5cf6' },
    { name: 'Closing Cash (computed)', val: 51600000, fill: '#00b4d8' }
  ];

  // Detailed Statement Rows (Matching Python Table)
  const statementSections = [
    {
      title: 'I. CASH FLOW FROM OPERATING ACTIVITY (CFO)',
      isHeader: true,
      rows: [
        { label: 'Net Profit (as per P&L)', vals: { 'Aug-25': 42000000, 'Sep-25': 48000000, 'Oct-25': 60000000, 'Nov-25': 58000000, 'Dec-25': 55000000, 'Jan-26': 87000000, 'Feb-26': 65000000, 'Mar-26': 35000000, 'Apr-26': 0, 'May-26': 1800000, 'Jun-26': 1800000, 'Jul-26': 1800000 } },
        { label: 'Add: Depreciation', vals: { 'Aug-25': 1200000, 'Sep-25': 1200000, 'Oct-25': 1200000, 'Nov-25': 1200000, 'Dec-25': 1200000, 'Jan-26': 1200000, 'Feb-26': 1200000, 'Mar-26': 1200000 } },
        { label: 'Add/(Less): Interest Paid / (Received)', vals: { 'Aug-25': 350000, 'Sep-25': 420000, 'Oct-25': 380000, 'Nov-25': 510000 } },
        { label: '= EBITDA / Operating Profit before Working Capital Changes', isSubtotal: true, vals: { 'Aug-25': 43550000, 'Sep-25': 49620000, 'Oct-25': 61580000, 'Nov-25': 59710000, 'Dec-25': 56200000, 'Jan-26': 88200000, 'Feb-26': 66200000, 'Mar-26': 36200000 } }
      ]
    },
    {
      title: 'Working Capital Changes',
      rows: [
        { label: '(Increase)/Decrease in Debtors', vals: { 'Aug-25': -12500000, 'Sep-25': -8200000, 'Oct-25': 15400000, 'Nov-25': 4200000 } },
        { label: '(Increase)/Decrease in Stock', vals: { 'Aug-25': -3200000, 'Sep-25': -1500000, 'Oct-25': -2100000, 'Nov-25': 1800000 } },
        { label: 'Increase/(Decrease) in Creditors', vals: { 'Aug-25': 8400000, 'Sep-25': 12100000, 'Oct-25': -4500000, 'Nov-25': 6200000 } },
        { label: '= CASH FLOW FROM OPERATING ACTIVITY', isCfo: true, vals: { 'Aug-25': 24000000, 'Sep-25': 26000000, 'Oct-25': 25000000, 'Nov-25': 62000000, 'Dec-25': 38000000, 'Jan-26': 37000000, 'Feb-26': 35000000, 'Mar-26': 72000000, 'Apr-26': 64000000, 'May-26': 24000000, 'Jun-26': 500000, 'Jul-26': 500000 } }
      ]
    },
    {
      title: 'II. CASH FLOW FROM INVESTING ACTIVITY (CFI)',
      isHeader: true,
      rows: [
        { label: '(Increase)/Decrease in Fixed Assets', vals: { 'Aug-25': -6000000, 'Sep-25': -5000000, 'Oct-25': -4000000, 'Nov-25': -3000000, 'Dec-25': -2000000, 'Jan-26': -2000000, 'Feb-26': -1000000, 'Mar-26': -2000000, 'Apr-26': -1000000 } },
        { label: '= CASH FLOW FROM INVESTING ACTIVITY', isCfi: true, vals: { 'Aug-25': -6000000, 'Sep-25': -5000000, 'Oct-25': -4000000, 'Nov-25': -3000000, 'Dec-25': -2000000, 'Jan-26': -2000000, 'Feb-26': -1000000, 'Mar-26': -2000000, 'Apr-26': -1000000, 'May-26': 0, 'Jun-26': 0, 'Jul-26': 0 } }
      ]
    },
    {
      title: 'III. CASH FLOW FROM FINANCING ACTIVITY (CFF)',
      isHeader: true,
      rows: [
        { label: 'Increase/(Decrease) in Loans', vals: { 'Aug-25': -34000000, 'Sep-25': -41000000, 'Oct-25': -36000000, 'Nov-25': -68000000, 'Dec-25': -55000000, 'Jan-26': -48000000, 'Feb-26': -63000000, 'Mar-26': -94000000, 'Apr-26': -82000000, 'May-26': -33000000 } },
        { label: '= CASH FLOW FROM FINANCING ACTIVITY', isCff: true, vals: { 'Aug-25': -34000000, 'Sep-25': -41000000, 'Oct-25': -36000000, 'Nov-25': -68000000, 'Dec-25': -55000000, 'Jan-26': -48000000, 'Feb-26': -63000000, 'Mar-26': -94000000, 'Apr-26': -82000000, 'May-26': -33000000, 'Jun-26': 0, 'Jul-26': 0 } }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-[#070913] text-slate-200 font-sans flex">
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#0d1326] border-r border-white/10 p-4 flex flex-col justify-between shrink-0 min-h-screen">
        <div>
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <PieChartIcon className="w-5 h-5 text-indigo-400" />
              MIS Portal
            </h2>
            <button title="Refresh" onClick={() => window.location.reload()} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 border border-white/10">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* User Badge with Settings Dropdown */}
          <div className="bg-[#151c33] border border-white/10 rounded-xl p-3 mb-6 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm border border-indigo-500/30">
                  👤
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">Rohit Barge</p>
                  <span className="inline-block mt-0.5 px-2 py-0.5 text-[10px] font-bold text-indigo-300 bg-indigo-500/20 border border-indigo-500/30 rounded-md tracking-wider">
                    ADMIN
                  </span>
                </div>
              </div>

              {/* Settings Dropdown Toggle */}
              <div className="relative">
                <button 
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-white/10 transition-colors"
                  title="Settings"
                >
                  <Settings className="w-3.5 h-3.5 text-indigo-400" />
                </button>

                {showSettings && (
                  <div className="absolute right-0 top-9 w-44 bg-[#0f1629] border border-white/15 rounded-xl shadow-2xl p-1.5 z-50 space-y-1">
                    <Link 
                      href="/admin" 
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
            </div>
          </div>

          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">Navigation</p>
          <nav className="space-y-1 mb-6">
            <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📈 Dashboard
            </Link>
            <Link href={`/tenant/${tenantSlug}/reports`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📄 MIS Reports
            </Link>
            <Link href={`/tenant/${tenantSlug}/cash-flow`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30">
              💵 Cash Flow
            </Link>
            <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📥 Downloads
            </Link>
            <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              🔄 Sync Status
            </Link>
          </nav>

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
                  <option value="3 Months">3 Months</option>
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

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 p-6 overflow-y-auto">
        
        {/* Top Header Row */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              💵 Cash Flow Statement
            </h1>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <Building2 className="w-3.5 h-3.5 text-indigo-400" /> {companyName}
            </p>
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300">
              🗓️ {fromMonth} ➔ {toMonth} | 12 months | Indirect Method
            </div>
          </div>

          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* 5 KPI CARDS (Python Screenshot 1:1 Match) */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
          <div className="bg-[#0f1629] p-4 rounded-2xl border border-white/10">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-1 flex items-center gap-1">
              💰 Net Cash Generated (period)
            </p>
            <h3 className="text-2xl font-black text-slate-100">-₹10.83Cr</h3>
          </div>

          <div className="bg-[#0f1629] p-4 rounded-2xl border border-white/10">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-1 flex items-center gap-1">
              ⚙️ CFO (period)
            </p>
            <h3 className="text-2xl font-black text-slate-100">₹48.56Cr</h3>
          </div>

          <div className="bg-[#0f1629] p-4 rounded-2xl border border-white/10">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-1 flex items-center gap-1">
              📈 CFI (period)
            </p>
            <h3 className="text-2xl font-black text-slate-100">-₹1.04Cr</h3>
          </div>

          <div className="bg-[#0f1629] p-4 rounded-2xl border border-white/10">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-1 flex items-center gap-1">
              💵 CFF (period)
            </p>
            <h3 className="text-2xl font-black text-slate-100">-₹58.35Cr</h3>
          </div>

          <div className="bg-[#0f1629] p-4 rounded-2xl border border-white/10">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-1 flex items-center gap-1">
              🏦 Closing Cash (Jul-26)
            </p>
            <h3 className="text-2xl font-black text-slate-100">₹5.16Cr</h3>
          </div>
        </div>

        {/* RECONCILIATION CAPTION BAR */}
        <div className="mb-6 bg-white/[0.02] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-300 flex items-center gap-2">
          <span>🔍 Reconciliation: 2/12 months tied out within tolerance.</span>
          <span className="text-amber-400 font-semibold flex items-center gap-1">
            ⚠️ Some months need review — see the Difference row in the statement below.
          </span>
        </div>

        {/* SUB-NAVIGATION TABS */}
        <div className="flex border-b border-white/10 mb-6 gap-2">
          <button 
            onClick={() => setActiveTab('chart')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'chart' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            📊 Chart View
          </button>
          <button 
            onClick={() => setActiveTab('statement')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'statement' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            📋 Cash Flow Statement
          </button>
        </div>

        {/* TAB 1: CHART VIEW */}
        {activeTab === 'chart' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* CFO vs CFI vs CFF by Month */}
              <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
                <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                  📊 CFO vs CFI vs CFF by Month
                </h3>
                <div className="h-72 w-full">
                  {mounted ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatINR(val)} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                        <Bar dataKey="cfo" name="CFO" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={16} />
                        <Bar dataKey="cfi" name="CFI" fill="#f59e0b" radius={[4, 4, 0, 0]} maxBarSize={16} />
                        <Bar dataKey="cff" name="CFF" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={16} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : null}
                </div>
              </div>

              {/* Closing Cash Balance Trend */}
              <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
                <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                  🏦 Closing Cash Balance Trend
                </h3>
                <div className="h-72 w-full">
                  {mounted ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <defs>
                          <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00b4d8" stopOpacity={0.5}/>
                            <stop offset="95%" stopColor="#00b4d8" stopOpacity={0.05}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatINR(val)} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                        <Area type="monotone" dataKey="actualClosing" name="Actual Closing Cash" stroke="#00b4d8" strokeWidth={2.5} fill="url(#actualGrad)" />
                        <Line type="monotone" dataKey="computedClosing" name="Computed Closing Cash" stroke="#ef4444" strokeDasharray="3 3" strokeWidth={2} dot={{ r: 3 }} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Bottom Chart: Cash Bridge — Jul-26 */}
            <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">
                💧 Cash Bridge — Jul-26
              </h3>
              <div className="h-64 w-full">
                {mounted ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={cashBridgeData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                      <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px' }} formatter={(val: number) => formatINR(val)} />
                      <Bar dataKey="val" radius={[4, 4, 0, 0]} maxBarSize={60}>
                        {cashBridgeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : null}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CASH FLOW STATEMENT TABLE */}
        {activeTab === 'statement' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-base font-extrabold text-slate-100 flex items-center gap-2">
                📋 Cash Flow Statement — Monthly (Indirect Method)
              </h3>
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-colors">
                <Download className="w-4 h-4" /> Export
              </button>
            </div>

            <div className="bg-[#0f1629] border border-white/10 rounded-2xl overflow-x-auto shadow-2xl">
              <table className="w-full text-left text-xs text-slate-300 border-collapse">
                <thead className="bg-[#151c33] text-slate-300 uppercase text-[11px] font-bold border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3 border-r border-white/10 min-w-[320px]">Particulars</th>
                    {months.map(m => (
                      <th key={m} className="px-3 py-3 border-r border-white/10 text-center min-w-[90px]">{m}</th>
                    ))}
                    <th className="px-4 py-3 text-right font-black text-indigo-300 bg-[#12233d]">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {statementSections.map((sec, sIdx) => (
                    <React.Fragment key={sIdx}>
                      {/* Section Banner Header */}
                      <tr className="bg-[#1e293b] font-extrabold text-slate-100">
                        <td colSpan={months.length + 2} className="px-4 py-2.5 text-xs text-indigo-300 tracking-wide border-y border-white/10">
                          {sec.title}
                        </td>
                      </tr>

                      {/* Ledger Rows */}
                      {sec.rows.map((r: any, rIdx: number) => {
                        let bgClass = "hover:bg-white/[0.02]";
                        let textClass = "text-slate-300";
                        if (r.isSubtotal) {
                          bgClass = "bg-[#151c33]/80 font-bold border-y border-indigo-500/20";
                          textClass = "text-indigo-300";
                        } else if (r.isCfo) {
                          bgClass = "bg-[#10b981]/20 font-black text-emerald-300 border-y border-emerald-500/30";
                        } else if (r.isCfi) {
                          bgClass = "bg-[#f59e0b]/20 font-black text-amber-300 border-y border-amber-500/30";
                        } else if (r.isCff) {
                          bgClass = "bg-[#8b5cf6]/20 font-black text-purple-300 border-y border-purple-500/30";
                        }

                        return (
                          <tr key={rIdx} className={`${bgClass} transition-colors`}>
                            <td className={`px-4 py-2.5 font-medium border-r border-white/10 pl-6 ${textClass}`}>{r.label}</td>
                            {months.map(m => (
                              <td key={m} className={`px-3 py-2.5 text-center font-mono border-r border-white/10 ${textClass}`}>
                                {formatINR(r.vals[m] || 0)}
                              </td>
                            ))}
                            <td className="px-4 py-2.5 text-right font-mono font-bold border-l-2 border-indigo-500/30 text-indigo-300 bg-[#12233d]">
                              {formatINR(Object.values(r.vals as Record<string, number>).reduce((a, b) => a + b, 0))}
                            </td>
                          </tr>
                        );
                      })}
                    </React.Fragment>
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
