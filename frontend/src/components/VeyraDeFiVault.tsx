/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Landmark, TrendingUp, Percent, Lock, Coins, ShieldCheck } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const stakingData = [
  { name: 'VRA', value: 400, color: '#6366f1' },
  { name: 'XAU', value: 300, color: '#f59e0b' },
  { name: 'USDT', value: 300, color: '#10b981' },
];

export function VeyraDeFiVault() {
  return (
    <div className="space-y-12">
      {/* Pool Overview */}
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-white/10 rounded-3xl p-8 relative overflow-hidden">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h3 className="text-xl font-bold uppercase tracking-widest italic">Global Liquidity Pool</h3>
              <p className="text-[10px] text-slate-500 font-mono">PROTOCOL: VRA_VAULT_V12</p>
            </div>
            <div className="flex items-center gap-2 text-emerald-400">
               <TrendingUp size={18} />
               <span className="font-mono text-sm font-black">+14.2% APY</span>
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-8 mb-10">
            {[
              { label: "Total Value Locked", val: "$42.2M", icon: Landmark },
              { label: "Staked Assets", val: "1.2M VRA", icon: Coins },
              { label: "Pool Health", val: "Optimal", icon: ShieldCheck },
            ].map((s, i) => (
              <div key={i}>
                <div className="flex items-center gap-2 mb-2">
                  <s.icon size={14} className="text-slate-600" />
                  <span className="text-[10px] text-slate-500 font-bold uppercase">{s.label}</span>
                </div>
                <h4 className="text-2xl font-black italic tracking-tighter text-white">{s.val}</h4>
              </div>
            ))}
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
               <PieChart>
                 <Pie data={stakingData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                   {stakingData.map((entry, index) => (
                     <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                   ))}
                 </Pie>
               </PieChart>
            </ResponsiveContainer>
            <div className="absolute flex flex-col items-center">
               <span className="text-[10px] text-slate-500 font-bold uppercase mb-1">Diversification</span>
               <span className="text-lg font-black text-white italic">AA+</span>
            </div>
          </div>
        </div>

        {/* Stake Control */}
        <div className="bg-zinc-900 border border-white/5 rounded-3xl p-8">
           <div className="flex items-center gap-3 mb-8">
             <div className="w-10 h-10 bg-indigo-600/10 rounded-xl flex items-center justify-center border border-indigo-500/20">
               <Lock size={18} className="text-indigo-400" />
             </div>
             <h3 className="text-xl font-bold uppercase tracking-widest italic">Asset Lockdown</h3>
           </div>

           <div className="space-y-6">
              <div className="bg-black/60 p-4 rounded-2xl border border-white/5 group">
                 <p className="text-[9px] text-slate-600 font-bold uppercase mb-2">Select Duration</p>
                 <div className="grid grid-cols-2 gap-2">
                    {['30 Days', '90 Days', '180 Days', '1 Year'].map(t => (
                      <button key={t} className="py-2.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-bold uppercase hover:bg-white hover:text-black transition-all">
                        {t}
                      </button>
                    ))}
                 </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-indigo-900/20 to-transparent border border-indigo-500/30 rounded-2xl">
                 <div className="flex items-center justify-between mb-4">
                    <span className="text-[10px] text-indigo-300 font-bold uppercase">Compound Interest</span>
                    <Percent size={14} className="text-indigo-400" />
                 </div>
                 <p className="text-xs text-slate-400 mb-4 leading-relaxed">Stake VRA token to earn an estimated <span className="text-white font-bold">12.4% annually</span> plus network protocol rewards.</p>
                 <button className="w-full bg-indigo-600 text-white py-4 rounded-xl text-xs font-black uppercase tracking-widest shadow-xl shadow-indigo-600/20 mt-4">
                   Initialize Stake
                 </button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
