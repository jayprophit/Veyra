/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { lazy, Suspense, useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Plus } from "lucide-react";

// Components
import { VeyraTradingDashboard } from "./components/VeyraTradingDashboard";
import { VeyraAssetTicker } from "./components/VeyraAssetTicker";
import { VeyraSidebar } from "./components/VeyraSidebar";
import { VeyraHeader } from "./components/VeyraHeader";
import { VeyraOnboarding } from "./components/VeyraOnboarding";
import { CurrencyProvider } from "./context/CurrencyContext";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { VeyraAuth } from "./components/VeyraAuth";
import { ThemeProvider } from "./context/ThemeContext";

type ViewType = "dashboard" | "markets" | "trading" | "portfolio" | "research" | "diagnostics" | "account" | "support" | "legal" | "onboarding" | "404";

const VeyraNotFound = lazy(() => import("./components/VeyraNotFound").then((module) => ({ default: module.VeyraNotFound })));
const VeyraFinanceMarkets = lazy(() => import("./components/VeyraFinanceMarkets").then((module) => ({ default: module.VeyraFinanceMarkets })));
const VeyraPortfolio = lazy(() => import("./components/VeyraPortfolio").then((module) => ({ default: module.VeyraPortfolio })));
const VeyraSettings = lazy(() => import("./components/VeyraSettings").then((module) => ({ default: module.VeyraSettings })));
const VeyraTradingView = lazy(() => import("./components/VeyraTradingView").then((module) => ({ default: module.VeyraTradingView })));
const VeyraProjectStatus = lazy(() => import("./components/VeyraProjectStatus").then((module) => ({ default: module.VeyraProjectStatus })));
const VeyraSupport = lazy(() => import("./components/VeyraSupport").then((module) => ({ default: module.VeyraSupport })));
const VeyraLegal = lazy(() => import("./components/VeyraLegal").then((module) => ({ default: module.VeyraLegal })));
const VeyraDiagnostics = lazy(() => import("./components/VeyraDiagnostics").then((module) => ({ default: module.VeyraDiagnostics })));
const VeyraResearchReader = lazy(() => import("./components/VeyraResearchReader").then((module) => ({ default: module.VeyraResearchReader })));

export default function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <CurrencyProvider>
          <AppContent />
        </CurrencyProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [view, setView] = useState<ViewType>("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [onboardingVisible, setOnboardingVisible] = useState(false);
  const [newTransactionModal, setNewTransactionModal] = useState(false);
  const [txData, setTxData] = useState({ symbol: 'VRA', type: 'buy', quantity: '', price: '' });

  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('veyra-onboarding-seen');
    if (isAuthenticated && !hasSeenOnboarding) {
      setOnboardingVisible(true);
    }
  }, [isAuthenticated]);

  const completeOnboarding = () => {
    setOnboardingVisible(false);
    localStorage.setItem('veyra-onboarding-seen', 'true');
  };

  const handleCreateTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    // Logic for adding transaction would go here
    setNewTransactionModal(false);
  };

  if (!isAuthenticated) {
    return <VeyraAuth />;
  }

  if (view === "404") {
    return (
      <div className="relative">
        <Suspense fallback={<ViewFallback />}>
          <VeyraNotFound onReturn={() => setView("dashboard")} />
        </Suspense>
      </div>
    );
  }

  return (
    <CurrencyProvider>
      <div className="min-h-screen bg-[#050505] text-slate-100 font-sans selection:bg-indigo-500 selection:text-white flex overflow-hidden">
      <AnimatePresence>
        {onboardingVisible && (
          <VeyraOnboarding onComplete={completeOnboarding} />
        )}
      </AnimatePresence>
      {/* Sidebar Navigation */}
      <VeyraSidebar 
        currentView={view} 
        onViewChange={setView} 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)} 
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden group">
        <VeyraHeader 
          onMenuToggle={() => setSidebarOpen(true)} 
          onViewChange={setView}
          currentView={view}
        />

        {/* Content Scroll Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-12 custom-scrollbar relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, scale: 0.98, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 1.02, y: -10 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="max-w-7xl mx-auto"
            >
              <Suspense fallback={<ViewFallback />}>
                {view === "dashboard" && (
                  <div className="space-y-12">
                       <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-8 border-b border-white/5">
                          <div>
                             <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic mb-4 uppercase text-transparent bg-clip-text bg-gradient-to-br from-white via-white to-white/20">Market_Hub</h2>
                             <p className="text-slate-500 text-lg md:text-xl font-medium tracking-tight">Private local-first market overview.</p>
                          </div>
                          <div className="flex gap-3">
                             <button 
                               onClick={() => setNewTransactionModal(true)}
                               className="px-6 py-3 bg-white text-black rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-200 transition-colors shadow-xl"
                             >
                               New Transaction
                             </button>
                             <button 
                               onClick={() => setNewTransactionModal(true)}
                               className="p-3 bg-white/5 border border-white/10 rounded-2xl text-white hover:bg-white/10 transition-colors"
                             >
                                <Plus size={20} />
                             </button>
                          </div>
                       </div>
                     <VeyraTradingDashboard />
                     <VeyraProjectStatus />
                     <VeyraAssetTicker />
                  </div>
                )}

                {view === "markets" && (
                  <div className="space-y-12">
                    <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic mb-4 uppercase text-white">Global_Assets</h2>
                    <VeyraFinanceMarkets />
                  </div>
                )}

                {view === "trading" && (
                  <div className="space-y-12">
                     <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic mb-4 uppercase text-white">Execution_Engine</h2>
                     <VeyraTradingView />
                  </div>
                )}

                {view === "portfolio" && (
                  <div className="space-y-12">
                    <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic mb-4 uppercase text-white">My_Holdings</h2>
                    <VeyraPortfolio />
                  </div>
                )}

                {view === "research" && (
                  <div className="space-y-12">
                    <div>
                      <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic mb-4 uppercase text-white">Research_Lab</h2>
                      <p className="text-slate-500 text-lg md:text-xl font-medium tracking-tight">
                        Crawl sources, paginate readable text, and summarize pages with local AI.
                      </p>
                    </div>
                    <VeyraResearchReader />
                  </div>
                )}

                {view === "support" && <VeyraSupport />}
                {view === "legal" && <VeyraLegal />}

                {view === "account" && <VeyraSettings />}
                {view === "diagnostics" && <VeyraDiagnostics />}
                {view === "onboarding" && <VeyraOnboarding onComplete={() => setView("dashboard")} />}
              </Suspense>
            </motion.div>
          </AnimatePresence>
          
          <footer className="mt-32 pt-16 border-t border-white/5 pb-12 flex flex-col md:flex-row items-center justify-between gap-8">
             <div className="flex flex-col items-center md:items-start">
                <div className="flex items-center gap-3 mb-2">
                   <div className="w-6 h-6 bg-indigo-600 rounded flex items-center justify-center font-bold text-xs italic">V</div>
                   <span className="font-black text-xs uppercase tracking-widest">Veyra Foundation 0.1.0</span>
                </div>
                <p className="text-[10px] text-slate-700 font-mono font-bold uppercase tracking-[0.2em]">© 2026 JAYPROPHIT / PRIVATE FOUNDATION</p>
             </div>
             <div className="flex gap-8 text-[10px] font-black uppercase tracking-widest text-slate-600">
               <button onClick={() => setView("markets")} className="hover:text-white transition-colors">Markets</button>
               <button onClick={() => setView("portfolio")} className="hover:text-white transition-colors">Portfolio</button>
               <button onClick={() => setView("diagnostics")} className="hover:text-white transition-colors">Health</button>
               <button onClick={() => setView("legal")} className="hover:text-white transition-colors">Compliance</button>
               <button onClick={() => setView("support")} className="hover:text-white transition-colors">Support</button>
             </div>
          </footer>
        </main>
      </div>

      {/* New Transaction Modal */}
      <AnimatePresence>
        {newTransactionModal && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setNewTransactionModal(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-xl"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-10 overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-500" />
              
              <header className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                  <Plus size={16} className="text-indigo-400" />
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest italic">Trade_Initialization</span>
                </div>
                <h3 className="text-3xl font-black italic text-white uppercase tracking-tighter">Forge_New_Transaction</h3>
              </header>

              <form onSubmit={handleCreateTransaction} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Asset_Symbol</label>
                    <input 
                      type="text" 
                      value={txData.symbol}
                      onChange={e => setTxData({...txData, symbol: e.target.value.toUpperCase()})}
                      className="w-full bg-black border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic font-sans"
                      placeholder="VRA"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Transaction_Type</label>
                    <div className="flex bg-black border border-white/5 rounded-2xl p-1">
                      <button 
                        type="button"
                        onClick={() => setTxData({...txData, type: 'buy'})}
                        className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase transition-all ${txData.type === 'buy' ? 'bg-emerald-500 text-black' : 'text-slate-500 hover:text-white'}`}
                      >
                        BUY
                      </button>
                      <button 
                        type="button"
                        onClick={() => setTxData({...txData, type: 'sell'})}
                        className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase transition-all ${txData.type === 'sell' ? 'bg-rose-500 text-black' : 'text-slate-500 hover:text-white'}`}
                      >
                        SELL
                      </button>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Quantity</label>
                  <input 
                    type="number" 
                    value={txData.quantity}
                    onChange={e => setTxData({...txData, quantity: e.target.value})}
                    className="w-full bg-black border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic font-sans"
                    placeholder="0.00"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Execution_Price (USDT)</label>
                  <input 
                    type="number" 
                    value={txData.price}
                    onChange={e => setTxData({...txData, price: e.target.value})}
                    className="w-full bg-black border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic font-sans"
                    placeholder="0.00"
                  />
                </div>

                <div className="pt-4 flex gap-4">
                  <button 
                    type="button"
                    onClick={() => setNewTransactionModal(false)}
                    className="flex-1 py-4 border border-white/5 rounded-2xl text-[10px] font-black uppercase text-slate-500 hover:text-white hover:bg-white/5 transition-all"
                  >
                    Cancel_Request
                  </button>
                  <button 
                    type="submit"
                    className="flex-1 py-4 bg-white text-black rounded-2xl text-[10px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-2xl shadow-indigo-500/10"
                  >
                    Confirm_Transaction
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Background Decorative Elements */}
      <div className="fixed inset-0 pointer-events-none -z-10 bg-[radial-gradient(circle_at_top_right,_rgba(99,102,241,0.05)_0%,_transparent_50%)]"></div>
      <div className="fixed inset-0 pointer-events-none -z-10 bg-[conic-gradient(from_0deg_at_50%_50%,_transparent_0%,_rgba(99,102,241,0.02)_50%,_transparent_100%)] animate-[spin_20s_infinite_linear]"></div>
      
      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #374151; }
      `}} />
    </div>
    </CurrencyProvider>
  );
}

function ViewFallback() {
  return (
    <div className="min-h-[240px] flex items-center justify-center text-sm font-bold uppercase tracking-widest text-slate-600">
      Loading
    </div>
  );
}
