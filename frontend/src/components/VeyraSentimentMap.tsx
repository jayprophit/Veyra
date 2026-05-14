/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Globe, MapPin, Search } from "lucide-react";

export function VeyraSentimentMap() {
  const [activeDots, setActiveDots] = useState<number[]>([]);
  const dots = new Array(100).fill(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const count = Math.floor(Math.random() * 20) + 5;
      const indices = [];
      for(let i=0; i<count; i++) {
        indices.push(Math.floor(Math.random() * 100));
      }
      setActiveDots(indices);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0a0a0a] border border-white/5 rounded-3xl p-8 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-8 opacity-5">
        <Globe size={180} />
      </div>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] mb-1">Global Intelligence</h5>
          <h4 className="text-xl font-bold tracking-tighter italic uppercase">Sentiment_Pulse</h4>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
           <Search size={14} className="text-slate-500" />
           <span className="text-[10px] font-mono text-slate-400">SCANNING_NODES</span>
        </div>
      </div>

      <div className="grid grid-cols-10 gap-2 mb-8">
        {dots.map((_, i) => (
          <motion.div
            key={i}
            animate={{ 
              scale: activeDots.includes(i) ? [1, 1.2, 1] : 1,
              backgroundColor: activeDots.includes(i) ? '#6366f1' : '#1f2937'
            }}
            className="aspect-square rounded-sm transition-colors duration-1000"
          />
        ))}
      </div>

      <div className="space-y-4">
        {[
          { loc: "Europe Central", pulse: "Strong", color: "text-emerald-400" },
          { loc: "North America", pulse: "Volatile", color: "text-amber-400" },
          { loc: "Asia Pacific", pulse: "Dormant", color: "text-slate-500" },
        ].map((node, i) => (
          <div key={i} className="flex items-center justify-between group/line">
             <div className="flex items-center gap-3">
               <MapPin size={12} className="text-slate-600 group-hover/line:text-white transition-colors" />
               <span className="text-[11px] font-bold tracking-tight">{node.loc}</span>
             </div>
             <div className="flex items-center gap-2">
               <div className={`w-1 h-3 rounded-full ${node.color.replace('text-', 'bg-')}`}></div>
               <span className={`text-[9px] font-mono font-black uppercase ${node.color}`}>{node.pulse}</span>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
}
