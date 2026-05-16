/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Send, Users, Shield, Zap, Globe, MessageSquare } from "lucide-react";
import { useState } from "react";

export function VeyraCommunity() {
  const [messages] = useState([
    { user: "Alpha_Node", text: "VRA accumulation signal triggered at depth 001. Check the contrarian engine.", tier: 12 },
    { user: "Beta_Scout", text: "Oracle sync delay detected on XAU feed. 0.003ms spike. Investigating.", tier: 10 },
    { user: "V_Architect", text: "New identity marks for Level 11 are live in the Asset Studio. Foundation status verified.", tier: 11 },
  ]);

  return (
    <div className="space-y-12">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Chat / Feed */}
        <div className="flex-1 bg-[#0a0a0a] border border-white/10 rounded-[2.5rem] flex flex-col h-[700px]">
          <div className="p-8 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-indigo-600/20 rounded-xl flex items-center justify-center border border-indigo-500/30">
                <Users size={24} className="text-indigo-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold tracking-tighter italic uppercase">Divine_Network</h3>
                <p className="text-[10px] text-slate-500 font-mono flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse space-x-1"></span>
                  2.4K MEMBERS_SYNCED
                </p>
              </div>
            </div>
            <div className="flex gap-2">
               <button className="bg-white/5 p-3 rounded-xl text-slate-500 hover:text-white transition-colors border border-white/5">
                 <Globe size={18} />
               </button>
               <button className="bg-white/5 p-3 rounded-xl text-slate-500 hover:text-white transition-colors border border-white/5">
                 <Shield size={18} />
               </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
            {messages.map((m, i) => (
              <div key={i} className="flex flex-col gap-3 group">
                <div className="flex items-center gap-3">
                   <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center font-bold text-xs italic tracking-tighter border border-white/10 group-hover:border-indigo-500/50 transition-colors">
                     {m.user[0]}
                   </div>
                   <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white uppercase tracking-tight italic">{m.user}</span>
                      <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[8px] font-bold border border-indigo-500/20 rounded uppercase">Tier {m.tier}</span>
                   </div>
                   <span className="text-[10px] text-slate-700 font-mono ml-auto">08:44:10</span>
                </div>
                <div className="pl-11 pr-4">
                   <p className="text-sm text-slate-400 leading-relaxed font-sans group-hover:text-slate-300 transition-colors">{m.text}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="p-8 border-t border-white/5">
             <div className="relative">
                <input 
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-16 text-sm font-sans placeholder-slate-600 outline-none focus:border-indigo-500/50 transition-all"
                  placeholder="Broadcast to Node Layer..."
                />
                <button className="absolute right-3 top-1/2 -translate-y-1/2 bg-indigo-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-colors">
                  <Send size={18} />
                </button>
             </div>
          </div>
        </div>

        {/* Global Stats / Pulse */}
        <div className="w-full lg:w-[380px] space-y-8">
           <div className="bg-zinc-950 border border-white/5 p-8 rounded-[2.5rem]">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] mb-8">Pulse Indicators</h4>
              <div className="space-y-8">
                {[
                  { label: "Community Sentiment", val: "BULLISH", sub: "92.4% Optimal", col: "text-emerald-400", icon: Zap },
                  { label: "Network Latency", val: "24ms", sub: "Global Average", col: "text-indigo-400", icon: Globe },
                  { label: "Resource Burn", val: "124/Sec", sub: "Mining Throughput", col: "text-amber-400", icon: Shield },
                ].map((s, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center border border-white/10 text-slate-500">
                       <s.icon size={18} />
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-slate-600 uppercase mb-1 tracking-tight">{s.label}</p>
                      <div className="flex items-center gap-2">
                        <span className={`text-lg font-black italic tracking-tighter ${s.col}`}>{s.val}</span>
                        <span className="text-[9px] text-slate-700 font-mono uppercase">{s.sub}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
           </div>

           <div className="bg-indigo-600 border border-indigo-500 p-8 rounded-[2.5rem] relative overflow-hidden group shadow-2xl shadow-indigo-600/30">
              <div className="absolute -right-4 -bottom-4 p-8 opacity-10 group-hover:scale-110 transition-transform">
                <MessageSquare size={120} />
              </div>
              <h4 className="text-xl font-black italic text-white uppercase tracking-tighter mb-2 underline decoration-white/20 underline-offset-4">DAO_GOVERNANCE</h4>
              <p className="text-indigo-100 text-xs leading-relaxed mb-6 font-medium">
                VOTE ON THE NEXT DATA CLUSTER DEPLOYMENT IN REGION: US-EAST-1.
              </p>
              <button className="bg-white text-indigo-600 px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-xl border border-white">
                Cast Protocol Vote
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
