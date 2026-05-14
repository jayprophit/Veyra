/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";

interface VeyraLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function VeyraLogo({ size = "md", className = "" }: VeyraLogoProps) {
  const sizes = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-16 h-16",
    xl: "w-24 h-24"
  };

  return (
    <div className={`relative ${sizes[size]} ${className} group`}>
      {/* Outer Glow */}
      <motion.div 
        animate={{ 
          scale: [1, 1.05, 1],
          opacity: [0.5, 0.8, 0.5] 
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
        className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full"
      />
      
      {/* Main Logo Container */}
      <div className="relative w-full h-full flex items-center justify-center">
        <svg 
          viewBox="0 0 100 100" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-[0_0_15px_rgba(99,102,241,0.3)]"
        >
          <defs>
            {/* Metallic Silver Gradient */}
            <linearGradient id="silver-grad" x1="0" y1="0" x2="0" y2="100">
              <stop offset="0%" stopColor="#e2e8f0" />
              <stop offset="50%" stopColor="#94a3b8" />
              <stop offset="100%" stopColor="#475569" />
            </linearGradient>

            {/* Glowing Green Gradient */}
            <linearGradient id="green-grad" x1="0" y1="0" x2="100" y2="100">
              <stop offset="0%" stopColor="#4ade80" />
              <stop offset="50%" stopColor="#22c55e" />
              <stop offset="100%" stopColor="#15803d" />
            </linearGradient>

            {/* Circuit Line Mask */}
            <pattern id="circuit-pattern" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
              <path d="M 0 5 L 10 5 M 5 0 L 5 10" stroke="white" strokeWidth="0.5" opacity="0.3" />
            </pattern>
          </defs>

          {/* Background Shadow Shape */}
          <path 
            d="M20 20 L50 85 L80 20 L70 20 L50 65 L30 20 Z" 
            fill="#050505" 
            filter="blur(2px)"
          />

          {/* Left Wing (Silver Metallic) */}
          <motion.path 
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            d="M15 15 L50 90 L50 70 L30 15 Z" 
            fill="url(#silver-grad)"
            className="stroke-slate-200"
            strokeWidth="0.5"
          />

          {/* Right Wing (Glowing Tech Green) */}
          <motion.path 
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, delay: 0.2, ease: "easeOut" }}
            d="M85 15 L50 90 L50 70 L70 15 Z" 
            fill="url(#green-grad)"
            className="stroke-emerald-400"
            strokeWidth="0.5"
          >
            <animate 
              attributeName="fill" 
              values="url(#green-grad);#4ade80;url(#green-grad)" 
              dur="3s" 
              repeatCount="indefinite" 
            />
          </motion.path>

          {/* Central Blue Sphere Core */}
          <motion.circle 
            animate={{ 
              scale: [0.9, 1.1, 0.9],
              opacity: [0.8, 1, 0.8] 
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              ease: "easeInOut" 
            }}
            cx="50" cy="45" r="8" 
            fill="#38bdf8" 
            className="drop-shadow-[0_0_10px_#38bdf8]"
          />
          
          <circle cx="50" cy="45" r="4" fill="white" className="blur-[1px]" />
        </svg>
      </div>

      {/* Speed Lines / Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            animate={{ 
              y: [-10, 20],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              delay: i * 0.6,
              ease: "easeOut" 
            }}
            className="absolute w-0.5 h-4 bg-indigo-400/30 rounded-full"
            style={{ 
              left: `${30 + (i * 20)}%`, 
              top: '20%' 
            }}
          />
        ))}
      </div>
    </div>
  );
}
