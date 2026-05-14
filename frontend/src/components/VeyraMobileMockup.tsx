/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Smartphone, CheckCircle, Eye, Accessibility } from "lucide-react";

export function VeyraMobileMockup() {
  return (
    <div className="bg-black/80 border border-white/10 rounded-2xl p-6 relative overflow-hidden group">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
          <Smartphone size={20} className="text-slate-300" />
        </div>
        <div>
          <h5 className="text-[10px] font-bold text-white uppercase tracking-widest">Mobile Accessibility</h5>
          <p className="text-[8px] text-slate-500 font-mono">WCAG 2.1 COMPLIANCE: AA+</p>
        </div>
      </div>

      <div className="relative flex justify-center py-4">
        {/* Phone Frame */}
        <div className="w-32 h-56 border-4 border-slate-800 rounded-[2rem] p-2 relative bg-black shadow-2xl">
          <div className="w-12 h-1 bg-slate-800 rounded-full mx-auto mb-4 mt-2"></div>
          
          <div className="space-y-2">
            <div className="h-6 w-full bg-indigo-600 rounded-md"></div>
            <div className="h-2 w-2/3 bg-white/10 rounded-full"></div>
            <div className="h-2 w-full bg-white/5 rounded-full"></div>
            <div className="grid grid-cols-2 gap-1 mt-4">
              <div className="h-12 bg-white/5 rounded-lg border border-white/10"></div>
              <div className="h-12 bg-white/5 rounded-lg border border-white/10"></div>
            </div>
          </div>

          {/* Accessibility Indicator */}
          <div className="absolute -right-4 top-1/2 -translate-y-12 bg-emerald-500 p-2 rounded-full shadow-lg">
             <Accessibility size={16} className="text-black" />
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-2">
        <div className="flex items-center gap-2 text-[9px] text-slate-400">
           <CheckCircle size={10} className="text-emerald-500" />
           <span>High Contrast Text (4.5:1+)</span>
        </div>
        <div className="flex items-center gap-2 text-[9px] text-slate-400">
           <CheckCircle size={10} className="text-emerald-500" />
           <span>Screen Reader Optimized</span>
        </div>
        <div className="flex items-center gap-2 text-[9px] text-slate-400">
           <Eye size={10} className="text-cyan-500" />
           <span>Visual Learning Overlays</span>
        </div>
      </div>
    </div>
  );
}
