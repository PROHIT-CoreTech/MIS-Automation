import { BarChart3, ChevronRight, Lock, Key } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-[#090b14] text-slate-200 overflow-hidden font-sans selection:bg-indigo-500/30">
      
      {/* Floating Orbs (Background) */}
      <div className="fixed -top-[100px] -left-[100px] w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(99,102,241,0.12)_0%,transparent_70%)] pointer-events-none animate-[orbFloat_12s_ease-in-out_infinite] z-0" />
      <div className="fixed -bottom-[50px] -right-[50px] w-[450px] h-[450px] rounded-full bg-[radial-gradient(circle,rgba(249,115,22,0.08)_0%,transparent_70%)] pointer-events-none animate-[orbFloat_15s_ease-in-out_infinite_reverse] z-0" />
      
      {/* Navbar */}
      <nav className="relative z-10 w-full max-w-[1200px] mx-auto px-6 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-extrabold text-slate-100 tracking-tight">📊 MIS Portal</span>
        </div>
        <div className="flex items-center">
          <Link href="/login" className="flex items-center gap-2 bg-white/5 border border-white/10 text-slate-200 px-5 py-2.5 rounded-lg font-medium hover:bg-white/10 hover:text-white transition-all">
            <Key className="w-4 h-4" />
            Super Admin Access
          </Link>
        </div>
      </nav>

      {/* Main Content Container */}
      <div className="relative z-10 max-w-[1200px] mx-auto px-6 pb-20">
        
        {/* Hero Section */}
        <main className="flex flex-col items-center justify-center text-center pt-20 pb-10">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/25 px-4 py-1.5 rounded-full text-xs font-bold text-indigo-400 uppercase tracking-wider mb-6">
            <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
            Automated Tally Prime Sync
          </div>
          
          <h1 className="text-[clamp(34px,5vw,56px)] font-extrabold tracking-tight leading-[1.05] text-slate-50 mb-5">
            Automate your financial intelligence <br className="hidden md:block" />
            <span className="bg-gradient-to-br from-indigo-500 to-orange-500 bg-clip-text text-transparent">
              instantly
            </span>
          </h1>
          
          <p className="text-[clamp(16px,2.5vw,20px)] text-slate-400 max-w-[700px] mx-auto leading-[1.5] mb-9">
            Connect Tally Prime directly to a beautiful, interactive, and role-isolated dashboard. Deliver detailed MIS reports, P&L breakups, and ageing lists to clients automatically.
          </p>
        </main>

        <div className="h-[1px] w-full bg-white/10 my-10" />

        {/* Features Section */}
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-[2rem] font-extrabold text-slate-100 tracking-tight mb-8">Everything you need to automate reporting</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Feature Card 1 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">📈</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Live KPI Dashboards</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Track Revenue, Gross Profit, and Net Profit trends in real-time. Analyze performance using premium, multi-dimensional Plotly charts.</p>
          </div>
          {/* Feature Card 2 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">⚡</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Direct Tally Prime Sync</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Synchronize complete financial history, balance sheet segments, and age books securely using standard XML endpoints.</p>
          </div>
          {/* Feature Card 3 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">🔒</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Multi-Tenant Isolation</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Keep your client accounts separated. Client roles see only their assigned businesses, tables, and synced data history.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {/* Feature Card 4 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">📄</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Detailed MIS breakups</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Deep-dive into custom monthly breakups of P&L ledger details mapped automatically using ledgers configuration.</p>
          </div>
          {/* Feature Card 5 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">📅</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Customer & Vendor Ageing</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Monitor accounts receivables and payables overdue intervals instantly. Filter by customer names and age brackets.</p>
          </div>
          {/* Feature Card 6 */}
          <div className="bg-[#0f1629]/60 border border-white/5 rounded-[20px] p-7 backdrop-blur-md hover:border-indigo-500/30 hover:-translate-y-1 hover:shadow-[0_12px_30px_rgba(0,0,0,0.4)] transition-all duration-200">
            <div className="text-3xl mb-4">📥</div>
            <h3 className="text-[1.15rem] font-bold text-slate-100 mb-2.5">Excel & PowerPoint Exports</h3>
            <p className="text-[0.88rem] text-slate-400 leading-[1.45]">Export formatted financial spreadsheets or fully designed slide decks directly for your board meetings.</p>
          </div>
        </div>

        {/* Pricing Grid Section */}
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-[2rem] font-extrabold text-slate-100 tracking-tight mb-8">Flexible pricing plans</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 items-start">
          
          {/* Bronze Plan */}
          <div className="bg-[#0f1629]/85 bg-gradient-to-br from-white/[0.03] to-white/[0.005] border border-white/5 rounded-[24px] px-7 py-8 text-center backdrop-blur-md hover:border-indigo-500/40 hover:-translate-y-1 hover:shadow-[0_16px_40px_rgba(0,0,0,0.5)] transition-all duration-250">
            <div className="text-[1.1rem] font-bold text-slate-400 tracking-wider uppercase mb-3">Bronze Plan</div>
            <div className="text-[2.5rem] font-extrabold text-slate-50 mb-6">₹1,999<span className="text-[0.9rem] text-slate-500 font-medium">/mo</span></div>
            <ul className="text-left space-y-3 mb-6">
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 <b>Dashboard</b> page</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Basic P&L overview</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Format Excel exports</li>
              <li className="text-[0.88rem] text-slate-600 line-through flex items-center gap-2">🔴 PowerPoint Exports</li>
              <li className="text-[0.88rem] text-slate-600 line-through flex items-center gap-2">🔴 Cash Flow analysis</li>
              <li className="text-[0.88rem] text-slate-600 line-through flex items-center gap-2">🔴 Auto Tally Sync</li>
            </ul>
            <button className="w-full py-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-medium text-white">Choose Bronze</button>
          </div>

          {/* Silver Plan */}
          <div className="relative bg-[#0f1629]/85 bg-gradient-to-br from-white/[0.03] to-white/[0.005] border border-indigo-500/40 rounded-[24px] px-7 py-8 text-center backdrop-blur-md shadow-[0_8px_32px_rgba(99,102,241,0.1)] hover:-translate-y-1 hover:shadow-[0_16px_40px_rgba(0,0,0,0.5)] transition-all duration-250 overflow-hidden">
            <div className="absolute top-[18px] -right-[30px] bg-indigo-500 text-white text-[0.65rem] font-extrabold px-[30px] py-1 rotate-45 tracking-wider uppercase">POPULAR</div>
            <div className="text-[1.1rem] font-bold text-indigo-500 tracking-wider uppercase mb-3">Silver Plan</div>
            <div className="text-[2.5rem] font-extrabold text-slate-50 mb-6">₹4,999<span className="text-[0.9rem] text-slate-500 font-medium">/mo</span></div>
            <ul className="text-left space-y-3 mb-6">
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 <b>Dashboard & Reports</b></li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Detailed P&L breakup</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Customer & Vendor Ageing</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Excel & PPT downloads</li>
              <li className="text-[0.88rem] text-slate-600 line-through flex items-center gap-2">🔴 Cash Flow analysis</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Manual Tally Sync</li>
            </ul>
            <button className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition-colors font-medium text-white shadow-lg shadow-indigo-500/25">Choose Silver</button>
          </div>

          {/* Gold Plan */}
          <div className="bg-[#0f1629]/85 bg-gradient-to-br from-white/[0.03] to-white/[0.005] border border-white/5 rounded-[24px] px-7 py-8 text-center backdrop-blur-md hover:border-indigo-500/40 hover:-translate-y-1 hover:shadow-[0_16px_40px_rgba(0,0,0,0.5)] transition-all duration-250">
            <div className="text-[1.1rem] font-bold text-slate-400 tracking-wider uppercase mb-3">Gold Plan</div>
            <div className="text-[2.5rem] font-extrabold text-slate-50 mb-6">₹9,999<span className="text-[0.9rem] text-slate-500 font-medium">/mo</span></div>
            <ul className="text-left space-y-3 mb-6">
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 <b>All Features</b> enabled</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Dashboard & Reports</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Cash Flow dashboards</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Unlimited Tally Sync</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Premium client portals</li>
              <li className="text-[0.88rem] text-slate-300 flex items-center gap-2">🟢 Custom templates</li>
            </ul>
            <button className="w-full py-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-medium text-white">Choose Gold</button>
          </div>

        </div>

        <div className="h-[1px] w-full bg-white/10 mb-10" />

        {/* Footer */}
        <footer className="text-center text-[0.8rem] text-slate-600 pb-8">
          <p>© 2026 MIS Portal SaaS. Secured with AES-256 and bcrypt credentials hashing.</p>
          <p className="mt-2">Powering automated financial reports directly from Tally Prime ODBC configurations.</p>
        </footer>

      </div>

      <style>{`
        @keyframes orbFloat {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(30px, 40px) scale(1.05); }
        }
      `}</style>
    </div>
  );
}
