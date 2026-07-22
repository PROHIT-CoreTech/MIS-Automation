'use client';

import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Line, ComposedChart, Area, AreaChart, PieChart, Pie, Cell, LineChart
} from 'recharts';
import { 
  Building2, TrendingUp, TrendingDown, DollarSign, Wallet, FileBarChart, PieChart as PieChartIcon, Target, Lightbulb
} from 'lucide-react';
import Link from 'next/link';
import { use, useState, useEffect } from 'react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

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

  useEffect(() => {
    setMounted(true);
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`http://localhost:5000/api/financial/dashboard/${tenantSlug}`);
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
    if (tenantSlug) {
      fetchDashboard();
    }
  }, [tenantSlug]);

  const companyName = dashboardData?.companyName || (tenantSlug ? tenantSlug.replace(/_/g, ' ').toUpperCase() : "Tenant Portal");
  const dateRange = dashboardData?.dateRange || "Live Financial Analytics";
  const stats = dashboardData?.stats || { totalRevenue: 0, grossProfit: 0, netProfit: 0, cashBank: 0, overhead: 0, gpPct: 0, npPct: 0 };
  const chartData = dashboardData?.chartData || [];
  const overheadData = dashboardData?.overheadData || [];

  const formatLakhs = (val: number) => {
    if (!val) return '₹0 L';
    return `₹${(val / 100000).toFixed(1)} L`;
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
          <Link href={`/tenant/${tenantSlug}`} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-medium transition-colors">
            <Target className="w-4 h-4" /> Dashboard
          </Link>
          <Link href={`/tenant/${tenantSlug}/sync`} className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-slate-400 hover:text-slate-200 transition-colors">
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
      <div className="ml-64 p-8 max-w-7xl">
        
        {/* Sticky Header */}
        <div className="sticky top-0 z-10 bg-[#090b14]/80 backdrop-blur-md py-4 mb-6 border-b border-white/10 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
              📊 Management Dashboard
            </h1>
            <p className="text-sm text-slate-400 mt-2 flex items-center gap-2">
              <Building2 className="w-4 h-4" /> {companyName} <span className="text-white/20">|</span> 📅 {dateRange}
            </p>
          </div>
          <div>
            <button className="bg-white/5 border border-white/10 hover:bg-white/10 text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              Export PDF
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-5 rounded-2xl border border-white/10">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">📈 Revenue</p>
            <h3 className="text-2xl font-bold text-slate-100">{formatLakhs(stats.totalRevenue)}</h3>
          </div>
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-5 rounded-2xl border border-white/10">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">💹 Gross Profit</p>
            <h3 className="text-2xl font-bold text-slate-100">{formatLakhs(stats.grossProfit)}</h3>
            <p className="text-xs text-emerald-400 font-medium mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> {stats.gpPct}%</p>
          </div>
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-5 rounded-2xl border border-white/10">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">💰 Net Profit</p>
            <h3 className="text-2xl font-bold text-slate-100">{formatLakhs(stats.netProfit)}</h3>
            <p className="text-xs text-emerald-400 font-medium mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> {stats.npPct}%</p>
          </div>
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-5 rounded-2xl border border-white/10">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">🏦 Cash & Bank</p>
            <h3 className="text-2xl font-bold text-slate-100">{formatLakhs(stats.cashBank)}</h3>
          </div>
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-5 rounded-2xl border border-white/10">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">💸 Overhead</p>
            <h3 className="text-2xl font-bold text-slate-100">{formatLakhs(stats.overhead)}</h3>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">📈 Revenue vs Profit Trend</h3>
            <div className="h-72 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${(value/100000).toFixed(0)}L`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                      itemStyle={{ color: '#f1f5f9' }}
                      formatter={(value: number) => `₹${(value/100000).toFixed(1)} L`}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Bar dataKey="revenue" name="Revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    <Line type="monotone" dataKey="gp" name="Gross Profit" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="np" name="Net Profit" stroke="#0ea5e9" strokeDasharray="5 5" strokeWidth={3} dot={{ r: 4 }} />
                  </ComposedChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">💸 Overhead Breakdown</h3>
            <div className="h-72 w-full flex justify-center items-center">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={overheadData}
                      cx="50%"
                      cy="50%"
                      innerRadius={70}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                      stroke="none"
                    >
                      {overheadData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                      formatter={(value: number) => `₹${(value/1000).toFixed(0)} K`}
                    />
                    <Legend verticalAlign="middle" align="right" layout="vertical" wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">🏦 Cash & Bank Trend</h3>
            <div className="h-64 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${(value/100000).toFixed(0)}L`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                      formatter={(value: number) => `₹${(value/100000).toFixed(1)} L`}
                    />
                    <Area type="monotone" dataKey="cash" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorCash)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2">📊 GP% vs NP% Trend</h3>
            <div className="h-64 w-full">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                      formatter={(value: number) => `${value}%`}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type="monotone" dataKey="gpPct" name="GP%" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="npPct" name="NP%" stroke="#8b5cf6" strokeDasharray="5 5" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>
        </div>

        {/* Key Insights */}
        <div className="mt-8">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" /> Key Insights
          </h3>
          
          <div className="space-y-3">
            <div className="bg-emerald-500/10 border-l-4 border-emerald-500 border-y border-r border-emerald-500/20 p-4 rounded-r-xl backdrop-blur-sm">
              <p className="font-bold text-emerald-400 flex items-center gap-2">✅ Strong Gross Margin</p>
              <p className="text-sm text-emerald-400/80 mt-1">GP% 33.8% — healthy profitability</p>
            </div>
            
            <div className="bg-indigo-500/10 border-l-4 border-indigo-500 border-y border-r border-indigo-500/20 p-4 rounded-r-xl backdrop-blur-sm">
              <p className="font-bold text-indigo-400 flex items-center gap-2">✅ Profitable</p>
              <p className="text-sm text-indigo-400/80 mt-1">Net profit ₹7.0 L (18.9%)</p>
            </div>
            
            <div className="bg-emerald-500/10 border-l-4 border-emerald-500 border-y border-r border-emerald-500/20 p-4 rounded-r-xl backdrop-blur-sm">
              <p className="font-bold text-emerald-400 flex items-center gap-2">✅ Overhead Lean</p>
              <p className="text-sm text-emerald-400/80 mt-1">Overhead 14.8% of revenue</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
