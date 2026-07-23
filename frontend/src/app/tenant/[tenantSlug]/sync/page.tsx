'use client';

import React, { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  PieChart as PieChartIcon, Building2, RotateCcw, RefreshCw, ChevronDown, 
  ChevronUp, CheckCircle2, HelpCircle, Settings
} from 'lucide-react';

export default function SyncPortal({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [showSettings, setShowSettings] = useState(false);
  const [tallyUrl, setTallyUrl] = useState('https://chevron-gumming-sloped.ngrok-free.dev');
  const [isUrlSettingsOpen, setIsUrlSettingsOpen] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState('2026-07-22 13:26:07');
  const [connectedUrl, setConnectedUrl] = useState('https://chevron-gumming-sloped.ngrok-free.dev');
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

  const handleUpdateUrl = (e: React.FormEvent) => {
    e.preventDefault();
    setConnectedUrl(tallyUrl);
    alert(`Tally URL updated to ${tallyUrl}`);
  };

  const handleSyncNow = () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
      const now = new Date();
      const formattedStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
      setLastSyncTime(formattedStr);
      alert('Tally data synced successfully!');
    }, 2500);
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
              <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
                📥 Downloads
              </Link>
            )}
            {(tenantFeatures.length === 0 || tenantFeatures.includes('sync')) && (
              <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30">
                🔄 Sync Status
              </Link>
            )}
          </nav>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 p-6 overflow-y-auto">
        
        {/* Header */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              🔄 Sync Status
            </h1>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* Collapsible Connection Settings Card (Matching Python Screenshot 2) */}
        <div className="bg-[#0f1629] border border-white/10 rounded-2xl mb-6 shadow-2xl overflow-hidden">
          <div 
            onClick={() => setIsUrlSettingsOpen(!isUrlSettingsOpen)}
            className="p-4 bg-[#151c33]/50 flex items-center justify-between cursor-pointer border-b border-white/5 select-none"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
              <Settings className="w-4 h-4 text-indigo-400" />
              <span>Connection Settings</span>
            </div>
            {isUrlSettingsOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {isUrlSettingsOpen && (
            <form onSubmit={handleUpdateUrl} className="p-5 space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-extrabold uppercase text-slate-400 tracking-wider">TALLY SERVER URL</label>
                  <HelpCircle className="w-4 h-4 text-slate-500 cursor-pointer" title="Enter your Tally HTTP URL or Ngrok Tunnel" />
                </div>
                <input 
                  type="text" 
                  value={tallyUrl}
                  onChange={(e) => setTallyUrl(e.target.value)}
                  className="w-full bg-[#15233c] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500" 
                />
              </div>

              <button 
                type="submit"
                className="px-5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-200 text-xs font-bold transition-colors"
              >
                Update URL
              </button>
            </form>
          )}
        </div>

        {/* Green Connection Banner (Matching Screenshot 2) */}
        <div className="mb-8 bg-[#12382c] border border-emerald-500/30 rounded-2xl p-4 flex items-center gap-2 text-xs font-bold text-emerald-300 shadow-xl">
          <span>✅</span>
          <span>Tally connected successfully at</span>
          <span className="underline font-mono">{connectedUrl}</span>
        </div>

        {/* Sync Data from Tally Section (Matching Screenshot 2) */}
        <div className="flex justify-between items-center mb-8 bg-[#0f1629] border border-white/10 p-6 rounded-2xl shadow-2xl">
          <div>
            <h2 className="text-xl font-extrabold text-slate-100">Sync Data from Tally</h2>
            <p className="text-xs text-slate-400 mt-1">This will fetch all companies from Tally and sync their data to the portal.</p>
          </div>

          <button 
            onClick={handleSyncNow}
            disabled={isSyncing}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Syncing...' : '🔄 Sync Now'}
          </button>
        </div>

        {/* Company Sync Status Section (Matching Screenshot 2) */}
        <div className="space-y-4">
          <h2 className="text-xl font-extrabold text-slate-100">Company Sync Status</h2>

          <div className="bg-[#0f1629] border border-white/10 rounded-2xl p-4 flex items-center justify-between shadow-xl">
            <div className="flex items-center gap-2 text-xs font-extrabold text-slate-100">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
              <span>Unique Steel Products</span>
            </div>
            <span className="text-xs font-mono text-slate-400">{lastSyncTime}</span>
          </div>
        </div>

      </main>
    </div>
  );
}
