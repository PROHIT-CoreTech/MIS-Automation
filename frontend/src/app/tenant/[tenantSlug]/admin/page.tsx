'use client';

import React, { useState, useEffect } from 'react';
import { use } from 'react';
import Link from 'next/link';
import { 
  PieChart as PieChartIcon, Settings, Users, Plus, Key, Eye, EyeOff, 
  RotateCcw, RefreshCw, ChevronDown, CheckCircle2, Lock, Trash2, Shield
} from 'lucide-react';

interface ClientUser {
  _id: string;
  username: string;
  full_name: string;
  role: string;
  can_download_excel: boolean;
  can_download_ppt: boolean;
  is_active: boolean;
  companies: any[];
  tenant?: string;
}

interface Company {
  _id: string;
  tally_name: string;
  display_name?: string;
}

export default function TenantAdminPage({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const resolvedParams = use(params);
  const tenantSlug = resolvedParams.tenantSlug;

  const [activeTab, setActiveTab] = useState<'manage' | 'create' | 'permissions'>('manage');
  
  // Form states
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [canExcel, setCanExcel] = useState(true);
  const [canPPT, setCanPPT] = useState(false);

  // Clients and Companies List
  const [clients, setClients] = useState<ClientUser[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tenantId, setTenantId] = useState<string | null>(null);

  // Selected client for permissions tab
  const [permSelectedClient, setPermSelectedClient] = useState<string>('');
  const [permCanExcel, setPermCanExcel] = useState(true);
  const [permCanPPT, setPermCanPPT] = useState(false);

  const [showSettings, setShowSettings] = useState(false);

  // Auth User state
  const [authUser, setAuthUser] = useState<{ username: string; full_name: string; role: string } | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (!storedToken || !userStr) {
      window.location.href = '/login';
      return;
    }
    try {
      const parsedUser = JSON.parse(userStr);
      setAuthUser(parsedUser);
      setToken(storedToken);
    } catch (e) {
      window.location.href = '/login';
      return;
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchTenantData();
    }
  }, [token, tenantSlug]);

  const fetchTenantData = async () => {
    setIsLoading(true);
    try {
      // First, get dashboard data to find the tenant ID
      const dashRes = await fetch('http://localhost:5001/api/admin/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (dashRes.ok) {
        const dashData = await dashRes.json();
        const tenant = (dashData.tenants || []).find((t: any) => t.slug === tenantSlug);
        if (tenant) {
          setTenantId(tenant.id);
          // Fetch users for this tenant
          await fetchTenantUsers(tenant.id);
          await fetchTenantCompanies(tenant.id);
        }
      }
    } catch (err) {
      console.error('Error fetching tenant data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTenantUsers = async (tid: string) => {
    try {
      const res = await fetch(`http://localhost:5001/api/admin/tenants/${tid}/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        // Filter only client/user roles (not admins)
        const clientUsers = data.filter((u: ClientUser) => u.role === 'client' || u.role === 'user');
        setClients(clientUsers);
      }
    } catch (err) {
      console.error('Error fetching tenant users:', err);
    }
  };

  const fetchTenantCompanies = async (tid: string) => {
    try {
      const res = await fetch(`http://localhost:5001/api/admin/tenants/${tid}/companies`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCompanies(data);
      }
    } catch (err) {
      console.error('Error fetching tenant companies:', err);
    }
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !username || !password) {
      alert('Please fill in all required fields (*)');
      return;
    }
    if (!tenantId) {
      alert('Tenant not found. Please refresh.');
      return;
    }

    try {
      const res = await fetch('http://localhost:5001/api/admin/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          username,
          password,
          full_name: fullName,
          role: 'client',
          tenantId,
          companies: selectedCompany ? [selectedCompany] : [],
          can_download_excel: canExcel,
          can_download_ppt: canPPT
        })
      });
      if (res.ok) {
        alert(`Client ${username} created successfully!`);
        setFullName('');
        setUsername('');
        setPassword('');
        setSelectedCompany('');
        setActiveTab('manage');
        if (tenantId) await fetchTenantUsers(tenantId);
      } else {
        const errData = await res.json();
        alert(`Error: ${errData.error || 'Failed to create client'}`);
      }
    } catch (err) {
      console.error(err);
      alert('Network error creating client.');
    }
  };

  const handleUpdatePermissions = async () => {
    if (!permSelectedClient) return;
    try {
      const res = await fetch(`http://localhost:5001/api/admin/users/${permSelectedClient}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          can_download_excel: permCanExcel,
          can_download_ppt: permCanPPT
        })
      });
      if (res.ok) {
        alert('Permissions updated successfully!');
        if (tenantId) await fetchTenantUsers(tenantId);
      } else {
        alert('Failed to update permissions.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error updating permissions.');
    }
  };

  const handleDeleteClient = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this client?')) return;
    try {
      const res = await fetch(`http://localhost:5001/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setClients(prev => prev.filter(c => c._id !== userId));
      } else {
        alert('Failed to delete client.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error deleting client.');
    }
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
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm border border-indigo-500/30">
                  👤
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">{authUser?.full_name || 'Admin'}</p>
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
              ⚙️ Admin Panel
            </h1>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold transition-colors cursor-pointer"
          >
            🚪 Logout
          </button>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex border-b border-white/10 mb-6 gap-2">
          <button 
            onClick={() => setActiveTab('manage')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'manage' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            👥 Client Management
          </button>
          <button 
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'create' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            ➕ Create Client
          </button>
          <button 
            onClick={() => setActiveTab('permissions')}
            className={`flex items-center gap-2 px-4 py-2.5 font-bold text-xs rounded-t-xl transition-all border-t border-x ${activeTab === 'permissions' ? 'bg-[#0f1629] text-indigo-400 border-white/10 border-b-[#0f1629]' : 'text-slate-400 hover:text-slate-200 border-transparent'}`}
          >
            🔑 Permissions
          </button>
        </div>

        {/* TAB 1: CLIENT MANAGEMENT */}
        {activeTab === 'manage' && (
          <div className="space-y-4">
            <h2 className="text-xl font-extrabold text-slate-100 mb-4">All Clients</h2>

            {isLoading ? (
              <div className="bg-[#15233c] border border-white/10 rounded-xl p-4 text-xs font-semibold text-slate-300">Loading clients...</div>
            ) : clients.length === 0 ? (
              <div className="bg-[#15233c] border border-white/10 rounded-xl p-4 text-xs font-semibold text-slate-300">
                No clients yet. Create one in the &apos;Create Client&apos; tab.
              </div>
            ) : (
              <div className="bg-[#0f1629] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                <table className="w-full text-left text-xs text-slate-300 border-collapse">
                  <thead className="bg-[#151c33] text-slate-400 uppercase text-[10px] font-bold border-b border-white/10">
                    <tr>
                      <th className="px-4 py-3">Full Name</th>
                      <th className="px-4 py-3">Username</th>
                      <th className="px-4 py-3">Assigned Companies</th>
                      <th className="px-3 py-3 text-center">Excel Access</th>
                      <th className="px-3 py-3 text-center">PPT Access</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 font-sans">
                    {clients.map((c) => (
                      <tr key={c._id} className="hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3 font-semibold text-slate-200">{c.full_name}</td>
                        <td className="px-4 py-3 font-mono text-indigo-300">{c.username}</td>
                        <td className="px-4 py-3 text-slate-400">
                          {c.companies && c.companies.length ? c.companies.map((comp: any) => typeof comp === 'string' ? comp : comp.display_name || comp.tally_name).join(', ') : '—'}
                        </td>
                        <td className="px-3 py-3 text-center font-bold">
                          {c.can_download_excel ? <span className="text-emerald-400">✅ Yes</span> : <span className="text-rose-400">❌ No</span>}
                        </td>
                        <td className="px-3 py-3 text-center font-bold">
                          {c.can_download_ppt ? <span className="text-emerald-400">✅ Yes</span> : <span className="text-rose-400">❌ No</span>}
                        </td>
                        <td className="px-4 py-3 text-right space-x-2">
                          <button onClick={() => handleDeleteClient(c._id)} className="text-rose-400 hover:text-rose-300 p-1">
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: CREATE CLIENT */}
        {activeTab === 'create' && (
          <div className="space-y-6 max-w-4xl">
            <h2 className="text-xl font-extrabold text-slate-100 mb-4">Create New Client</h2>

            <form onSubmit={handleCreateClient} className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl space-y-6 shadow-2xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Left Column: Personal & Credentials */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">FULL NAME *</label>
                    <input 
                      type="text" 
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">USERNAME *</label>
                    <input 
                      type="text" 
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">PASSWORD *</label>
                    <div className="relative">
                      <input 
                        type={showPassword ? 'text' : 'password'} 
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
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

                {/* Right Column: Company Assignment & Permissions */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">Assign Company</label>
                    <select 
                      value={selectedCompany}
                      onChange={(e) => setSelectedCompany(e.target.value)}
                      className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                    >
                      <option value="">Choose an option</option>
                      {companies.map((c) => (
                        <option key={c._id} value={c._id}>{c.display_name || c.tally_name}</option>
                      ))}
                      {companies.length === 0 && (
                        <option value="" disabled>No companies found for this tenant</option>
                      )}
                    </select>
                  </div>

                  <div className="pt-2 space-y-3">
                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-200">
                      <input 
                        type="checkbox" 
                        checked={canExcel} 
                        onChange={(e) => setCanExcel(e.target.checked)}
                        className="w-4 h-4 rounded border-white/20 bg-[#151c33] text-indigo-600 focus:ring-0" 
                      />
                      Excel Download
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-200">
                      <input 
                        type="checkbox" 
                        checked={canPPT} 
                        onChange={(e) => setCanPPT(e.target.checked)}
                        className="w-4 h-4 rounded border-white/20 bg-[#151c33] text-indigo-600 focus:ring-0" 
                      />
                      PPT Download
                    </label>
                  </div>
                </div>

              </div>

              <div>
                <button 
                  type="submit"
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30"
                >
                  Create Client
                </button>
              </div>
            </form>
          </div>
        )}

        {/* TAB 3: PERMISSIONS */}
        {activeTab === 'permissions' && (
          <div className="space-y-6 max-w-3xl">
            <h2 className="text-xl font-extrabold text-slate-100 mb-4">Update Client Permissions</h2>

            {clients.length === 0 ? (
              <div className="bg-[#15233c] border border-white/10 rounded-xl p-4 text-xs font-semibold text-slate-300">
                No clients yet.
              </div>
            ) : (
              <div className="bg-[#0f1629] border border-white/10 p-6 rounded-2xl space-y-4 shadow-2xl">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1.5">Select Client</label>
                  <select 
                    value={permSelectedClient} 
                    onChange={(e) => {
                      setPermSelectedClient(e.target.value);
                      const target = clients.find(c => c._id === e.target.value);
                      if (target) {
                        setPermCanExcel(target.can_download_excel);
                        setPermCanPPT(target.can_download_ppt);
                      }
                    }}
                    className="w-full bg-[#151c33] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                  >
                    <option value="">Choose a client...</option>
                    {clients.map(c => (
                      <option key={c._id} value={c._id}>{c.full_name} ({c.username})</option>
                    ))}
                  </select>
                </div>

                <div className="pt-2 space-y-3">
                  <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-200">
                    <input 
                      type="checkbox" 
                      checked={permCanExcel} 
                      onChange={(e) => setPermCanExcel(e.target.checked)}
                      className="w-4 h-4 rounded border-white/20 bg-[#151c33] text-indigo-600 focus:ring-0" 
                    />
                    Excel Download Permission
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-200">
                    <input 
                      type="checkbox" 
                      checked={permCanPPT} 
                      onChange={(e) => setPermCanPPT(e.target.checked)}
                      className="w-4 h-4 rounded border-white/20 bg-[#151c33] text-indigo-600 focus:ring-0" 
                    />
                    PPT Download Permission
                  </label>
                </div>

                <button 
                  onClick={handleUpdatePermissions}
                  disabled={!permSelectedClient}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/30 mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Update Permissions
                </button>
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}
