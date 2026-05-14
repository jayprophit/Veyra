/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Copy, Check } from "lucide-react";
import React, { useState, Fragment } from "react";

interface ShieldProps {
  label: string;
  value: string;
  color: string;
}

export function VeyraShield({ label, value, color }: ShieldProps) {
  return (
    <div className="inline-flex items-center font-mono text-[10px] h-6 overflow-hidden rounded shadow-sm border border-white/5">
      <div className="bg-[#555] text-white px-2 py-1 uppercase tracking-tighter h-full flex items-center">
        {label}
      </div>
      <div 
        className="px-2 py-1 text-white font-bold h-full flex items-center"
        style={{ backgroundColor: color }}
      >
        {value}
      </div>
    </div>
  );
}

export function VeyraREADMEAssets() {
  const [copied, setCopied] = useState(false);
  const markdown = `[![Veyra License](https://img.shields.io/badge/License-Apache_2.0-red.svg)](LICENSE)\n[![Tier Achievement](https://img.shields.io/badge/Tier-Transcendent-blueviolet.svg)](#tiers)`;

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-zinc-900 border border-white/10 rounded-2xl p-8">
      <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6">README Shield Kit</h5>
      
      <div className="flex flex-wrap gap-4 mb-8">
        <VeyraShield label="License" value="Apache-2.0" color="#D22" />
        <VeyraShield label="Build" value="Passing" color="#4c1" />
        <VeyraShield label="Version" value="12.4.0-Final" color="#007ec6" />
        <VeyraShield label="Tier" value="Transcendent" color="#9c27b0" />
      </div>

      <div className="bg-black/60 rounded-xl p-4 border border-white/5 relative group">
        <p className="text-[9px] text-slate-500 mb-2 font-mono">MARKDOWN SNIPPET:</p>
        <code className="text-indigo-400 text-[10px] break-all leading-relaxed block pr-12">
          {markdown.split('\n').map((line, i) => (
            <Fragment key={i}>
              {line}
              {i === 0 && <br/>}
            </Fragment>
          ))}
        </code>
        <button 
          onClick={handleCopy}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-all text-slate-400 hover:text-white"
        >
          {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}
