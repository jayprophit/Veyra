/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Volume2, Play, Square, Activity } from "lucide-react";

export function VeyraAudioAnalyzer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [bars, setBars] = useState<number[]>(new Array(40).fill(10));

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setBars(prev => prev.map(() => Math.random() * 80 + 10));
      }, 100);
    } else {
      setBars(new Array(40).fill(10));
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="bg-zinc-900 border border-white/5 rounded-3xl p-8 overflow-hidden relative group">
      <div className="absolute top-0 right-0 p-8 opacity-5">
        <Volume2 size={120} />
      </div>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] mb-1">Sonic Intelligence</h5>
          <h4 className="text-xl font-bold tracking-tighter italic">QUANTUM_AUDIO_SYNC</h4>
        </div>
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${isPlaying ? 'bg-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.4)]' : 'bg-white text-black'}`}
        >
          {isPlaying ? <Square size={20} fill="currentColor" /> : <Play size={20} className="ml-1" fill="currentColor" />}
        </button>
      </div>

      <div className="h-24 flex items-center gap-[2px]">
        {bars.map((height, i) => (
          <motion.div
            key={i}
            animate={{ height: `${height}%` }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className={`flex-1 rounded-full ${isPlaying ? 'bg-gradient-to-t from-indigo-500 via-violet-500 to-cyan-400' : 'bg-white/10'}`}
          />
        ))}
      </div>

      <div className="mt-8 grid grid-cols-3 gap-4 border-t border-white/5 pt-6">
        <div>
          <p className="text-[8px] text-slate-500 uppercase font-bold mb-1">Decibel Level</p>
          <div className="flex items-center gap-2">
            <Activity size={12} className="text-emerald-400" />
            <span className="text-xs font-mono font-bold tracking-tighter">-12.4 DB</span>
          </div>
        </div>
        <div>
          <p className="text-[8px] text-slate-500 uppercase font-bold mb-1">Frequency</p>
          <p className="text-xs font-mono font-bold tracking-tighter">44.1 KHZ</p>
        </div>
        <div className="text-right">
          <p className="text-[8px] text-slate-500 uppercase font-bold mb-1">Status</p>
          <p className={`text-xs font-mono font-bold tracking-tighter ${isPlaying ? 'text-emerald-400' : 'text-slate-600'}`}>
            {isPlaying ? "STREAMING" : "STANDBY"}
          </p>
        </div>
      </div>
    </div>
  );
}
