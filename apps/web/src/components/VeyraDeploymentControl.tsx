/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Server, Zap, Shield, Globe, Cpu } from "lucide-react";

export function VeyraDeploymentControl() {
  return (
    <div className="bg-[#0c0c0c] border border-white/10 rounded-2xl p-6 font-mono">
      <div className="flex items-center justify-between mb-6">
        <h5 className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Multi-Cloud Orchestrator</h5>
        <div className="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 rounded text-[7px] text-indigo-300">V.12.0_SYNC</div>
      </div>

      <div className="space-y-4">
        {/* Strategy Alpha */}
        <div className="p-3 bg-white/5 border border-white/10 rounded-xl group hover:border-indigo-500/50 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Globe size={14} className="text-slate-400" />
              <span className="text-[10px] font-bold text-white">STRATEGY: ZERO-COST</span>
            </div>
            <span className="text-[8px] text-emerald-400">ACTIVE</span>
          </div>
          <div className="flex gap-1 h-1 bg-white/5 rounded-full overflow-hidden">
            <div className="w-1/3 bg-indigo-500"></div>
            <div className="w-1/4 bg-blue-500"></div>
          </div>
          <p className="text-[8px] text-slate-500 mt-2 uppercase">Edges: Vercel / Cloudflare / Netlify</p>
        </div>

        {/* Strategy Beta */}
        <div className="p-3 bg-indigo-900/20 border border-indigo-500/30 rounded-xl relative overflow-hidden">
          <div className="absolute -right-2 -top-2 opacity-10">
            <Shield size={40} />
          </div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Server size={14} className="text-indigo-400" />
              <span className="text-[10px] font-bold text-white">STRATEGY: ENTERPRISE</span>
            </div>
            <span className="text-[8px] text-indigo-400 animate-pulse">OPTIMIZING</span>
          </div>
          <div className="grid grid-cols-3 gap-1">
             <div className="h-1 bg-indigo-500 rounded-full"></div>
             <div className="h-1 bg-indigo-500 rounded-full"></div>
             <div className="h-1 bg-indigo-500/20 rounded-full"></div>
          </div>
          <p className="text-[8px] text-slate-400 mt-2 uppercase">Nodes: AWS / GCP / Azure (Private)</p>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center">
        <div className="flex items-center gap-2 text-[8px] text-slate-600">
          <Cpu size={10} />
          <span>L-Sync: 12ms</span>
        </div>
        <button className="text-[8px] font-bold text-white bg-white/10 px-3 py-1 rounded hover:bg-indigo-600 transition-colors">DECODE LOGS</button>
      </div>
    </div>
  );
}
