'use client';

import { use, useState } from 'react';
import { 
  Building2, TrendingUp, FileBarChart, PieChart as PieChartIcon, Target, 
  RefreshCw, CheckCircle2, AlertCircle, Clock, Database 
} from 'lucide-react';
import Link from 'next/link';

export default function SyncPortal({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState('2026-03-24 14:30:00');
  
  // Mock company details
  const companyName = tenantSlug ? tenantSlug.replace(/_/g, ' ').toUpperCase() : "Rohit Inc";

  const handleSync = () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
      setLastSync(new Date().toLocaleString());
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#090b14] text-slate-200 font-sans selection:bg-indigo-500/30">
      
      {/* Sidebar Navigation */}
      <div className="fixed w-64 h-full bg-[#0f1629]/90 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col z-20">
        <div className="mb-10">
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <PieChartIcon className="w-5 h-5 text-indigo-400" />
            MIS Portal
          </h2>
          <p className="text-xs text-indigo-400 mt-1 font-medium px-7 uppercase tracking-wider">{companyName}</p>
        </div>

        <nav className="space-y-1 flex-1">
          <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 transition-colors">
            <Target className="w-4 h-4" /> Dashboard
          </Link>
          <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-medium transition-colors">
            <TrendingUp className="w-4 h-4" /> Tally Sync
          </Link>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 transition-colors text-left">
            <FileBarChart className="w-4 h-4" /> MIS Reports
          </button>
        </nav>

        <div className="mt-auto">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <p className="text-xs text-slate-400 font-medium mb-1">Logged in as</p>
            <p className="text-sm font-bold text-slate-200">Admin User</p>
            <button className="text-xs text-rose-400 hover:text-rose-300 mt-2 font-medium">Sign Out</button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8 max-w-4xl mx-auto">
        
        {/* Sticky Header */}
        <div className="sticky top-0 z-10 bg-[#090b14]/80 backdrop-blur-md py-4 mb-8 border-b border-white/10 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
              🔄 Tally Prime Synchronization
            </h1>
            <p className="text-sm text-slate-400 mt-2">
              Securely connect and pull financial records directly from Tally ODBC.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          
          {/* Status Card */}
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 rounded-2xl p-8 relative overflow-hidden shadow-xl shadow-black/50">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
            
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/30">
                <Database className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Connection Status</p>
                <h3 className="text-xl font-bold text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" /> Active
                </h3>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="text-slate-400 flex items-center gap-2"><Building2 className="w-4 h-4" /> Company</span>
                <span className="font-bold text-slate-200">{companyName}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="text-slate-400 flex items-center gap-2"><Clock className="w-4 h-4" /> Last Synced</span>
                <span className="font-medium text-slate-200">{lastSync}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-slate-400">Records Parsed</span>
                <span className="font-medium text-slate-200">12,450 rows</span>
              </div>
            </div>
          </div>

          {/* Sync Action Card */}
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-indigo-500/30 rounded-2xl p-8 flex flex-col justify-center items-center text-center shadow-[0_8px_32px_rgba(99,102,241,0.1)]">
            <h3 className="text-xl font-bold text-slate-100 mb-2">Manual Sync Trigger</h3>
            <p className="text-slate-400 text-sm mb-8">
              Initiate a manual pull of the latest P&L and Balance Sheet ledgers from the connected Tally Prime instance.
            </p>

            <button 
              onClick={handleSync}
              disabled={isSyncing}
              className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all ${
                isSyncing 
                  ? 'bg-indigo-600/50 text-indigo-200 cursor-not-allowed' 
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:-translate-y-1'
              }`}
            >
              <RefreshCw className={`w-5 h-5 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? 'Synchronizing Data...' : 'Sync Now'}
            </button>
          </div>

        </div>

        {/* Instructions */}
        <div className="bg-indigo-500/10 border-l-4 border-indigo-500 border-y border-r border-indigo-500/20 p-6 rounded-r-xl backdrop-blur-sm">
          <h4 className="font-bold text-indigo-400 flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5" /> Prerequisites for Sync
          </h4>
          <ul className="list-disc list-inside text-sm text-indigo-200/80 space-y-2">
            <li>Ensure Tally Prime is running on the host machine.</li>
            <li>ODBC Server must be enabled in Tally settings (F12) on port 9000.</li>
            <li>The company <strong className="text-indigo-300">{companyName}</strong> must be open and selected in Tally.</li>
            <li>If you encounter errors, check the terminal logs of the Node.js backend.</li>
          </ul>
        </div>

      </div>
    </div>
  );
}
