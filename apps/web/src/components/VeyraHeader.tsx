/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { 
  Bell, 
  Search, 
  Menu, 
  User, 
  Zap, 
  ShieldCheck, 
  Layers, 
  Command,
  Layout,
  Cpu,
  ChevronRight,
  ChevronDown,
  Settings,
  Globe,
  Check,
  Moon,
  Sun,
  Palette,
  Camera,
  Upload
} from "lucide-react";
import { useState, useEffect, useRef, MouseEvent, ChangeEvent } from "react";
import { useCurrency, currencies } from "../context/CurrencyContext";
import { useTheme, ThemeType } from "../context/ThemeContext";

import { useAuth } from "../context/AuthContext";
import { VeyraLogo } from "./VeyraLogo";

interface HeaderProps {
  onMenuToggle: () => void;
  onViewChange: (view: any) => void;
  currentView: string;
}

export function VeyraHeader({ onMenuToggle, onViewChange, currentView }: HeaderProps) {
  const { user, logout, updateUser } = useAuth();
  const { theme, setTheme } = useTheme();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [currencyOpen, setCurrencyOpen] = useState(false);
  const [themeOpen, setThemeOpen] = useState(false);
  const { selectedCurrency, setSelectedCurrency } = useCurrency();

  const handleAvatarClick = (e: MouseEvent) => {
    e.stopPropagation();
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        updateUser({ avatar: reader.result as string });
      };
      reader.readAsDataURL(file);
    }
  };

  const themes: { id: ThemeType; label: string; icon: any }[] = [
    { id: 'dark', label: 'Dark Protocol', icon: Moon },
    { id: 'light', label: 'Light Grid', icon: Sun },
    { id: 'neutral', label: 'Neutral Silk', icon: Palette },
    { id: 'cyber', label: 'Cyber Neon', icon: Zap },
  ];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
      if (e.key === 'Escape') setIsSearchOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const searchResults = [
    { id: "dashboard", label: "Overview", group: "Foundation" },
    { id: "markets", label: "Market Data", group: "Foundation" },
    { id: "trading", label: "Paper Trading", group: "Execution" },
    { id: "portfolio", label: "Portfolio", group: "Foundation" },
    { id: "diagnostics", label: "Health Checks", group: "Operations" },
    { id: "account", label: "Account Settings", group: "System" },
    { id: "support", label: "Knowledge Base", group: "Help" },
    { id: "legal", label: "Risk Notes", group: "Legal" },
  ].filter(r => r.label.toLowerCase().includes(searchValue.toLowerCase()));

  return (
    <>
      <header className="h-20 border-b border-white/5 bg-black/50 backdrop-blur-3xl sticky top-0 z-50 flex items-center justify-between px-6 md:px-12">
        <div className="flex items-center gap-6">
          <button 
            onClick={onMenuToggle}
            className="lg:hidden p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors"
          >
            <Menu size={20} />
          </button>
          
          <div className="hidden lg:flex items-center gap-4 bg-white/5 border border-white/5 px-4 py-2 rounded-xl text-slate-500 font-mono text-[10px] tracking-widest cursor-pointer hover:border-white/20 transition-all group" onClick={() => setIsSearchOpen(true)}>
            <div className="flex items-center gap-2 pr-2 border-r border-white/10">
              <VeyraLogo size="sm" />
            </div>
            <Search size={14} className="group-hover:text-indigo-400 transition-colors" />
            <span>QUICK_SCAN</span>
            <div className="flex items-center gap-1 bg-black/60 px-1.5 py-0.5 rounded border border-white/5">
              <Command size={10} />
              <span>K</span>
            </div>
          </div>

          <div className="hidden xl:flex items-center gap-2 px-4 py-2 bg-emerald-500/5 border border-emerald-500/10 rounded-xl">
             <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
             <span className="text-[9px] font-black uppercase text-emerald-500 tracking-[0.2em] italic">Network_Healthy</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
           {/* Currency Selector */}
           <div className="relative">
             <button 
               onClick={() => setCurrencyOpen(!currencyOpen)}
               className={`p-3 rounded-xl transition-all flex items-center gap-2 ${currencyOpen ? 'bg-white text-black' : 'text-slate-400 hover:text-white hover:bg-white/5 border border-white/5'}`}
             >
                <div className="text-[10px] font-black font-mono tracking-tighter">{selectedCurrency.code}</div>
                <Globe size={16} />
             </button>
             
             <AnimatePresence>
               {currencyOpen && (
                 <motion.div 
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0, y: 10 }}
                   className="absolute right-0 mt-4 w-48 bg-zinc-950 border border-white/10 rounded-3xl shadow-2xl p-2 overflow-hidden z-50 text-white"
                 >
                    {currencies.map((c) => (
                      <button 
                        key={c.code}
                        onClick={() => {
                          setSelectedCurrency(c);
                          setCurrencyOpen(false);
                        }}
                        className={`w-full flex items-center justify-between p-4 rounded-2xl transition-all text-left ${selectedCurrency.code === c.code ? 'bg-indigo-600/20 text-white' : 'hover:bg-white/5 text-slate-400 hover:text-white'}`}
                      >
                         <div>
                            <p className="text-[10px] font-black italic">{c.code}</p>
                            <p className="text-[8px] font-mono text-slate-500 uppercase">{c.symbol}</p>
                         </div>
                         {selectedCurrency.code === c.code && <Check size={14} className="text-indigo-400" />}
                      </button>
                    ))}
                 </motion.div>
               )}
             </AnimatePresence>
           </div>

           {/* Theme Selector */}
           <div className="relative">
             <button 
               onClick={() => setThemeOpen(!themeOpen)}
               className={`p-3 rounded-xl transition-all flex items-center gap-2 ${themeOpen ? 'bg-white text-black' : 'text-slate-400 hover:text-white hover:bg-white/5 border border-white/5'}`}
             >
                <Palette size={18} />
             </button>
             
             <AnimatePresence>
               {themeOpen && (
                 <motion.div 
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0, y: 10 }}
                   className="absolute right-0 mt-4 w-48 bg-zinc-950 border border-white/10 rounded-3xl shadow-2xl p-2 overflow-hidden z-50 text-white"
                 >
                    <div className="p-3 border-b border-white/5 mb-1">
                       <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Select Theme</p>
                    </div>
                    {themes.map((t) => (
                      <button 
                        key={t.id}
                        onClick={() => {
                          setTheme(t.id);
                          setThemeOpen(false);
                        }}
                        className={`w-full flex items-center gap-3 p-3 rounded-2xl transition-all text-left ${theme === t.id ? 'bg-indigo-600/20 text-white' : 'hover:bg-white/5 text-slate-400 hover:text-white'}`}
                      >
                         <t.icon size={14} className={theme === t.id ? 'text-indigo-400' : 'text-slate-600'} />
                         <span className="text-[10px] font-black italic">{t.label}</span>
                      </button>
                    ))}
                 </motion.div>
               )}
             </AnimatePresence>
           </div>

           <div className="w-px h-8 bg-white/5"></div>

           {/* Notifications */}
           <div className="relative">
             <button 
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className={`p-3 rounded-xl transition-all relative ${notificationsOpen ? 'bg-white text-black' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
             >
                <Bell size={18} />
                <span className="absolute top-3 right-3 w-1.5 h-1.5 bg-rose-500 rounded-full border border-black group-hover:animate-ping"></span>
             </button>
             
             <AnimatePresence>
               {notificationsOpen && (
                 <motion.div 
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0, y: 10 }}
                   className="absolute right-0 mt-4 w-80 bg-zinc-950 border border-white/10 rounded-3xl shadow-2xl p-6 space-y-6"
                 >
                    <div className="flex items-center justify-between">
                       <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Local Alerts</h5>
                       <span className="text-[10px] text-indigo-400 cursor-pointer">Mark all read</span>
                    </div>
                    <div className="space-y-4">
                       {[
                         { title: "API_HEALTH", msg: "Gateway health check is responding.", time: "2m", alert: false },
                         { title: "PAPER_ORDER", msg: "One paper order is ready for review.", time: "1h", alert: true },
                         { title: "MARKET_CACHE", msg: "Local market snapshot refreshed.", time: "3h", alert: false },
                       ].map((n, i) => (
                         <div key={i} className="flex gap-4 p-3 hover:bg-white/5 rounded-2xl transition-colors cursor-pointer border border-transparent hover:border-white/5">
                            <div className={`w-2 h-2 mt-1.5 rounded-full ${n.alert ? 'bg-rose-500' : 'bg-slate-700'}`}></div>
                            <div>
                               <p className="text-xs font-bold text-white mb-0.5 uppercase tracking-tighter">{n.title}</p>
                               <p className="text-[10px] text-slate-500 leading-tight">{n.msg}</p>
                            </div>
                         </div>
                       ))}
                    </div>
                    <button className="w-full text-[10px] font-black uppercase text-center text-slate-600 hover:text-white transition-colors">Clear Stream</button>
                 </motion.div>
               )}
             </AnimatePresence>
           </div>

           <div className="relative group/notify">
             <button className="relative w-12 h-12 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-center text-slate-500 hover:text-white hover:border-white/20 transition-all">
                <Bell size={20} />
                <div className="absolute top-3 right-3 w-2 h-2 bg-rose-500 rounded-full border-2 border-black animate-pulse" />
             </button>

             {/* Cascading Notification Link */}
             <div className="absolute right-0 mt-4 w-96 bg-zinc-950 border border-white/10 rounded-[2.5rem] shadow-2xl opacity-0 translate-y-4 pointer-events-none group-hover/notify:opacity-100 group-hover/notify:translate-y-0 group-hover/notify:pointer-events-auto transition-all p-2 z-[100] backdrop-blur-2xl">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                   <div>
                      <h6 className="text-white font-black italic uppercase tracking-tighter text-lg">Activity_Feed</h6>
                      <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">3 Recent Local Events</p>
                   </div>
                   <button className="text-[9px] font-black text-indigo-400 uppercase tracking-widest hover:text-white transition-colors">Mark_Read</button>
                </div>
                
                <div className="max-h-96 overflow-y-auto p-2 space-y-2 scrollbar-hide">
                   {[
                     { title: "API Ready", desc: "Gateway health endpoint returned successfully.", time: "2m ago", type: "success" },
                     { title: "Market Refresh", desc: "Canonical quote cache updated for tracked symbols.", time: "5m ago", type: "info" },
                     { title: "Paper Review", desc: "Pending paper order requires confirmation.", time: "12m ago", type: "error" },
                   ].map((n, i) => (
                     <div key={i} className="p-4 bg-white/[0.02] border border-transparent hover:border-white/5 hover:bg-white/5 rounded-3xl transition-all cursor-pointer group/n">
                        <div className="flex justify-between items-start mb-2">
                           <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded ${
                             n.type === 'error' ? 'bg-rose-500/10 text-rose-500' : 
                             n.type === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 
                             'bg-indigo-500/10 text-indigo-400'
                           }`}>{n.title}</span>
                           <span className="text-[8px] font-mono text-slate-700">{n.time}</span>
                        </div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase italic leading-relaxed group-hover/n:text-white transition-colors">{n.desc}</p>
                     </div>
                   ))}
                </div>

                <div className="p-4 pt-2">
                   <button className="w-full py-4 bg-white/5 border border-white/5 rounded-[1.8rem] text-[9px] font-black uppercase text-slate-400 tracking-widest hover:bg-white transition-all hover:text-black">
                      View_All_Activity
                   </button>
                </div>
             </div>
           </div>

           <div className="w-px h-8 bg-white/5"></div>

           <div className="relative group/profile">
             <input 
               type="file" 
               ref={fileInputRef} 
               className="hidden" 
               accept="image/*"
               onChange={handleFileChange}
             />
             <button 
               onClick={() => onViewChange("account")}
               className="flex items-center gap-3 px-3 py-2 bg-white/5 border border-white/5 rounded-2xl transition-all hover:border-white/20 group"
             >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xl italic text-white shadow-lg ring-2 ring-transparent group-hover:ring-indigo-500/50 transition-all overflow-hidden relative">
                  {user?.avatar ? (
                    <img src={user.avatar} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    user?.name.split(' ').map(n => n[0]).join('') || 'J'
                  )}
                  <div 
                    onClick={handleAvatarClick}
                    className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
                  >
                    <Camera size={14} className="text-white" />
                  </div>
                </div>
                <div className="hidden sm:block text-left pr-4">
                   <p className="text-xs font-black text-[var(--foreground)] uppercase tracking-tight italic">{user?.name || 'Jay Prophit'}</p>
                   <p className="text-[9px] text-slate-600 font-mono tracking-tighter">NODE_LVL_12</p>
                </div>
                <ChevronDown size={14} className="text-slate-700 group-hover:text-slate-400 transition-all" />
             </button>

             {/* Cascading Identity Menu */}
             <div className="absolute right-0 mt-4 w-72 bg-zinc-950 border border-white/10 rounded-[2.5rem] shadow-2xl opacity-0 translate-y-4 pointer-events-none group-hover/profile:opacity-100 group-hover/profile:translate-y-0 group-hover/profile:pointer-events-auto transition-all p-2 z-[100] backdrop-blur-2xl">
                <div className="p-6 bg-white/[0.02] border-b border-white/5 mb-2 rounded-t-[2.2rem]">
                   <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-1">Identity_Kernel</p>
                   <h6 className="text-white font-black italic uppercase tracking-tighter text-lg">{user?.username.toUpperCase() || 'PROPHIT_ALPHA_X'}</h6>
                   <div className="flex gap-2 mt-4">
                      <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[8px] font-black text-emerald-500 uppercase tracking-widest italic">SECURED</div>
                      <div className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-[8px] font-black text-indigo-400 uppercase tracking-widest italic">ACTIVE</div>
                   </div>
                </div>
                <div className="space-y-1">
                   {[
                     { label: "Account Settings", id: "account", icon: Settings },
                     { label: "Health Checks", id: "diagnostics", icon: ShieldCheck },
                     { label: "Knowledge Base", id: "support", icon: Layers }
                   ].map((item, i) => (
                     <button 
                        key={i}
                        onClick={() => onViewChange(item.id as any)}
                        className="w-full flex items-center justify-between p-4 rounded-3xl hover:bg-white/5 transition-all group/item"
                     >
                        <div className="flex items-center gap-4">
                           <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center text-slate-600 group-hover/item:text-indigo-400 group-hover/item:bg-indigo-500/10 transition-all">
                              <item.icon size={16} />
                           </div>
                           <span className="text-[11px] font-black uppercase text-slate-400 group-hover/item:text-white tracking-widest italic">{item.label}</span>
                        </div>
                        <ChevronRight size={14} className="text-slate-800 transition-transform group-hover/item:translate-x-1 group-hover/item:text-indigo-500" />
                     </button>
                   ))}
                </div>
                <div className="mt-2 p-2 pt-0">
                   <button 
                     onClick={() => logout()}
                     className="w-full py-5 bg-rose-500/5 border border-rose-500/10 rounded-[2rem] text-[9px] font-black uppercase text-rose-500/80 tracking-[0.3em] hover:bg-rose-500/10 hover:text-rose-500 transition-all"
                   >
                      Sign_Out
                   </button>
                </div>
             </div>
           </div>
        </div>
      </header>

      {/* Global Search Modal */}
      <AnimatePresence>
        {isSearchOpen && (
          <div className="fixed inset-0 z-[100] flex items-start justify-center pt-24 px-6 md:px-0">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsSearchOpen(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-md"
            />
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              className="relative w-full max-w-2xl bg-zinc-950 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden"
            >
              <div className="p-8 border-b border-white/5 bg-black/40">
                 <div className="flex items-center gap-6">
                    <Search className="text-indigo-400" size={24} />
                    <input 
                      autoFocus
                      placeholder="Search foundation views..."
                      value={searchValue}
                      onChange={(e) => setSearchValue(e.target.value)}
                      className="flex-1 bg-transparent border-none text-2xl font-bold tracking-tighter text-white placeholder-slate-800 outline-none italic"
                    />
                 </div>
              </div>

              <div className="max-h-[400px] overflow-y-auto p-8 space-y-6">
                 {searchResults.length > 0 ? (
                   searchResults.map((result) => (
                     <button
                       key={result.id}
                       onClick={() => {
                         onViewChange(result.id);
                         setIsSearchOpen(false);
                       }}
                       className="w-full flex items-center justify-between p-4 hover:bg-white/5 rounded-2xl transition-all border border-transparent hover:border-white/10 group"
                     >
                        <div className="flex items-center gap-4 text-left">
                           <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center text-slate-500 group-hover:text-indigo-400 transition-colors">
                              {result.group === 'Trading' ? <Layout size={20}/> : result.group === 'Automation' ? <Cpu size={20}/> : <Layers size={20}/>}
                           </div>
                           <div>
                              <p className="text-sm font-bold text-white uppercase tracking-tight">{result.label}</p>
                              <p className="text-[10px] text-slate-500 font-mono tracking-widest">{result.group}</p>
                           </div>
                        </div>
                        <ChevronRight className="text-slate-800 group-hover:text-white transition-colors" size={20} />
                     </button>
                   ))
                 ) : (
                   <div className="text-center py-20">
                      <Zap className="mx-auto text-slate-800 mb-4" size={48} />
                      <p className="text-slate-500 font-mono text-[10px] tracking-widest uppercase">No System Matches Found</p>
                   </div>
                 )}
              </div>

              <div className="p-6 bg-black/40 border-t border-white/5 flex items-center justify-between">
                 <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5 text-[9px] text-slate-500 font-bold uppercase">
                       <span className="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded">ESC</span>
                       <span>to close</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[9px] text-slate-500 font-bold uppercase">
                       <span className="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded">⏎</span>
                       <span>to navigate</span>
                    </div>
                 </div>
                 <div className="text-[9px] text-slate-700 font-mono uppercase tracking-[0.3em]">Foundation_Search</div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
