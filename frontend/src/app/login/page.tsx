'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }
    // In a real implementation, this would call the backend /api/auth/login
    // and store the JWT before routing. For now, we mock the routing:
    if (username === 'admin') {
      window.location.href = '/admin';
    } else {
      window.location.href = '/tenant/rohit_inc';
    }
  };

  return (
    <div className="relative min-h-screen bg-[#090b14] flex items-center justify-center overflow-hidden font-sans selection:bg-indigo-500/30">
      
      {/* Floating Orbs (Background) */}
      <div className="fixed -top-[140px] -left-[140px] w-[420px] h-[420px] rounded-full bg-[radial-gradient(circle,rgba(99,102,241,0.20)_0%,transparent_70%)] pointer-events-none animate-[orbFloat1_9s_ease-in-out_infinite] z-0" />
      <div className="fixed -bottom-[100px] -right-[100px] w-[380px] h-[380px] rounded-full bg-[radial-gradient(circle,rgba(249,115,22,0.16)_0%,transparent_70%)] pointer-events-none animate-[orbFloat2_11s_ease-in-out_infinite] z-0" />
      <div className="fixed top-[40%] left-[60%] w-[220px] h-[220px] rounded-full bg-[radial-gradient(circle,rgba(16,185,129,0.10)_0%,transparent_70%)] pointer-events-none animate-[orbFloat1_7s_ease-in-out_infinite_reverse] z-0" />

      <div className="relative z-10 w-full max-w-md px-6 flex flex-col items-center">
        
        {/* Header Texts */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-1.5 rounded-full text-xs font-bold text-slate-300 uppercase tracking-wider mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            MIS PORTAL · SECURE ACCESS
          </div>
          <h1 className="text-[clamp(30px,5vw,42px)] font-extrabold tracking-tight leading-[1.1] text-slate-100 mb-2">
            Welcome <span className="bg-gradient-to-br from-indigo-500 via-orange-500 to-emerald-500 bg-clip-text text-transparent">back</span>
          </h1>
          <p className="text-[0.91rem] text-slate-400">Sign in to your financial intelligence dashboard</p>
        </div>

        {/* Glassmorphism Form Card */}
        <div className="w-full bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 rounded-[28px] p-9 backdrop-blur-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_32px_80px_rgba(0,0,0,0.55),0_0_0_1px_rgba(99,102,241,0.15)] transform transition-transform hover:scale-[1.01] duration-300">
          <form onSubmit={handleLogin} className="space-y-5">
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl text-center font-medium">
                ❌ {error}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full bg-[#080c16]/60 border border-white/10 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full bg-[#080c16]/60 border border-white/10 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all"
              />
            </div>
            <button 
              type="submit"
              className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-xl transition-colors shadow-lg shadow-indigo-500/25"
            >
              Sign In
            </button>
          </form>
        </div>

        <Link href="/" className="mt-6 w-full text-center py-3 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-slate-300 text-sm font-medium transition-colors">
          ⬅ Back to Home
        </Link>

        <p className="mt-5 text-center text-[#334155] text-[0.70rem] tracking-[0.06em] uppercase">
          Secured · Role-based access · Encrypted
        </p>

      </div>

      <style>{`
        @keyframes orbFloat1 {
          0%, 100% { transform: translate(0,0) scale(1); }
          50%       { transform: translate(40px, 30px) scale(1.1); }
        }
        @keyframes orbFloat2 {
          0%, 100% { transform: translate(0,0) scale(1); }
          50%       { transform: translate(-30px,-25px) scale(1.08); }
        }
      `}</style>
    </div>
  );
}
