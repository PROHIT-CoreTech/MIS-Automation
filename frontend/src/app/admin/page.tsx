'use client';

import { useState, useEffect } from 'react';
import { Shield, Search, Plus, CheckCircle2, XCircle, LayoutDashboard, Building2, UserPlus } from 'lucide-react';
import Link from 'next/link';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: string;
  status: string;
  mrr: number;
}

const COLORS = ['#eab308', '#94a3b8', '#10b981', '#6366f1']; 

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'manage' | 'create'>('dashboard');
  const [search, setSearch] = useState('');
  
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [stats, setStats] = useState({ total_mrr: 0, active_subscriptions: 0, total_users: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [serverError, setServerError] = useState(false);

  useEffect(() => {
    setMounted(true);
    const fetchDashboardData = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/admin/dashboard');
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        if (data.tenants) {
          setTenants(data.tenants);
          setStats(data.stats);
          setServerError(false);
        }
      } catch (error) {
        setServerError(true);
        console.warn('Express backend server is offline or unreachable on http://localhost:5000.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const revenueByPlan = tenants.reduce((acc, tenant) => {
    const existingIndex = acc.findIndex(item => item.name === tenant.plan);
    if (existingIndex >= 0) {
      acc[existingIndex] = { ...acc[existingIndex], value: acc[existingIndex].value + (tenant.mrr || 0) };
    } else {
      acc.push({ name: tenant.plan || 'Other', value: tenant.mrr || 0 });
    }
    return acc;
  }, [] as {name: string, value: number}[]);

  return (
    <div className="min-h-screen bg-[#090b14] text-slate-200 font-sans selection:bg-indigo-500/30">
      {/* Header */}
      <header className="bg-[#0f1629]/80 backdrop-blur-xl border-b border-white/10 px-8 py-5 flex justify-between items-center sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
            <Shield className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">SaaS Admin Portal</h1>
            <p className="text-xs text-slate-400 font-medium tracking-wider uppercase">System Configuration Access</p>
          </div>
        </div>
        <div className="flex gap-4">
          <button className="text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 border border-white/5 px-4 py-2 rounded-lg transition-colors text-sm font-medium">
            Log out
          </button>
        </div>
      </header>

      <main className="p-8 max-w-7xl mx-auto">
        
        {serverError && (
          <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-sm flex items-center justify-between animate-in fade-in">
            <div>
              <span className="font-bold">⚠️ Backend Server Disconnected:</span> Please start the Express backend server (`cd backend && npm start`) to fetch live MongoDB tenant data.
            </div>
            <button 
              onClick={() => {
                setIsLoading(true);
                setServerError(false);
                fetch('http://localhost:5000/api/admin/dashboard')
                  .then(res => res.json())
                  .then(data => { setTenants(data.tenants); setStats(data.stats); setServerError(false); })
                  .catch(() => setServerError(true))
                  .finally(() => setIsLoading(false));
              }} 
              className="px-3 py-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 rounded-lg text-xs font-semibold transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-1 bg-white/5 p-1 rounded-xl w-fit mb-8 border border-white/10">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === 'dashboard' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('manage')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === 'manage' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
          >
            <Building2 className="w-4 h-4" />
            Manage Tenants
          </button>
          <button 
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === 'create' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
          >
            <UserPlus className="w-4 h-4" />
            Create Tenant
          </button>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* MRR Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-6 rounded-2xl border border-indigo-500/30 relative overflow-hidden group hover:border-indigo-500/60 transition-colors">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl -mr-10 -mt-10 group-hover:bg-indigo-500/20 transition-colors"></div>
                <p className="text-sm font-semibold text-indigo-400 tracking-wider uppercase mb-2">Total Monthly Revenue</p>
                <h3 className="text-4xl font-extrabold text-slate-100">₹{stats.total_mrr.toLocaleString()}</h3>
              </div>
              <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-6 rounded-2xl border border-white/10 hover:border-emerald-500/40 transition-colors relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl -mr-10 -mt-10 group-hover:bg-emerald-500/10 transition-colors"></div>
                <p className="text-sm font-semibold text-emerald-400 tracking-wider uppercase mb-2">Active Subscriptions</p>
                <h3 className="text-4xl font-extrabold text-slate-100">{stats.active_subscriptions}</h3>
              </div>
              <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-6 rounded-2xl border border-white/10 hover:border-orange-500/40 transition-colors relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-full blur-3xl -mr-10 -mt-10 group-hover:bg-orange-500/10 transition-colors"></div>
                <p className="text-sm font-semibold text-orange-400 tracking-wider uppercase mb-2">Total Platform Users</p>
                <h3 className="text-4xl font-extrabold text-slate-100">{stats.total_users}</h3>
              </div>
            </div>

            {/* Revenue By Plan & Payment Details Mockup */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-slate-200 mb-6">Revenue by Plan</h3>
                <div className="h-64 w-full flex items-center justify-center">
                  {mounted && revenueByPlan.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={revenueByPlan}
                          cx="50%"
                          cy="50%"
                          innerRadius={70}
                          outerRadius={100}
                          paddingAngle={2}
                          dataKey="value"
                          stroke="none"
                        >
                          {revenueByPlan.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                          formatter={(value: number) => `₹${value.toLocaleString()}`}
                        />
                        <Legend verticalAlign="middle" align="right" layout="vertical" wrapperStyle={{ fontSize: '14px', color: '#f1f5f9' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full w-full flex items-center justify-center text-slate-500 text-sm">
                      {isLoading ? "Loading analytics chart..." : "No revenue plan data available"}
                    </div>
                  )}
                </div>
              </div>
              <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-slate-200 mb-6">Tenant Payment Details</h3>
                <div className="space-y-4">
                  {tenants.map(t => (
                    <div key={t.id} className="flex justify-between items-center p-4 bg-black/20 rounded-xl border border-white/5">
                      <div>
                        <p className="font-bold text-slate-200">{t.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{t.plan} Plan</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-slate-200">₹{t.mrr}</p>
                        <p className="text-xs text-emerald-400 mt-1">{t.status === 'active' ? '🟢 Active' : '🔴 Suspended'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'manage' && (
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 rounded-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-xl shadow-black/50">
            <div className="p-6 border-b border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 bg-black/20">
              <h2 className="text-lg font-bold text-slate-100">All Registered Tenants</h2>
              
              <div className="relative w-full sm:w-72">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Search tenants..." 
                  className="w-full pl-9 pr-4 py-2 bg-black/40 border border-white/10 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-400">
                <thead className="bg-black/40 text-slate-300 font-medium border-b border-white/10">
                  <tr>
                    <th className="px-6 py-4">Tenant Name</th>
                    <th className="px-6 py-4">Subdomain URL</th>
                    <th className="px-6 py-4">Plan</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 bg-[#0f1629]/40">
                  {tenants.filter(t => t.name.toLowerCase().includes(search.toLowerCase())).map((tenant) => (
                    <tr key={tenant.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-200">{tenant.name}</td>
                      <td className="px-6 py-4">
                        <Link href={`http://${tenant.slug}.localhost:3000`} className="text-indigo-400 hover:text-indigo-300 hover:underline">
                          {tenant.slug}.localhost:3000
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-white/5 text-slate-300 border border-white/10">
                          {tenant.plan}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {tenant.status === 'active' ? (
                          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                            <CheckCircle2 className="w-4 h-4" /> Active
                          </span>
                        ) : (
                          <span className="flex items-center gap-1.5 text-rose-400 font-medium">
                            <XCircle className="w-4 h-4" /> Suspended
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-indigo-400 hover:text-indigo-300 font-medium text-sm">
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className="bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 rounded-2xl p-8 max-w-3xl animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-xl shadow-black/50">
            <h2 className="text-xl font-bold text-slate-100 mb-2">Register a New Tenant</h2>
            <p className="text-slate-400 text-sm mb-8">This will create a new tenant environment and assign a default Tenant Administrator.</p>
            
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <h3 className="font-semibold text-slate-200 border-b border-white/10 pb-2">Company Details</h3>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Tenant Organization Name *</label>
                    <input type="text" placeholder="e.g. Hooli Inc." className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Unique URL/Slug *</label>
                    <input type="text" placeholder="e.g. hooli" className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Plan Level *</label>
                    <select className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 appearance-none">
                      <option>Bronze</option>
                      <option>Silver</option>
                      <option>Gold</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-slate-200 border-b border-white/10 pb-2">Tenant Administrator Account</h3>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Admin Full Name *</label>
                    <input type="text" placeholder="e.g. Richard Hendricks" className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Admin Username *</label>
                    <input type="text" placeholder="e.g. richard_admin" className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-1.5">Admin Password *</label>
                    <input type="password" placeholder="Enter secure password" className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500" />
                  </div>
                </div>
              </div>
              
              <div className="pt-4 mt-6 border-t border-white/10">
                <button type="button" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl transition-colors shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2">
                  🚀 Register Tenant & Create Admin
                </button>
              </div>
            </form>
          </div>
        )}

      </main>
    </div>
  );
}

