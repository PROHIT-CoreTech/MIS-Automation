'use client';

import React, { useState, useEffect } from 'react';
import { 
  Building2, DollarSign, Users, Plus, Key, Eye, EyeOff, 
  RotateCcw, RefreshCw, ChevronDown, CheckCircle2, Lock, Shield, Settings, Percent, Activity
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend } from 'recharts';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: string;
  status: string;
  mrr: number;
  features: string[];
  is_active: boolean;
}

interface Stats {
  total_mrr: number;
  active_subscriptions: number;
  total_users: number;
}

const PLAN_PRICES: Record<string, number> = { Bronze: 2999, Silver: 4999, Gold: 9999 };
const PLAN_COLORS: Record<string, string> = { Bronze: '#f59e0b', Silver: '#94a3b8', Gold: '#eab308' };

const FEATURES_MAP: Record<string, string> = {
  "📊 Dashboard": "dashboard",
  "📄 MIS Reports": "reports",
  "💵 Cash Flow": "cash_flow",
  "📥 Downloads": "downloads",
  "🔄 Tally Sync": "sync"
};

const PLAN_DEFAULTS: Record<string, string[]> = {
  "Bronze": ["dashboard", "downloads"],
  "Silver": ["dashboard", "reports", "downloads", "sync"],
  "Gold": ["dashboard", "reports", "cash_flow", "downloads", "sync"]
};

export default function SaaSAdminPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'manage' | 'create'>('overview');
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [stats, setStats] = useState<Stats>({ total_mrr: 0, active_subscriptions: 0, total_users: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Create Tenant Form States
  const [tenantName, setTenantName] = useState('');
  const [tenantSlug, setTenantSlug] = useState('');
  const [tenantPlan, setTenantPlan] = useState('Silver');
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>(PLAN_DEFAULTS["Silver"]);
  const [adminName, setAdminName] = useState('');
  const [adminUser, setAdminUser] = useState('');
  const [adminPass, setAdminPass] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Edit Tenant Mode State
  const [editingTenantId, setEditingTenantId] = useState<string | null>(null);
  const [expandedTenantId, setExpandedTenantId] = useState<string | null>(null);
  const [editPlan, setEditPlan] = useState('Silver');
  const [editFeatures, setEditFeatures] = useState<string[]>([]);
  const [editStatus, setEditStatus] = useState(true);

  // Auth User state
  const [authUser, setAuthUser] = useState<{ username: string; full_name: string } | null>(null);

  useEffect(() => {
    // Check if token exists
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if (!token || !userStr) {
      window.location.href = '/login';
      return;
    }
    try {
      const parsedUser = JSON.parse(userStr);
      if (parsedUser.role !== 'super_admin') {
        // If not super_admin, redirect to their tenant page
        const slug = parsedUser.tenant ? parsedUser.tenant.slug : 'default';
        window.location.href = `/tenant/${slug}`;
        return;
      }
      setAuthUser(parsedUser);
    } catch (e) {
      window.location.href = '/login';
      return;
    }

    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError('');
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:5001/api/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        // Normalize features: Python stores as JSON string, ensure it's always an array
        const normalizedTenants = (data.tenants || []).map((t: any) => {
          let features = t.features || [];
          if (typeof features === 'string') {
            try { features = JSON.parse(features); } catch (e) { features = []; }
          }
          if (!Array.isArray(features)) features = [];
          return { ...t, features };
        });
        setTenants(normalizedTenants);
        setStats(data.stats || { total_mrr: 0, active_subscriptions: 0, total_users: 0 });
      } else {
        setError('Failed to fetch dashboard data. Please try again.');
      }
    } catch (err) {
      console.error(err);
      setError('Connection error. Server may be offline.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tenantName || !tenantSlug || !adminName || !adminUser || !adminPass) {
      alert('All required fields (*) must be filled.');
      return;
    }
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:5001/api/admin/tenants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: tenantName,
          slug: tenantSlug.toLowerCase().trim().replace(/\s+/g, '_'),
          plan_name: tenantPlan,
          features: selectedFeatures,
          admin_name: adminName,
          admin_user: adminUser,
          admin_pass: adminPass
        })
      });
      if (res.ok) {
        alert(`Tenant '${tenantName}' and Admin created successfully!`);
        setTenantName('');
        setTenantSlug('');
        setAdminName('');
        setAdminUser('');
        setAdminPass('');
        fetchDashboardData();
        setActiveTab('manage');
      } else {
        const errData = await res.json();
        alert(`Error: ${errData.error || 'Failed to create tenant'}`);
      }
    } catch (err) {
      console.error(err);
      alert('Network error registering tenant.');
    }
  };

  const handleUpdateTenant = async (tenantId: string) => {
    const token = localStorage.getItem('token');
    // Find the tenant to use its values if not in edit mode
    const tenant = tenants.find(t => t.id === tenantId);
    const planToSave = editingTenantId === tenantId ? editPlan : (tenant?.plan || 'Silver');
    const featuresToSave = editingTenantId === tenantId ? editFeatures : (tenant?.features || []);
    const statusToSave = editingTenantId === tenantId ? editStatus : (tenant?.is_active ?? true);

    try {
      const res = await fetch(`http://localhost:5001/api/admin/tenants/${tenantId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_name: planToSave,
          features: featuresToSave,
          is_active: statusToSave
        })
      });
      if (res.ok) {
        alert('Tenant updated successfully!');
        setEditingTenantId(null);
        setExpandedTenantId(null);
        fetchDashboardData();
      } else {
        alert('Failed to update tenant.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error updating tenant.');
    }
  };

  const handleToggleStatus = async (tenantId: string, currentStatus: boolean) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`http://localhost:5001/api/admin/tenants/${tenantId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });
      if (res.ok) {
        fetchDashboardData();
      } else {
        alert('Failed to toggle status.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error toggling tenant status.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/login';
  };

  // Process chart data for PieChart
  const activeTenants = tenants.filter(t => t.is_active);
  const planDistribution = activeTenants.reduce((acc, t) => {
    acc[t.plan] = (acc[t.plan] || 0) + PLAN_PRICES[t.plan];
    return acc;
  }, {} as Record<string, number>);

  const chartData = Object.keys(PLAN_PRICES).map(plan => ({
    name: `${plan} Plan`,
    value: planDistribution[plan] || 0
  })).filter(item => item.value > 0);

  const formatCurrency = (val: number) => {
    return `₹${val.toLocaleString('en-IN')}`;
  };

  return (
    <div className="min-h-screen bg-[#070913] text-slate-200 font-sans flex">
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#0d1326] border-r border-white/10 p-4 flex flex-col justify-between shrink-0 min-h-screen">
        <div>
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Shield className="w-5 h-5 text-indigo-400" />
              SaaS Admin
            </h2>
            <button title="Refresh" onClick={fetchDashboardData} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 border border-white/10">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* User Badge */}
          <div className="bg-[#151c33] border border-white/10 rounded-xl p-3 mb-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm border border-indigo-500/30">
                🛡️
              </div>
              <div>
                <p className="text-xs font-bold text-slate-200">{authUser?.full_name || 'Super Admin'}</p>
                <span className="inline-block mt-0.5 px-2 py-0.5 text-[10px] font-bold text-indigo-300 bg-indigo-500/20 border border-indigo-500/30 rounded-md tracking-wider">
                  SUPER ADMIN
                </span>
              </div>
            </div>
          </div>

          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">Navigation</p>
          <nav className="space-y-1">
            <button 
              onClick={() => setActiveTab('overview')} 
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-left text-sm font-semibold transition-all ${activeTab === 'overview' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
            >
              📊 Platform Overview
            </button>
            <button 
              onClick={() => setActiveTab('manage')} 
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-left text-sm font-semibold transition-all ${activeTab === 'manage' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
            >
              🏢 Manage Tenants
            </button>
            <button 
              onClick={() => setActiveTab('create')} 
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-left text-sm font-semibold transition-all ${activeTab === 'create' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
            >
              ➕ Register Tenant
            </button>
          </nav>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 p-6 overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 tracking-tight">
              ⚙️ SaaS Portal Management
            </h1>
            <p className="text-xs text-slate-400 mt-1">Configure registered client organisations, billings and feature limits.</p>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl mb-6 font-semibold flex items-center gap-2">
            ❌ {error}
          </div>
        )}

        {isLoading ? (
          <div className="h-64 flex items-center justify-center text-slate-400 text-sm font-semibold">
            <Activity className="w-5 h-5 animate-spin text-indigo-400 mr-2" /> Loading platform records...
          </div>
        ) : (
          <>
            {/* TAB 1: OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* 3 Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#0f1629] p-6 rounded-2xl border border-white/10 shadow-sm">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4 text-indigo-400" /> Platform Monthly Revenue
                    </p>
                    <h3 className="text-3xl font-black text-slate-100">{formatCurrency(stats.total_mrr)}</h3>
                  </div>

                  <div className="bg-[#0f1629] p-6 rounded-2xl border border-white/10 shadow-sm">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Building2 className="w-4 h-4 text-indigo-400" /> Active Subscriptions
                    </p>
                    <h3 className="text-3xl font-black text-slate-100">{stats.active_subscriptions}</h3>
                  </div>

                  <div className="bg-[#0f1629] p-6 rounded-2xl border border-white/10 shadow-sm">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Users className="w-4 h-4 text-indigo-400" /> Total Platform Users
                    </p>
                    <h3 className="text-3xl font-black text-slate-100">{stats.total_users}</h3>
                  </div>
                </div>

                {/* Plan Distribution Chart */}
                <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl max-w-2xl">
                  <h3 className="text-sm font-bold text-slate-200 mb-6">Plan Revenue Breakdown</h3>
                  <div className="h-64 w-full flex items-center justify-center relative">
                    {chartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={85}
                            paddingAngle={4}
                            dataKey="value"
                            stroke="none"
                          >
                            {chartData.map((entry, index) => {
                              const planKey = entry.name.split(' ')[0];
                              return <Cell key={`cell-${index}`} fill={PLAN_COLORS[planKey] || '#6366f1'} />;
                            })}
                          </Pie>
                          <RechartsTooltip 
                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f1f5f9' }}
                            formatter={(value: number) => formatCurrency(value)}
                          />
                          <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '11px' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-slate-400 text-xs">No active plans data.</div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: MANAGE TENANTS */}
            {activeTab === 'manage' && (
              <div className="space-y-3">
                <h2 className="text-lg font-bold text-slate-100 mb-4">All Registered Tenants</h2>

                {tenants.length === 0 ? (
                  <div className="bg-[#0f1629] border border-white/10 rounded-xl p-4 text-xs text-slate-400">
                    No tenants registered yet.
                  </div>
                ) : tenants.map(t => {
                  const isOpen = expandedTenantId === t.id;
                  const isEditing = editingTenantId === t.id;
                  const statusLabel = t.is_active ? '🟢 Active' : '🔴 Suspended';

                  return (
                    <div key={t.id} className="bg-[#0f1629] border border-white/10 rounded-xl overflow-hidden shadow-lg">
                      {/* Accordion Header */}
                      <button
                        className="w-full flex items-center justify-between px-5 py-3.5 text-left hover:bg-white/[0.02] transition-colors"
                        onClick={() => {
                          setExpandedTenantId(isOpen ? null : t.id);
                          if (!isOpen) {
                            setEditingTenantId(null);
                          }
                        }}
                      >
                        <span className="text-sm font-semibold text-slate-200">
                          {t.name} <span className="text-slate-400 font-normal">({t.slug})</span>{' '}
                          <span className="text-slate-500 mx-1">—</span>{' '}
                          <span className="font-bold" style={{ color: PLAN_COLORS[t.plan] || '#6366f1' }}>{t.plan}</span>{' '}
                          <span className="text-slate-500 mx-1">|</span>{' '}
                          <span className={t.is_active ? 'text-emerald-400' : 'text-rose-400'}>{statusLabel}</span>
                        </span>
                        <span className={`text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>▾</span>
                      </button>

                      {/* Accordion Body */}
                      {isOpen && (
                        <div className="border-t border-white/10 px-5 py-5">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                            {/* LEFT: Tenant Details */}
                            <div className="space-y-2">
                              <p className="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-3">Tenant Details</p>
                              <div className="space-y-2 text-xs text-slate-300">
                                <div>
                                  <span className="text-slate-500">ID: </span>
                                  <code className="font-mono text-indigo-300 text-[11px]">{t.id}</code>
                                </div>
                                <div>
                                  <span className="text-slate-500">Current Plan: </span>
                                  <span className="font-bold" style={{ color: PLAN_COLORS[t.plan] || '#6366f1' }}>{t.plan}</span>
                                </div>
                                <div>
                                  <span className="text-slate-500">Access: </span>
                                  <span className="text-slate-400">Login via Main Portal (</span>
                                  <a href={`http://${t.slug}.localhost:3000/`} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">
                                    Live Link
                                  </a>
                                  <span className="text-slate-400">)</span>
                                </div>
                                <div>
                                  <span className="text-slate-500">Created At: </span>
                                  <code className="font-mono text-amber-300 text-[11px]">{(t as any).created_at || '—'}</code>
                                </div>
                                <div>
                                  <span className="text-slate-500">Active Client Accounts: </span>
                                  <span className="font-semibold text-slate-200">{(t as any).client_count ?? 0}</span>
                                </div>
                              </div>

                              {/* Tenant Active — toggle switch */}
                              <div className="pt-4">
                                <label className="flex items-center gap-3 cursor-pointer">
                                  <div className="relative">
                                    <input
                                      type="checkbox"
                                      className="sr-only peer"
                                      checked={isEditing ? editStatus : t.is_active}
                                      onChange={(e) => {
                                        if (!isEditing) {
                                          setEditingTenantId(t.id);
                                          setEditPlan(t.plan);
                                          setEditFeatures([...t.features]);
                                        }
                                        setEditStatus(e.target.checked);
                                      }}
                                    />
                                    <div className="w-9 h-5 bg-slate-700 rounded-full peer peer-checked:bg-indigo-600 transition-colors"></div>
                                    <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-4"></div>
                                  </div>
                                  <span className="text-xs font-semibold text-slate-200">Tenant Active</span>
                                </label>
                              </div>
                            </div>

                            {/* RIGHT: Plan & Features */}
                            <div className="space-y-4">
                              <p className="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-3">Plan & Features</p>

                              {/* Plan Level Select */}
                              <div>
                                <label className="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 tracking-wider">Plan Level</label>
                                <select
                                  value={isEditing ? editPlan : t.plan}
                                  onChange={(e) => {
                                    if (!isEditing) {
                                      setEditingTenantId(t.id);
                                      setEditStatus(t.is_active);
                                    }
                                    setEditPlan(e.target.value);
                                    setEditFeatures(PLAN_DEFAULTS[e.target.value] || []);
                                  }}
                                  className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                >
                                  <option value="Bronze">Bronze</option>
                                  <option value="Silver">Silver</option>
                                  <option value="Gold">Gold</option>
                                </select>
                              </div>

                              {/* Configure Features — chip style multiselect */}
                              <div>
                                <label className="block text-[11px] font-bold text-slate-500 uppercase mb-2 tracking-wider">Configure Features</label>
                                {/* Selected chips */}
                                <div className="flex flex-wrap gap-1.5 p-2.5 bg-[#151c33] border border-white/10 rounded-xl min-h-[42px]">
                                  {(() => {
                                    const currentFeatures = isEditing ? editFeatures : t.features;
                                    const selectedEntries = Object.entries(FEATURES_MAP).filter(([, v]) => currentFeatures.includes(v));
                                    const unselectedEntries = Object.entries(FEATURES_MAP).filter(([, v]) => !currentFeatures.includes(v));
                                    return (
                                      <>
                                        {selectedEntries.map(([label, value]) => (
                                          <button
                                            key={value}
                                            type="button"
                                            onClick={() => {
                                              if (!isEditing) {
                                                setEditingTenantId(t.id);
                                                setEditPlan(t.plan);
                                                setEditStatus(t.is_active);
                                                setEditFeatures(t.features.filter((f: string) => f !== value));
                                              } else {
                                                setEditFeatures(prev => prev.filter(f => f !== value));
                                              }
                                            }}
                                            className="flex items-center gap-1 px-2.5 py-1 bg-indigo-600/30 border border-indigo-500/40 text-indigo-200 rounded-lg text-[11px] font-semibold hover:bg-rose-500/20 hover:border-rose-500/30 hover:text-rose-300 transition-colors group"
                                          >
                                            {label}
                                            <span className="opacity-60 group-hover:opacity-100 ml-0.5">×</span>
                                          </button>
                                        ))}
                                        {selectedEntries.length === 0 && (
                                          <span className="text-slate-500 text-[11px] px-1">No features selected</span>
                                        )}
                                      </>
                                    );
                                  })()}
                                </div>
                                {/* Add features from unselected */}
                                {(() => {
                                  const currentFeatures = isEditing ? editFeatures : t.features;
                                  const unselectedEntries = Object.entries(FEATURES_MAP).filter(([, v]) => !currentFeatures.includes(v));
                                  if (unselectedEntries.length === 0) return null;
                                  return (
                                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                                      {unselectedEntries.map(([label, value]) => (
                                        <button
                                          key={value}
                                          type="button"
                                          onClick={() => {
                                            if (!isEditing) {
                                              setEditingTenantId(t.id);
                                              setEditPlan(t.plan);
                                              setEditStatus(t.is_active);
                                              setEditFeatures([...t.features, value]);
                                            } else {
                                              setEditFeatures(prev => [...prev, value]);
                                            }
                                          }}
                                          className="flex items-center gap-1 px-2.5 py-1 bg-white/5 border border-white/10 text-slate-500 rounded-lg text-[11px] font-semibold hover:bg-indigo-600/20 hover:text-indigo-300 hover:border-indigo-500/30 transition-colors"
                                        >
                                          + {label}
                                        </button>
                                      ))}
                                    </div>
                                  );
                                })()}
                              </div>
                            </div>
                          </div>

                          {/* Save Button */}
                          <div className="mt-5 pt-4 border-t border-white/10">
                            <button
                              onClick={() => handleUpdateTenant(t.id)}
                              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30"
                            >
                              💾 Save Changes
                            </button>
                            {isEditing && (
                              <button
                                onClick={() => { setEditingTenantId(null); }}
                                className="ml-2 px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 font-bold text-xs transition-all border border-white/10"
                              >
                                Cancel
                              </button>
                            )}
                          </div>
                        </div>
                      )}

                    </div>
                  );
                })}
              </div>
            )}

            {/* TAB 3: CREATE TENANT */}
            {activeTab === 'create' && (
              <div className="space-y-6 max-w-4xl">
                <h2 className="text-lg font-bold text-slate-100">Register New Tenant environment</h2>
                
                <form onSubmit={handleCreateTenant} className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl space-y-6 shadow-2xl">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    {/* Organization details */}
                    <div className="space-y-4">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">🏢 Tenant Details</h3>
                      
                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Tenant Organization Name *</label>
                        <input 
                          type="text" 
                          required
                          value={tenantName}
                          onChange={(e) => setTenantName(e.target.value)}
                          placeholder="e.g. Hooli Inc."
                          className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Unique URL/Slug *</label>
                        <input 
                          type="text" 
                          required
                          value={tenantSlug}
                          onChange={(e) => {
                            setTenantSlug(e.target.value.toLowerCase().replace(/[^a-z0-9_\-]/g, ''));
                          }}
                          placeholder="e.g. hooli"
                          className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono" 
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Plan Level *</label>
                        <select 
                          value={tenantPlan}
                          onChange={(e) => {
                            setTenantPlan(e.target.value);
                            setSelectedFeatures(PLAN_DEFAULTS[e.target.value]);
                          }}
                          className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                        >
                          <option value="Bronze">Bronze (₹2,999/mo)</option>
                          <option value="Silver">Silver (₹4,999/mo)</option>
                          <option value="Gold">Gold (₹9,999/mo)</option>
                        </select>
                      </div>

                      <div className="pt-2">
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-2 tracking-wider">Enable Features *</label>
                        <div className="grid grid-cols-2 gap-3">
                          {Object.entries(FEATURES_MAP).map(([label, value]) => (
                            <label key={value} className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-200">
                              <input 
                                type="checkbox" 
                                checked={selectedFeatures.includes(value)} 
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedFeatures(prev => [...prev, value]);
                                  } else {
                                    setSelectedFeatures(prev => prev.filter(f => f !== value));
                                  }
                                }}
                                className="w-4 h-4 rounded border-white/20 bg-[#151c33] text-indigo-600 focus:ring-0" 
                              />
                              {label}
                            </label>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Admin Account details */}
                    <div className="space-y-4">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">👤 Admin Account</h3>
                      
                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Admin Full Name *</label>
                        <input 
                          type="text" 
                          required
                          value={adminName}
                          onChange={(e) => setAdminName(e.target.value)}
                          placeholder="e.g. Richard Hendricks"
                          className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Admin Username *</label>
                        <input 
                          type="text" 
                          required
                          value={adminUser}
                          onChange={(e) => setAdminUser(e.target.value)}
                          placeholder="e.g. richard_h"
                          className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-400 uppercase mb-1.5 tracking-wider">Admin Password *</label>
                        <div className="relative">
                          <input 
                            type={showPassword ? 'text' : 'password'} 
                            required
                            value={adminPass}
                            onChange={(e) => setAdminPass(e.target.value)}
                            placeholder="Enter password"
                            className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 pr-10" 
                          />
                          <button 
                            type="button" 
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-200"
                          >
                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>

                  </div>

                  <div className="pt-2">
                    <button 
                      type="submit"
                      className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30"
                    >
                      🚀 Register Tenant & Create Admin
                    </button>
                  </div>
                </form>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
