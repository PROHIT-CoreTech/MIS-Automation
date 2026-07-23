'use client';

import React, { use, useState } from 'react';
import Link from 'next/link';
import { 
  PieChart as PieChartIcon, Building2, Download, RotateCcw, RefreshCw, ChevronDown, 
  FileSpreadsheet, Presentation, Settings
} from 'lucide-react';

export default function DownloadsPage({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [showSettings, setShowSettings] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<string>('Unique Steel Products');
  const [quickSelect, setQuickSelect] = useState<string>('12 Months');
  const [fromMonth, setFromMonth] = useState<string>('Aug-25');
  const [toMonth, setToMonth] = useState<string>('Jul-26');
  const [isGeneratingExcel, setIsGeneratingExcel] = useState(false);
  const [isGeneratingPPT, setIsGeneratingPPT] = useState(false);
  const [tenantFeatures, setTenantFeatures] = useState<string[]>([]);
  const [authUser, setAuthUser] = useState<{ username: string; full_name: string; role: string } | null>(null);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) { try { setAuthUser(JSON.parse(userStr)); } catch (e) {} }
    if (tenantSlug) {
      fetch(`http://localhost:5001/api/financial/tenant-info/${tenantSlug}`)
        .then(r => r.ok ? r.json() : null)
        .then(info => { if (info?.features) setTenantFeatures(Array.isArray(info.features) ? info.features : []); })
        .catch(() => {});
    }
  }, [tenantSlug]);

  const handleResetFilters = () => {
    setQuickSelect('12 Months');
    setFromMonth('Aug-25');
    setToMonth('Jul-26');
  };

  const handleGenerateExcel = () => {
    setIsGeneratingExcel(true);
    setTimeout(() => {
      setIsGeneratingExcel(false);
      alert('Excel report generated successfully!');
    }, 1500);
  };

  const handleGeneratePPT = () => {
    setIsGeneratingPPT(true);
    setTimeout(() => {
      setIsGeneratingPPT(false);
      alert('PowerPoint presentation generated successfully!');
    }, 1500);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/login';
  };

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

          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">Navigation</p>
          <nav className="space-y-1 mb-6">
            <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📈 Dashboard
            </Link>
            {(tenantFeatures.length === 0 || tenantFeatures.includes('reports')) && (
              <Link href={`/tenant/${tenantSlug}/reports`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                📄 MIS Reports
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('cash_flow')) && (
              <Link href={`/tenant/${tenantSlug}/cash-flow`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                💵 Cash Flow
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('downloads')) && (
              <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30">
                📥 Downloads
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('sync')) && (
              <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                🔄 Sync Status
              </Link>
            )}
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
        
        {/* Header */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              📥 Export Reports
            </h1>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <Building2 className="w-3.5 h-3.5 text-indigo-400" /> {selectedCompany}
            </p>
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300">
              🗓️ {fromMonth} ➔ {toMonth} | 12 months selected
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* Company & Date Sub-header Banner (Matching Screenshot 1) */}
        <div className="bg-[#0f1629] border border-white/10 rounded-2xl p-4 mb-6">
          <div className="flex items-center gap-4 text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-1.5 font-bold text-slate-100">
              🏢 {selectedCompany}
            </span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">
              🗓️ {fromMonth} ➔ {toMonth}
            </span>
          </div>
        </div>

        {/* Selection summary text */}
        <div className="text-xs font-medium text-slate-400 mb-6 flex items-center gap-2">
          <span>📊 12 months selected:</span>
          <span className="font-bold text-slate-200">{fromMonth} ➔ {toMonth}</span>
        </div>

        {/* 2 Large Export Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Excel Export Card */}
          <div className="bg-[#0f1629] border border-white/10 p-8 rounded-2xl flex flex-col justify-between shadow-2xl hover:border-indigo-500/50 transition-all">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">🟩</span>
                <h3 className="text-xl font-extrabold text-slate-100">Excel Export</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-8">
                Full <strong className="text-slate-200">P&L Detailed Report</strong> with monthly columns, section headers, subtotals, GP and NP rows — formatted with colors.
              </p>
            </div>

            <button 
              onClick={handleGenerateExcel}
              disabled={isGeneratingExcel}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30"
            >
              <Settings className={`w-4 h-4 ${isGeneratingExcel ? 'animate-spin' : ''}`} /> 
              {isGeneratingExcel ? 'Generating Excel...' : '⚙️ Generate Excel'}
            </button>
          </div>

          {/* PowerPoint Export Card */}
          <div className="bg-[#0f1629] border border-white/10 p-8 rounded-2xl flex flex-col justify-between shadow-2xl hover:border-indigo-500/50 transition-all">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">📁</span>
                <h3 className="text-xl font-extrabold text-slate-100">PowerPoint Export</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-8">
                3-slide <strong className="text-slate-200">MIS Presentation</strong> with title slide, KPI summary cards, and detailed P&L table — ready to share with management.
              </p>
            </div>

            <button 
              onClick={handleGeneratePPT}
              disabled={isGeneratingPPT}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30"
            >
              <Settings className={`w-4 h-4 ${isGeneratingPPT ? 'animate-spin' : ''}`} /> 
              {isGeneratingPPT ? 'Generating PowerPoint...' : '⚙️ Generate PowerPoint'}
            </button>
          </div>

        </div>

      </main>
    </div>
  );
}
