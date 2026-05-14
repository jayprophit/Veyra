/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { Landmark, TrendingUp, TrendingDown, ArrowRight, Table as TableIcon, Activity, Cpu, Shield } from "lucide-react";
import { useCurrency } from "../context/CurrencyContext";
import { useState } from "react";
import { VeyraInfoBox } from "./VeyraInfoBox";

const marketData = [
  { symbol: "V-EQUITY", name: "Veyra Infrastructure Shares", price: "442.20", delta: "+1.2%", status: "Open" },
  { symbol: "V-BOND-12", name: "10Y Treasury Linked (VRA)", price: "98.45", delta: "-0.05%", status: "Active" },
  { symbol: "AAPL-V", name: "Apple Oracle Mirror", price: "182.10", delta: "+0.8%", status: "Open" },
  { symbol: "TSLA-V", name: "Tesla Oracle Mirror", price: "172.44", delta: "+5.1%", status: "Volatile" },
];

export function VeyraFinanceMarkets() {
  const { formatValue } = useCurrency();
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  return (
    <div className="space-y-12">
      <div className="grid lg:grid-cols-4 gap-8">
        {[
          { label: "Equities_Benchmark", val: "+2.4%", sub: "S&P Mirror Protocol", up: true },
          { label: "Bond_Yield_Index", val: "4.82%", sub: "Aggregated Yield Hub", up: true },
          { label: "Total_Market_Gap", val: formatValue(12400000000).replace(/\.00$/, ''), sub: "Mirror Asset Cap", up: true },
          { label: "Integrated_Volume", val: formatValue(2100000).replace(/\.00$/, ''), sub: "24h Cross-Node", up: false }
        ].map((stat, i) => (
          <VeyraInfoBox 
            key={i} 
            label={stat.label} 
            value={stat.val} 
            details={[
              { label: "Drift", value: "0.0012%" },
              { label: "Nodes", value: "Active" },
              { label: "Stability", value: "99.98%" }
            ]}
          >
            <div className="bg-[#0a0a0a] border border-white/10 p-8 rounded-[2.5rem] relative overflow-hidden group hover:bg-white/5 transition-all active:scale-95 cursor-help h-full">
               <div className="absolute -right-4 -bottom-4 text-white/5 group-hover:scale-110 transition-transform">
                  <TrendingUp size={80} />
               </div>
               <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mb-1">{stat.label}</p>
               <h4 className="text-3xl font-black italic tracking-tighter text-white mb-2">{stat.val}</h4>
               <div className="flex items-center gap-2">
                  <div className={`w-1 h-1 rounded-full ${stat.up ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                  <p className="text-[9px] text-slate-600 font-mono uppercase tracking-widest">{stat.sub}</p>
               </div>
            </div>
          </VeyraInfoBox>
        ))}
      </div>

      <div className="bg-[#0a0a0a] border border-white/10 rounded-[3rem] overflow-hidden shadow-2xl">
        <div className="p-10 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 bg-black/40">
           <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-indigo-500 rounded-2xl flex items-center justify-center shadow-2xl">
                 <Landmark size={24} className="text-white" />
              </div>
              <div>
                 <h3 className="text-2xl font-black uppercase tracking-tighter italic">Global Asset Registry</h3>
                 <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Mirror_Asset_Node_v2_Active</p>
              </div>
           </div>
           <div className="flex gap-2 p-1 bg-white/5 rounded-2xl border border-white/5">
              {['Equities', 'Bonds', 'Indices'].map(tab => (
                 <button key={tab} className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${tab === 'Equities' ? 'bg-white text-black' : 'text-slate-500 hover:text-white'}`}>
                    {tab}
                 </button>
              ))}
           </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#050505] text-[10px] font-black uppercase tracking-widest text-slate-600">
              <tr>
                <th className="p-10 font-medium italic">Asset Identifier</th>
                <th className="p-10 font-medium italic">Spot Price</th>
                <th className="p-10 font-medium italic">24h Delta</th>
                <th className="p-10 font-medium italic">Market State</th>
                <th className="p-10 font-medium text-right italic">Liquidity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-sans">
              {marketData.map((asset, i) => (
                <>
                <tr 
                  key={asset.symbol} 
                  onClick={() => setExpandedRow(expandedRow === asset.symbol ? null : asset.symbol)}
                  className="group hover:bg-white/5 transition-colors cursor-pointer"
                >
                  <td className="p-10">
                    <div className="flex items-center gap-6">
                       <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 italic font-black text-sm text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-all">
                         {asset.symbol[0]}
                       </div>
                       <div>
                         <p className="font-black text-lg tracking-tighter uppercase italic group-hover:text-indigo-400 transition-colors">{asset.name}</p>
                         <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">{asset.symbol}</p>
                       </div>
                    </div>
                  </td>
                  <td className="p-10 font-mono text-lg font-black text-white">{formatValue(parseFloat(asset.price))}</td>
                  <td className={`p-10 font-mono text-sm font-black italic tracking-tighter ${asset.delta.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {asset.delta}
                  </td>
                  <td className="p-10">
                    <VeyraInfoBox 
                      label="Asset_Node_State" 
                      value={asset.status} 
                      details={[
                        { label: "Market", value: "Spot_Mirror" },
                        { label: "Oracle", value: "Verified" },
                        { label: "Sync", value: "0.2ms" }
                      ]}
                    >
                      <span className="px-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-[9px] font-black uppercase tracking-[0.2em] text-slate-400 cursor-help hover:border-indigo-500/30 hover:text-indigo-400 transition-all">
                        {asset.status}
                      </span>
                    </VeyraInfoBox>
                  </td>
                  <td className="p-10 text-right">
                    <ArrowRight size={24} className={`ml-auto text-slate-700 transition-all ${expandedRow === asset.symbol ? 'rotate-90 text-indigo-400' : 'group-hover:text-white group-hover:translate-x-2'}`} />
                  </td>
                </tr>
                <AnimatePresence>
                   {expandedRow === asset.symbol && (
                     <tr key={`${asset.symbol}-details`}>
                        <td colSpan={5} className="p-0 bg-white/[0.01]">
                           <motion.div
                             initial={{ height: 0, opacity: 0 }}
                             animate={{ height: 'auto', opacity: 1 }}
                             exit={{ height: 0, opacity: 0 }}
                             className="overflow-hidden"
                           >
                              <div className="p-10 grid grid-cols-4 gap-8">
                                 {[
                                   { l: "Kernel_Load", v: "14%", icon: Cpu },
                                   { l: "Drift_Correction", v: "0.00ms", icon: Activity },
                                   { l: "Liquidity_Reserve", v: "$14.2M", icon: Landmark },
                                   { l: "Sync_Reliability", v: "99.98%", icon: Shield }
                                 ].map((d, idx) => (
                                   <div key={idx} className="p-6 bg-black/40 border border-white/5 rounded-3xl group/d">
                                      <d.icon size={16} className="text-slate-600 mb-3 group-hover/d:text-indigo-400" />
                                      <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">{d.l}</p>
                                      <p className="text-lg font-black italic text-white uppercase">{d.v}</p>
                                   </div>
                                 ))}
                              </div>
                           </motion.div>
                        </td>
                     </tr>
                   )}
                </AnimatePresence>
                </>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="p-10 bg-black/40 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-6">
           <div className="flex items-center gap-4 text-[10px] text-slate-600 font-mono">
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-lg">
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                 <span className="font-black text-emerald-500 uppercase">ORACLE_SYNCHRONIZED</span>
              </div>
              <div className="flex items-center gap-2">
                 <Activity size={14} />
                 <span>FIDELITY: 99.998%</span>
              </div>
           </div>
           <button className="px-8 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] text-white hover:bg-white/10 transition-all hover:scale-105 active:scale-95 shadow-2xl">
              Expand Registry Data
           </button>
        </div>
      </div>
    </div>
  );
}
