'use client';

import React, { use, useState } from 'react';
import Link from 'next/link';
import { 
  PieChart as PieChartIcon, Building2, RotateCcw, RefreshCw, ChevronDown, CheckCircle2, Settings
} from 'lucide-react';

export default function SubscriptionPage({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [showSettings, setShowSettings] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<string>('Unique Steel Products');

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
            <Link href={`/tenant/${tenantSlug}/cash-flow`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              💵 Cash Flow
            </Link>
            <Link href={`/tenant/${tenantSlug}/downloads`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              📥 Downloads
            </Link>
            <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors">
              🔄 Sync Status
            </Link>
          </nav>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 p-6 overflow-y-auto">
        
        {/* Header */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              💳 Subscription Details
            </h1>
            <p className="text-xs text-slate-400 mt-1">Manage your workspace plan and billing.</p>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* 3 Status Cards (Matching Python Screenshot 1) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          
          {/* Card 1: Current Plan */}
          <div className="bg-[#1b2b48] border border-white/10 p-5 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 mb-3">Current Plan</p>
            <div className="bg-[#15233c] border border-white/10 rounded-xl p-3.5">
              <span className="text-base font-extrabold text-slate-100">Silver</span>
            </div>
          </div>

          {/* Card 2: Status */}
          <div className="bg-[#1b2b48] border border-white/10 p-5 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 mb-3">Status</p>
            <div className="bg-[#12382c] border border-emerald-500/30 rounded-xl p-3.5 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
              <span className="text-base font-bold text-emerald-300">Active</span>
            </div>
          </div>

          {/* Card 3: Renewal Date */}
          <div className="bg-[#1b2b48] border border-white/10 p-5 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 mb-3">Renewal Date</p>
            <div className="bg-[#38331d] border border-amber-500/30 rounded-xl p-3.5">
              <span className="text-base font-bold text-amber-200">21 August, 2026</span>
            </div>
          </div>

        </div>

        {/* Section: Enabled Features */}
        <div className="space-y-4">
          <h2 className="text-xl font-extrabold text-slate-100 flex items-center gap-2">
            🌟 Enabled Features
          </h2>

          <ul className="space-y-3 pl-4 text-xs font-semibold text-slate-200">
            <li className="flex items-center gap-2">
              <span className="text-slate-500">•</span>
              <span className="text-emerald-400">✅</span>
              <span>Dashboard</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-slate-500">•</span>
              <span className="text-emerald-400">✅</span>
              <span>Reports</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-slate-500">•</span>
              <span className="text-emerald-400">✅</span>
              <span>Cash Flow</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-slate-500">•</span>
              <span className="text-emerald-400">✅</span>
              <span>Downloads</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-slate-500">•</span>
              <span className="text-emerald-400">✅</span>
              <span>Sync</span>
            </li>
          </ul>
        </div>

      </main>
    </div>
  );
}
