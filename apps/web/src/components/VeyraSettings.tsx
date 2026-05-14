/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from "react";
import { motion } from "motion/react";
import { 
  User, 
  Shield, 
  Key, 
  Bell, 
  Smartphone, 
  Globe, 
  Database, 
  ChevronRight,
  ShieldAlert,
  CreditCard,
  ShieldCheck,
  ToggleLeft,
  ToggleRight,
  Lock,
  Cpu
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

export function VeyraSettings() {
  const { user } = useAuth();
  const [toggles, setToggles] = useState({
    twoFactor: true,
    stealthMode: false,
    aiOptimization: true,
    oracleSync: true
  });

  const [profile, setProfile] = useState({
    name: user?.name || "Jay Prophit",
    username: user?.username || "@prophit_alpha",
    email: user?.email || "jprophit@gmail.com",
    walletAddress: "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    protocolId: "VRA_ALPHA_001_X",
    accountTier: "Transcendent"
  });

  const toggleSetting = (key: keyof typeof toggles) => {
    setToggles(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const updateProfile = (field: keyof typeof profile, value: string) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-24">
      <header className="mb-12">
         <h2 className="text-5xl font-black italic tracking-tighter mb-4 uppercase text-white">System_Configuration</h2>
         <p className="text-slate-500 leading-relaxed font-sans text-lg italic uppercase tracking-wider">Manage high-latency node encryption, protocol kernels, and neural-sync permissions.</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-8 items-start">
        {/* Profile Identity Card */}
        <div className="lg:col-span-1 bg-[#0a0a0a] border border-white/5 p-8 rounded-[3rem] relative overflow-hidden group hover:border-indigo-500/30 transition-all flex flex-col items-center text-center h-full">
          <div className="absolute -right-4 -top-4 p-8 opacity-5 group-hover:scale-110 transition-transform">
            <User size={120} />
          </div>
          <div className="w-24 h-24 rounded-[2.5rem] bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center font-black text-3xl italic shadow-2xl text-white mb-6">
            {profile.name.split(' ').map(n => n[0]).join('')}
          </div>
          <h3 className="text-2xl font-black italic uppercase text-white mb-2">{profile.name}</h3>
          <p className="text-[9px] text-indigo-400 font-mono uppercase tracking-[0.3em] font-black mb-6">NODE_LEVEL_{profile.accountTier.toUpperCase()}</p>
          
          <div className="w-full space-y-3 pt-6 border-t border-white/5">
             <div className="flex flex-col gap-1">
                <span className="text-[8px] font-black text-slate-700 uppercase tracking-widest">Protocol_Signature</span>
                <span className="text-[10px] font-mono text-slate-400 truncate">{profile.protocolId}</span>
             </div>
          </div>
        </div>

        {/* Identity Grid Form */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-white/5 p-10 rounded-[4rem] space-y-8 h-full">
           <div className="flex items-center gap-4 mb-4">
              <ShieldCheck size={20} className="text-indigo-500" />
              <h4 className="text-xl font-black italic text-white uppercase tracking-tighter">Core_Identity_Manifest</h4>
           </div>

           <div className="grid sm:grid-cols-2 gap-8">
              <div className="space-y-2">
                 <label className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] pl-2">Legal_Name</label>
                 <input 
                   type="text" 
                   value={profile.name}
                   onChange={(e) => updateProfile('name', e.target.value)}
                   className="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic"
                 />
              </div>
              <div className="space-y-2">
                 <label className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] pl-2">User_Handle</label>
                 <input 
                   type="text" 
                   value={profile.username}
                   onChange={(e) => updateProfile('username', e.target.value)}
                   className="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic"
                 />
              </div>
              <div className="space-y-2">
                 <label className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] pl-2">Email_Bridge</label>
                 <input 
                   type="email" 
                   value={profile.email}
                   onChange={(e) => updateProfile('email', e.target.value)}
                   className="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all italic"
                 />
              </div>
              <div className="space-y-2">
                 <label className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] pl-2">Node_ID</label>
                 <input 
                   type="text" 
                   value={profile.protocolId}
                   readOnly
                   className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-sm font-mono text-slate-500 cursor-not-allowed italic"
                 />
              </div>
              <div className="sm:col-span-2 space-y-2">
                 <label className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] pl-2">Primary_Wallet_Address</label>
                 <div className="relative">
                    <input 
                      type="text" 
                      value={profile.walletAddress}
                      onChange={(e) => updateProfile('walletAddress', e.target.value)}
                      className="w-full bg-black/40 border border-white/5 rounded-2xl p-4 pr-14 text-[11px] font-mono text-indigo-400 focus:outline-none focus:border-indigo-500/50 transition-all italic uppercase"
                    />
                    <CreditCard size={18} className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-700" />
                 </div>
              </div>
           </div>

           <div className="pt-6">
              <button className="flex items-center gap-4 px-10 py-4 bg-white text-black rounded-2xl font-black uppercase text-[10px] tracking-widest hover:scale-105 transition-all shadow-2xl">
                 Commit_Manifest_Update
              </button>
           </div>
        </div>
      </div>

      {/* Grid Row 2: Security & Summary */}
      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-1 bg-black/40 border border-white/5 p-10 rounded-[3rem] flex flex-col justify-between border-l-4 border-l-emerald-500">
           <div className="flex justify-between items-start mb-8">
              <div>
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Network Credibility</p>
                <h4 className="text-6xl font-black italic tracking-tighter text-emerald-400">AA+</h4>
              </div>
              <div className="p-4 bg-emerald-500/10 rounded-2xl">
                <ShieldCheck className="text-emerald-400" size={32} />
              </div>
           </div>
           
           <div className="space-y-3">
              <div className="flex items-center justify-between">
                 <span className="text-[10px] font-black uppercase text-slate-600">Verification Rate</span>
                 <span className="text-[10px] font-mono text-emerald-500">99.98%</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                 <div className="w-[99.98%] h-full bg-emerald-500" />
              </div>
           </div>
        </div>

        <div className="md:col-span-2 bg-[#0a0a0a] border border-white/5 p-10 rounded-[3rem] flex items-center justify-between group">
           <div className="space-y-4">
              <h5 className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Protocol_Uptime</h5>
              <div className="flex items-baseline gap-2">
                 <span className="text-4xl font-black italic text-white">4,202</span>
                 <span className="text-xs font-mono text-slate-600">HOURS_ACTIVE</span>
              </div>
           </div>
           <div className="flex gap-2">
              {[1,2,3,4,5,6,7,8].map(i => (
                <div key={i} className={`w-1 h-12 rounded-full ${i > 6 ? 'bg-indigo-500' : 'bg-indigo-200'} opacity-20`} />
              ))}
           </div>
        </div>
      </div>

      {/* Control Toggles */}
      <div className="grid sm:grid-cols-2 gap-6">
         {[
           { id: 'twoFactor', label: 'Biometric 2FA', sub: 'Neural Mesh Verification', icon: Smartphone },
           { id: 'stealthMode', label: 'Dark Node Splicing', sub: 'IP Proxy Extraction', icon: Lock },
           { id: 'aiOptimization', label: 'Auto-Bot Sync', sub: 'Forge Intelligence V3', icon: Cpu },
           { id: 'oracleSync', label: 'Global Oracle Push', sub: 'Real-time Asset Calibration', icon: Globe }
         ].map((setting) => (
           <div key={setting.id} className="p-8 bg-[#0a0a0a] border border-white/5 rounded-[2.5rem] flex items-center justify-between group hover:bg-white/5 transition-all">
              <div className="flex items-center gap-4">
                 <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center text-slate-500 group-hover:text-indigo-400 transition-colors">
                    <setting.icon size={20} />
                 </div>
                 <div>
                    <h5 className="text-[10px] font-black uppercase text-white tracking-widest mb-1">{setting.label}</h5>
                    <p className="text-[9px] font-mono text-slate-600 uppercase italic">{setting.sub}</p>
                 </div>
              </div>
              <button 
                onClick={() => toggleSetting(setting.id as keyof typeof toggles)}
                className={`transition-colors ${toggles[setting.id as keyof typeof toggles] ? 'text-indigo-500' : 'text-slate-700'}`}
              >
                {toggles[setting.id as keyof typeof toggles] ? <ToggleRight size={32} /> : <ToggleLeft size={32} />}
              </button>
           </div>
         ))}
      </div>

      {/* Settings Groups */}
      <div className="space-y-4">
        <h5 className="text-[10px] font-black uppercase text-slate-600 tracking-[0.4em] mb-6 pl-4">Advanced_Parameters</h5>
        {[
          { label: "API_GATEWAY_MANAGEMENT", sub: "Generate encrypted keys for external Veyra nodes.", icon: Key, col: "text-amber-400" },
          { label: "NOTIFICATION_PROTOCOLS", sub: "Webhooks, Signal Alpha, High-frequency alerts.", icon: Bell, col: "text-rose-400" },
          { label: "ORACLE_DATA_RESERVES", sub: "Configure TimescaleDB and Mirror kernel feeds.", icon: Database, col: "text-emerald-400" },
          { label: "FISCAL_TAX_EXPORT", sub: "Professional IRS8949 reporting (JSON/CSV bundles).", icon: CreditCard, col: "text-slate-400" },
        ].map((item, i) => (
          <motion.div 
            key={i}
            whileHover={{ x: 8, backgroundColor: 'rgba(255,255,255,0.05)' }}
            className="flex items-center justify-between p-8 bg-white/2 border border-white/5 rounded-[2.5rem] cursor-pointer group transition-all"
          >
             <div className="flex items-center gap-8">
               <div className={`w-14 h-14 bg-black/40 rounded-2xl flex items-center justify-center border border-white/5 ${item.col} group-hover:scale-110 transition-transform`}>
                  <item.icon size={24} />
               </div>
               <div>
                  <h4 className="font-black text-sm uppercase tracking-widest italic text-white group-hover:text-indigo-400 transition-colors">{item.label}</h4>
                  <p className="text-[10px] text-slate-500 font-mono uppercase mt-1 tracking-wider">{item.sub}</p>
               </div>
             </div>
             <ChevronRight size={24} className="text-slate-800 group-hover:text-white transition-all transform group-hover:translate-x-2" />
          </motion.div>
        ))}
      </div>

      {/* Danger Zone */}
      <div className="pt-12 border-t border-white/5">
         <div className="bg-rose-500/5 border border-rose-500/20 p-10 rounded-[3.5rem] flex flex-col lg:flex-row items-center justify-between gap-12">
            <div className="flex items-center gap-8 text-center lg:text-left flex-col lg:flex-row">
               <div className="w-24 h-24 rounded-3xl bg-rose-500/20 flex items-center justify-center text-rose-500 border border-rose-500/40 shadow-2xl">
                  <ShieldAlert size={48} />
               </div>
               <div>
                  <h4 className="text-3xl font-black italic uppercase tracking-tighter mb-4 text-white">Decommission_Kernel</h4>
                  <p className="text-sm font-bold text-slate-500 leading-relaxed italic uppercase max-w-md">
                    IRREVERSIBLY WIPE ALL IDENTITY KEYS, PORTFOLIO MIRRORS, AND BOT INSTANCES FROM THE VEYRA NETWORK. THIS ACTION IS FINAL.
                  </p>
               </div>
            </div>
            <button className="px-12 py-5 bg-rose-600 text-white font-black uppercase text-[10px] tracking-[0.2em] rounded-2xl hover:bg-rose-500 transition-all hover:scale-105 active:scale-95 shadow-2xl shadow-rose-600/30">
               Initiate_Destruction
            </button>
         </div>
      </div>
    </div>
  );
}
