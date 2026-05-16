/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip 
} from "recharts";
import { 
  Briefcase, 
  Wallet, 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight, 
  Clock, 
  Activity,
  History,
  ArrowRight,
  Zap,
  Layers
} from "lucide-react";
import { useCurrency } from "../context/CurrencyContext";

const portfolioData = [
  { name: 'Stocks', value: 45, color: '#6366f1' },
  { name: 'Bonds', value: 15, color: '#f59e0b' },
  { name: 'Crytpo', value: 20, color: '#10b981' },
  { name: 'Mining', value: 10, color: '#ef4444' },
  { name: 'Alternatives', value: 10, color: '#a855f7' },
];

const performanceData = [
  { day: 'Mon', val: 4000 },
  { day: 'Tue', val: 3200 },
  { day: 'Wed', val: 4500 },
  { day: 'Thu', val: 5100 },
  { day: 'Fri', val: 4800 },
  { day: 'Sat', val: 6000 },
  { day: 'Sun', val: 5800 },
];

export function VeyraPortfolio() {
  const { formatValue } = useCurrency();

  return (
    <div className="space-y-12">
      {/* 5-Star Summary Header */}
      <div className="grid lg:grid-cols-12 gap-8">
        <div className="lg:col-span-7 bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-12 relative overflow-hidden group">
           <div className="absolute -right-20 -bottom-20 text-white/5 group-hover:scale-110 transition-transform duration-1000">
             <Wallet size={320} />
           </div>
           <div className="relative z-10">
             <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-indigo-500 rounded-2xl flex items-center justify-center">
                   <Zap size={20} className="text-white" />
                </div>
                <p className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.4em]">Integrated Capital Engine</p>
             </div>
             <h2 className="text-6xl md:text-8xl font-black italic tracking-tighter text-white mb-6">{formatValue(1240490.22)}</h2>
             <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-400 font-black text-xs">
                   <ArrowUpRight size={16} />
                   <span>{formatValue(14200.00)} (+1.2%)</span>
                </div>
                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Global Asset Synthesis ACTIVE</div>
             </div>
           </div>
        </div>

        <div className="lg:col-span-5 bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-10 flex flex-col items-center justify-center relative overflow-hidden">
           <div className="w-full h-64 mb-6">
              <ResponsiveContainer width="100%" height="100%">
                 <PieChart>
                    <Pie
                       data={portfolioData}
                       innerRadius={60}
                       outerRadius={90}
                       paddingAngle={5}
                       dataKey="value"
                       stroke="none"
                    >
                       {portfolioData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                       ))}
                    </Pie>
                    <Tooltip 
                       contentStyle={{ background: '#000', border: '1px solid #333', borderRadius: '1rem', fontSize: '10px' }}
                    />
                 </PieChart>
              </ResponsiveContainer>
           </div>
           <div className="grid grid-cols-2 gap-4 w-full">
              {portfolioData.map((item, i) => (
                 <div key={i} className="flex items-center gap-3 p-3 bg-white/5 rounded-2xl border border-white/5">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <div>
                       <p className="text-[9px] font-black uppercase text-slate-500 truncate">{item.name}</p>
                       <p className="text-xs font-bold text-white tracking-widest">{item.value}%</p>
                    </div>
                 </div>
              ))}
           </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
         {/* Detailed Analytics Grid */}
         <div className="col-span-1 space-y-6">
            <div className="p-8 bg-zinc-950 border border-white/10 rounded-[2.5rem]">
               <div className="flex items-center justify-between mb-8">
                  <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Yield_Optimization</h5>
                  <TrendingUp size={16} className="text-amber-500" />
               </div>
               <div className="space-y-4">
                  {[
                    { label: "Nexo Vault A", yield: "12.4%", status: "OPTIMAL" },
                    { label: "VRA Staking", yield: "18.2%", status: "CRITICAL" },
                    { label: "Mirror Yield", yield: "5.1%", status: "STABLE" }
                  ].map((y, i) => (
                    <div key={i} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0">
                       <span className="text-xs font-bold text-white">{y.label}</span>
                       <span className="text-xs font-mono font-black text-emerald-400">{y.yield} APY</span>
                    </div>
                  ))}
               </div>
            </div>
            
            <div className="p-8 bg-indigo-600 rounded-[2.5rem] text-white shadow-2xl relative overflow-hidden group">
               <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform">
                  <Activity size={96} />
               </div>
               <h5 className="text-xl font-black italic tracking-tighter uppercase mb-4">Neural_Audit</h5>
               <p className="text-[10px] font-bold text-indigo-100 uppercase leading-relaxed mb-6">
                  Systematic risk analysis complete. Current portfolio structure is 94% efficient relative to market volatility.
               </p>
               <button className="w-full py-4 bg-white text-indigo-600 rounded-2xl font-black uppercase tracking-widest text-[10px] transition-transform active:scale-95">
                  Rebalance_Protocol
               </button>
            </div>
         </div>

         {/* Asset Table: Pro Appearance */}
         <div className="md:col-span-2 bg-[#0a0a0a] border border-white/10 rounded-[3rem] overflow-hidden">
            <div className="p-8 border-b border-white/5 flex items-center justify-between">
               <div className="flex items-center gap-3">
                  <Layers size={18} className="text-slate-500" />
                  <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Live_Reserves_Matrix</h5>
               </div>
               <div className="flex gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[8px] font-black text-emerald-500 uppercase">Synced_Protocol_v2.0</span>
               </div>
            </div>
            <div className="overflow-x-auto">
               <table className="w-full text-left">
                  <thead>
                     <tr className="border-b border-white/5">
                        <th className="p-8 text-[10px] font-black uppercase text-slate-600 tracking-widest">Asset_Identifier</th>
                        <th className="p-8 text-[10px] font-black uppercase text-slate-600 tracking-widest">Allocation</th>
                        <th className="p-8 text-[10px] font-black uppercase text-slate-600 tracking-widest">Unrealized PNL</th>
                        <th className="p-8 text-[10px] font-black uppercase text-slate-600 tracking-widest">Status</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                     {[
                       { name: "Bitcoin (Mirror)", tag: "BTC_M", value: 42420.12, pnl: 1204.00, color: "text-amber-400", bg: "bg-amber-400/10" },
                       { name: "Veyra Native", tag: "VRA", value: 12440.00, pnl: 4220.12, color: "text-indigo-400", bg: "bg-indigo-400/10" },
                       { name: "Ethereum (Mirror)", tag: "ETH_M", value: 8204.44, pnl: -122.00, color: "text-blue-400", bg: "bg-blue-400/10" },
                     ].map((asset, i) => (
                       <tr key={i} className="hover:bg-white/5 transition-colors group">
                          <td className="p-8">
                             <div className="flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-black italic ${asset.bg} ${asset.color}`}>
                                   {asset.tag[0]}
                                </div>
                                <div>
                                   <p className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors uppercase italic">{asset.name}</p>
                                   <p className="text-[9px] font-mono text-slate-600">{asset.tag}</p>
                                </div>
                             </div>
                          </td>
                          <td className="p-8">
                             <p className="text-sm font-black font-mono text-white tracking-widest">{formatValue(asset.value)}</p>
                          </td>
                          <td className="p-8">
                             <div className={`flex items-center gap-2 font-black italic tracking-tighter text-sm ${asset.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {asset.pnl >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                {formatValue(Math.abs(asset.pnl))}
                             </div>
                          </td>
                          <td className="p-8">
                             <div className="px-3 py-1 bg-white/5 border border-white/5 rounded-full inline-block">
                                <span className="text-[8px] font-black uppercase text-slate-500 tracking-widest">Verified</span>
                             </div>
                          </td>
                       </tr>
                     ))}
                  </tbody>
               </table>
            </div>
         </div>
      </div>
    </div>
  );
}
