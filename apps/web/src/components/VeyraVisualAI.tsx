/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { useEffect, useState } from "react";
import { Info } from "lucide-react";

export function VeyraVisualAI() {
  const [dataPoints, setDataPoints] = useState<number[]>([]);
  const [showTooltip, setShowTooltip] = useState(false);

  const scanData = {
    patterns: ["Double Top Liquidity", "Fair Value Gap", "Order Block Rejection"],
    confidence: "94.2%",
    neuralNodes: 124,
    latency: "0.02ms"
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setDataPoints(prev => {
        const next = [...prev, Math.random() * 100];
        if (next.length > 20) return next.slice(1);
        return next;
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black/60 border border-white/10 rounded-2xl p-6 font-mono overflow-hidden relative group">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
          <span className="text-[10px] text-cyan-400 uppercase tracking-widest font-bold">Visual AI Scanner</span>
        </div>
        <div className="flex items-center gap-2">
           <button 
             onMouseEnter={() => setShowTooltip(true)}
             onMouseLeave={() => setShowTooltip(false)}
             className="text-slate-600 hover:text-cyan-400 transition-colors"
           >
              <Info size={12} />
           </button>
           <span className="text-[8px] text-slate-500">BETA_V.0.9</span>
        </div>
      </div>

      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute top-12 right-6 left-6 bg-zinc-950 border border-white/10 rounded-xl p-4 shadow-2xl z-50 text-left pointer-events-none"
          >
            <div className="space-y-3">
              <h5 className="text-[9px] font-black text-cyan-400 uppercase tracking-widest italic border-b border-white/10 pb-2">Scan_Dossier_Alpha</h5>
              <div className="space-y-2">
                <div>
                  <p className="text-[7px] font-black text-slate-600 uppercase tracking-widest mb-1">Patterns_Detected</p>
                  <div className="flex flex-wrap gap-1">
                    {scanData.patterns.map(p => (
                      <span key={p} className="text-[7px] font-bold text-white bg-white/5 px-2 py-0.5 rounded-full">{p}</span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-1">
                  <div>
                    <p className="text-[7px] font-black text-slate-600 uppercase tracking-widest">Confidence</p>
                    <p className="text-[10px] font-black text-emerald-400 italic">{scanData.confidence}</p>
                  </div>
                  <div>
                    <p className="text-[7px] font-black text-slate-600 uppercase tracking-widest">Latency</p>
                    <p className="text-[10px] font-black text-amber-400 italic">{scanData.latency}</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="h-32 flex items-end gap-1 mb-4">
        {dataPoints.map((p, i) => (
          <motion.div
            key={i}
            initial={{ height: 0 }}
            animate={{ height: `${p}%` }}
            className="flex-1 bg-gradient-to-t from-cyan-900/40 to-cyan-400/80 rounded-t-sm"
          />
        ))}
      </div>

      <div className="space-y-1">
        <div className="flex justify-between items-center text-[9px]">
          <span className="text-slate-500 uppercase">Pattern_Match:</span>
          <span className="text-white font-bold">98.4%</span>
        </div>
        <div className="flex justify-between items-center text-[9px]">
          <span className="text-slate-500 uppercase">Engine_State:</span>
          <span className="text-emerald-400 font-bold">LEARNING</span>
        </div>
        <div className="flex justify-between items-center text-[9px]">
          <span className="text-slate-500 uppercase">VRA_Signal:</span>
          <span className="text-white font-bold">BULLISH_REVERSAL</span>
        </div>
      </div>
    </div>
  );
}
