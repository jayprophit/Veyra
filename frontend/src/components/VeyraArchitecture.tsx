/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Server, Cloud, Database, Globe, ArrowRight } from "lucide-react";

export function VeyraArchitecture() {
  return (
    <div className="bg-black/60 border border-white/10 rounded-2xl p-8 font-sans overflow-hidden">
      <h5 className="text-xs font-bold text-slate-500 uppercase tracking-[0.3em] mb-8">Infrastructure Topology</h5>
      
      <div className="flex flex-col gap-8 relative">
        {/* User Layer */}
        <div className="flex justify-center">
          <div className="bg-white/5 border border-white/20 px-6 py-3 rounded-xl flex items-center gap-3">
            <Globe className="text-cyan-400" size={20} />
            <div className="text-left">
              <p className="text-[10px] font-bold text-white uppercase">Client Gateway</p>
              <p className="text-[8px] text-slate-500 font-mono">React / Mobile / API</p>
            </div>
          </div>
        </div>

        <div className="flex justify-center -my-4">
          <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent"></div>
        </div>

        {/* Compute Layer */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-indigo-900/20 to-transparent border border-indigo-500/30 p-4 rounded-xl">
            <Server className="text-indigo-400 mb-2" size={18} />
            <p className="text-[9px] font-bold text-white">Veyra Core API</p>
            <p className="text-[8px] text-slate-500">Go / GPRC / Redis</p>
          </div>
          <div className="bg-gradient-to-br from-violet-900/20 to-transparent border border-violet-500/30 p-4 rounded-xl">
            <Cloud className="text-violet-400 mb-2" size={18} />
            <p className="text-[9px] font-bold text-white">Visual AI Engine</p>
            <p className="text-[8px] text-slate-500">TensorFlow / CUDA</p>
          </div>
        </div>

        <div className="flex justify-center -my-4">
           <ArrowRight className="rotate-90 text-slate-800" size={16} />
        </div>

        {/* Data Layer */}
        <div className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="text-slate-400" size={18} />
            <div>
              <p className="text-[9px] font-bold text-white uppercase tracking-tighter">Distributed Ledger</p>
              <p className="text-[8px] text-slate-500">PostgreSQL / TimescaleDB</p>
            </div>
          </div>
          <div className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded text-[7px] text-emerald-400 font-bold">
            MULTICLOUD_SYNC
          </div>
        </div>
      </div>
    </div>
  );
}
