/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Hammer, CircleDollarSign, Factory, Pickaxe, Boxes } from "lucide-react";
import { useState, useEffect } from "react";

export function VeyraExtractionLab() {
  const [minedData, setMinedData] = useState([
    { asset: "Lithium", current: 420, target: 1000, color: "text-cyan-400" },
    { asset: "Gold (XAU)", current: 12.4, target: 50, color: "text-amber-400" },
    { asset: "Platinum", current: 8.2, target: 20, color: "text-slate-300" },
  ]);

  return (
    <div className="space-y-12">
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Resource Extraction Monitoring */}
        <div className="bg-[#0a0a0a] border border-white/10 rounded-3xl p-8 relative overflow-hidden">
          <div className="absolute -right-8 -bottom-8 opacity-5">
            <Pickaxe size={160} />
          </div>
          
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-xl font-bold uppercase tracking-widest italic">Mining Analytics</h3>
              <p className="text-[10px] text-slate-500 font-mono">NODE_CLUSTER: DEPTH_001</p>
            </div>
            <Factory size={24} className="text-slate-600" />
          </div>

          <div className="space-y-8">
            {minedData.map((m, i) => (
              <div key={i} className="group">
                <div className="flex justify-between items-end mb-2">
                  <span className={`text-xs font-bold uppercase ${m.color}`}>{m.asset}</span>
                  <span className="text-[10px] font-mono text-slate-400">{m.current} / {m.target} UNITS</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden border border-white/5">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${(m.current/m.target)*100}%` }}
                    transition={{ 
                      duration: 1.5, 
                      delay: i * 0.2,
                      ease: [0.16, 1, 0.3, 1] 
                    }}
                    className={`h-full bg-current ${m.color.replace('text-', 'bg-')}`}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 flex gap-4">
             <button className="flex-1 bg-white text-black py-3 rounded-xl text-xs font-bold uppercase tracking-widest border border-white shadow-xl">
               Optimize Extraction
             </button>
             <button className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-slate-400 hover:text-white transition-colors">
               <Boxes size={18} />
             </button>
          </div>
        </div>

        {/* Minting Terminal */}
        <div className="bg-gradient-to-br from-indigo-900/10 to-transparent border border-indigo-500/20 rounded-3xl p-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-indigo-600/20 rounded-full flex items-center justify-center border border-indigo-500/40">
              <CircleDollarSign size={20} className="text-indigo-400" />
            </div>
            <h3 className="text-xl font-bold uppercase tracking-widest italic">Token Forge</h3>
          </div>

          <div className="bg-black/60 border border-white/10 rounded-2xl p-6 mb-8 text-center">
             <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-mono">Circulating Supply (VRA)</p>
             <h2 className="text-4xl font-black italic tracking-tighter text-white">1,240,490,221</h2>
             <div className="flex justify-center gap-2 mt-4">
               <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[8px] font-bold border border-emerald-500/20 rounded uppercase">Minting Enabled</span>
               <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[8px] font-bold border border-indigo-500/20 rounded uppercase">Private Foundation</span>
             </div>
          </div>

          <div className="space-y-4">
             <div className="p-4 bg-white/5 border border-white/5 rounded-xl flex justify-between items-center group hover:border-indigo-400/50 transition-colors">
                <div className="flex items-center gap-3">
                   <Hammer size={16} className="text-slate-500 group-hover:text-indigo-400 transition-colors" />
                   <span className="text-[11px] font-bold tracking-tight">MINT_VRA_IDENTITY</span>
                </div>
                <button className="text-xs font-black uppercase tracking-widest px-4 py-1.5 bg-indigo-600 rounded-lg shadow-lg">Mint</button>
             </div>
             
             <div className="p-4 bg-white/5 border border-white/5 rounded-xl flex justify-between items-center">
                <div className="flex items-center gap-3">
                   <CircleDollarSign size={16} className="text-slate-500" />
                   <span className="text-[11px] font-bold tracking-tight text-slate-400 opacity-50">STAKE_PROOFS (Locked)</span>
                </div>
                <span className="text-[10px] font-mono text-slate-700">T-11 REQ</span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
