/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Terminal, Database, Activity, GitBranch } from "lucide-react";

export function VeyraAlphaTerminal() {
  const logs = [
    { time: "08:12:01", msg: "VRA_SIGNAL_LOCK: METALS_BULLISH", type: "info" },
    { time: "08:12:03", msg: "VISUAL_AI: PATTERN_77_DETECTED", type: "warn" },
    { time: "08:12:05", msg: "TRANSCENDENT_SYNC: COMPLETE", type: "success" },
    { time: "08:12:08", msg: "ALPHA_LEAK: PREVENTED", type: "info" },
  ];

  return (
    <div className="bg-zinc-950 border border-white/5 rounded-2xl p-4 font-mono text-[10px] shadow-2xl">
      <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-2">
        <Terminal size={14} className="text-slate-500" />
        <span className="text-slate-300 font-bold tracking-tighter">VEYRA_ALPHA_TERMINAL</span>
      </div>

      <div className="space-y-2 mb-6">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3">
            <span className="text-slate-600">[{log.time}]</span>
            <span className={
              log.type === "success" ? "text-emerald-400" : 
              log.type === "warn" ? "text-amber-400" : "text-slate-300"
            }>
              {log.msg}
            </span>
          </div>
        ))}
        <div className="flex gap-3">
          <span className="text-slate-600">[08:12:10]</span>
          <span className="text-indigo-400 animate-pulse">_READY_FOR_COMMAND</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="p-2 bg-white/5 rounded border border-white/10">
          <div className="flex items-center gap-2 mb-1">
            <Database size={10} className="text-indigo-400" />
            <span className="text-[8px] text-slate-500">LEDGER_STATE</span>
          </div>
          <p className="text-white font-bold">STABLE</p>
        </div>
        <div className="p-2 bg-white/5 rounded border border-white/10">
          <div className="flex items-center gap-2 mb-1">
            <GitBranch size={10} className="text-violet-400" />
            <span className="text-[8px] text-slate-500">FORK_COUNT</span>
          </div>
          <p className="text-white font-bold">12.4K</p>
        </div>
      </div>
    </div>
  );
}
