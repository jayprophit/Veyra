/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";

export function VeyraContrarian() {
  return (
    <div className="bg-zinc-900 border border-white/5 rounded-2xl p-6 font-sans relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
        <Activity size={48} />
      </div>

      <h5 className="text-[10px] font-bold text-rose-500 uppercase tracking-widest mb-4 flex items-center gap-2">
        <div className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></div>
        Contrarian Analysis
      </h5>

      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-2xl font-black italic tracking-tighter">92.4%</p>
          <p className="text-[9px] text-slate-500 uppercase font-bold">Crowd Sentiment</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-black italic tracking-tighter text-emerald-400">LONG</p>
          <p className="text-[9px] text-slate-500 uppercase font-bold">Recommended Signal</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
          <div className="h-full bg-rose-500 w-[92%]" />
          <div className="h-full bg-emerald-500 w-[8%]" />
        </div>
        
        <div className="flex justify-between text-[8px] font-mono text-slate-500">
          <span>EXCESSIVE OPTIMISM (SELL)</span>
          <span>FEAR (BUY)</span>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <TrendingDown size={12} className="text-rose-500" />
          <span>Retail volume at 2-year high</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <TrendingUp size={12} className="text-emerald-500" />
          <span>Whale accumulation detected (VRA-Signal)</span>
        </div>
      </div>
    </div>
  );
}
