/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Shield, Zap, Sparkles, Globe, Cpu, Infinity, Triangle } from "lucide-react";

export type TierType = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | "404";

interface BadgeProps {
  tier: TierType;
  size?: "sm" | "md" | "lg";
}

const tierMeta = {
  1: { name: "Foundation", color: "from-slate-400 to-slate-600", icon: Shield },
  2: { name: "Builder", color: "from-blue-400 to-blue-600", icon: Zap },
  3: { name: "Architect", color: "from-cyan-400 to-cyan-600", icon: Globe },
  4: { name: "Analyst", color: "from-emerald-400 to-emerald-600", icon: Cpu },
  5: { name: "Trader", color: "from-green-400 to-green-600", icon: Zap },
  6: { name: "Expert", color: "from-purple-400 to-purple-600", icon: Sparkles },
  7: { name: "Master", color: "from-indigo-400 to-indigo-600", icon: Sparkles },
  8: { name: "Elite", color: "from-rose-400 to-rose-600", icon: Shield },
  9: { name: "Visionary", color: "from-amber-400 to-amber-600", icon: Cpu },
  10: { name: "Transcendent", color: "from-violet-500 via-fuchsia-500 to-indigo-500", icon: Infinity },
  11: { name: "Divine", color: "from-yellow-200 via-amber-400 to-yellow-500", icon: Sparkles },
  12: { name: "Final", color: "from-zinc-900 via-slate-800 to-black", icon: Infinity },
  "404": { name: "Lost in Void", color: "from-red-500 to-red-800", icon: Triangle },
};

export function VeyraBadge({ tier, size = "md" }: BadgeProps) {
  const meta = tierMeta[tier];
  const Icon = meta.icon;

  const sizeClasses = {
    sm: "w-12 h-12 text-[10px]",
    md: "w-24 h-24 text-[12px]",
    lg: "w-48 h-48 text-[16px]",
  };

  return (
    <motion.div
      whileHover={{ scale: 1.05, rotate: 2 }}
      className={`relative flex flex-col items-center justify-center rounded-xl p-1 bg-gradient-to-br ${meta.color} shadow-lg ${sizeClasses[size]}`}
    >
      <div className="absolute inset-0.5 bg-black/80 rounded-[10px] flex flex-col items-center justify-center p-2 text-center">
        <Icon className="w-1/2 h-1/2 mb-1" style={{ color: "white" }} />
        <span className="font-mono font-bold text-white uppercase tracking-tighter opacity-80">
          {tier === "404" ? "ERR" : `T${tier}`}
        </span>
        <span className="text-[8px] font-sans font-medium text-white/60 uppercase leading-none mt-1">
          {meta.name}
        </span>
      </div>
      
      {/* Decorative inner borders or pulses for high tiers */}
      {(tier === 10 || tier === 11 || tier === 12) && (
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute inset-0 rounded-xl bg-white/20 blur-sm -z-10"
        />
      )}
    </motion.div>
  );
}
