import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  ShieldCheck, 
  ArrowRight, 
  Cpu, 
  Lock, 
  User, 
  Mail, 
  Key,
  Globe,
  Zap,
  ChevronRight
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { VeyraLogo } from "./VeyraLogo";

export function VeyraAuth() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();

  // Form states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(name, username, email);
      }
    } catch (error) {
      console.error("Auth failed", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500 selection:text-white flex overflow-hidden font-sans">
      {/* Left Decorative/Branding Sidebar */}
      <div className="hidden lg:flex w-1/2 bg-zinc-950 border-r border-white/5 relative items-center justify-center p-20 overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-[-10%] left-[-10%] w-[120%] h-[120%] bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.15)_0,transparent_70%)] animate-pulse" />
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:40px_40px]" />
        </div>

        <div className="relative z-10 space-y-12">
          <header className="space-y-6">
            <VeyraLogo size="xl" />
            <h1 className="text-8xl font-black italic tracking-tighter uppercase leading-[0.8]">
              Veyra<br/><span className="text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-emerald-400">_LABS</span>
            </h1>
          </header>

          <div className="space-y-8 max-w-md">
            <p className="text-xl font-bold text-slate-500 uppercase italic tracking-widest leading-relaxed border-l-2 border-indigo-500/30 pl-8">
              THE PREMIER TERMINAL FOR HIGH-LATENCY PROTOCOL EXTRACTION AND NEURAL LIQUIDITY ANALYSIS.
            </p>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-6 bg-white/2 border border-white/5 rounded-3xl space-y-4">
                <Cpu size={24} className="text-indigo-400" />
                <h4 className="text-[10px] font-black uppercase text-white tracking-widest">Global_Sync</h4>
                <p className="text-[9px] text-slate-600 uppercase font-bold leading-relaxed">Connect to 12,000+ consensus nodes instantly.</p>
              </div>
              <div className="p-6 bg-white/2 border border-white/5 rounded-3xl space-y-4">
                <Globe size={24} className="text-emerald-400" />
                <h4 className="text-[10px] font-black uppercase text-white tracking-widest">Deep_Audit</h4>
                <p className="text-[9px] text-slate-600 uppercase font-bold leading-relaxed">System-wide verification on every protocol kernel.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-10 left-10 flex items-center gap-4">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-mono text-slate-700 uppercase tracking-widest font-black">Cluster_Status: NOMINAL</span>
        </div>
      </div>

      {/* Right Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-24 relative">
        {/* Mobile Logo */}
        <div className="lg:hidden absolute top-10 left-10 flex items-center gap-4">
          <VeyraLogo size="sm" />
          <span className="text-2xl font-black italic uppercase tracking-tighter">Veyra</span>
        </div>

        <div className="w-full max-w-lg space-y-12">
          <header>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest italic">{mode === 'login' ? 'Existing_Protocol_Member' : 'New_Kernel_Registration'}</span>
            </div>
            <h2 className="text-5xl font-black italic tracking-tighter uppercase text-white">
              {mode === 'login' ? 'Access_Terminal' : 'Initialize_Node'}
            </h2>
          </header>

          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-6">
              {mode === 'register' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Legal_Name</label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-700" size={16} />
                      <input 
                        type="text" 
                        required
                        placeholder="Jay Prophit"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        className="w-full bg-white/2 border border-white/5 rounded-2xl p-4 pl-12 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-800 italic"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">User_Handle</label>
                    <div className="relative">
                      <Zap className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-700" size={16} />
                      <input 
                        type="text" 
                        required
                        placeholder="@prophit_alpha"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        className="w-full bg-white/2 border border-white/5 rounded-2xl p-4 pl-12 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-800 italic"
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest pl-2">Email_Bridge</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-700" size={16} />
                  <input 
                    type="email" 
                    required
                    placeholder="operator@veyra.io"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full bg-white/2 border border-white/5 rounded-2xl p-4 pl-12 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-800 italic"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center px-2">
                  <label className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Access_Key</label>
                  {mode === 'login' && <button type="button" className="text-[9px] font-black text-slate-700 uppercase hover:text-indigo-400 transition-colors">Lapsed_Key?</button>}
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-700" size={16} />
                  <input 
                    type="password" 
                    required
                    placeholder="••••••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="w-full bg-white/2 border border-white/5 rounded-2xl p-4 pl-12 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-800 italic"
                  />
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-5 bg-white text-black rounded-[2rem] font-black uppercase text-xs tracking-[0.3em] hover:bg-slate-200 active:scale-95 transition-all shadow-2xl relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div 
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center justify-center gap-3"
                  >
                    <div className="w-2 h-2 rounded-full bg-black animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-2 h-2 rounded-full bg-black animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-2 h-2 rounded-full bg-black animate-bounce" />
                    <span>Synchronizing...</span>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="idle"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex justify-center items-center gap-4"
                  >
                    {mode === 'login' ? 'Initiate_Session' : 'Finalize_Node_Protocol'}
                    <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          </form>

          <footer className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-6">
            <button 
              onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
              className="group text-[10px] font-black text-slate-500 uppercase tracking-widest hover:text-white transition-colors"
            >
              {mode === 'login' ? (
                <>New_Here? <span className="text-indigo-400 group-hover:underline underline-offset-4 decoration-2">Create_Network_Node</span></>
              ) : (
                <>Already_Verified? <span className="text-indigo-400 group-hover:underline underline-offset-4 decoration-2">Login_Terminal</span></>
              )}
            </button>
            <div className="flex items-center gap-4">
              <span className="text-[10px] font-black text-slate-800 uppercase tracking-widest italic">Veyra_V12.4.1</span>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
