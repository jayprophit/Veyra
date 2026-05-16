/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Sparkles, Hexagon, Image as ImageIcon, ShoppingCart, Zap } from "lucide-react";
import { VeyraBadge } from "./VeyraBadge";

const identityItems = [
  { id: "VRA-9901", name: "Foundation Origin #01", tier: 12, price: "1,200", type: "Artifact" },
  { id: "VRA-4422", name: "Alpha Node Identity", tier: 10, price: "450", type: "Identity" },
  { id: "VRA-0012", name: "Visual AI Pattern 77", tier: 11, price: "890", type: "Pattern" },
];

export function VeyraIdentityDiscovery() {
  return (
    <div className="space-y-12">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
           <h3 className="text-3xl font-black tracking-tighter italic uppercase mb-2">Discovery Protocol</h3>
           <p className="text-slate-400 text-sm max-w-xl">A private workspace for Veyra identity artifacts and visual analysis patterns.</p>
        </div>
        <div className="flex gap-2">
           <button className="bg-white text-black px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest">Connect Wallet</button>
           <button className="bg-white/5 border border-white/10 text-white px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest">Inventory</button>
        </div>
      </header>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {identityItems.map((item) => (
          <div key={item.id} className="bg-zinc-900 border border-white/10 rounded-3xl overflow-hidden group hover:border-indigo-500/50 transition-all shadow-2xl">
            {/* Visual Preview */}
            <div className="aspect-square bg-[#050505] p-12 flex items-center justify-center relative overflow-hidden">
               <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-from)_0%,_transparent_70%)] from-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
               <VeyraBadge tier={item.tier as any} size="lg" />
               <div className="absolute top-4 right-4 bg-black/80 border border-white/10 px-3 py-1 rounded-full text-[9px] font-black text-indigo-400 uppercase tracking-widest backdrop-blur-md">
                 {item.type}
               </div>
            </div>

            {/* Info */}
            <div className="p-8">
               <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-bold text-lg italic tracking-tight">{item.name}</h4>
                    <p className="text-[10px] text-slate-500 font-mono">SERIAL: {item.id}</p>
                  </div>
                  <div className="w-10 h-10 bg-white/5 border border-white/5 rounded-xl flex items-center justify-center">
                    <Hexagon size={18} className="text-indigo-400" />
                  </div>
               </div>

               <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
                  <div className="flex items-center gap-2">
                     <span className="text-xs font-black italic">{item.price}</span>
                     <span className="text-[10px] font-bold text-slate-600 uppercase">VRA</span>
                  </div>
                  <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-colors">
                    <ShoppingCart size={14} />
                    Acquire
                  </button>
               </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gradient-to-br from-indigo-900/20 via-transparent to-transparent border border-white/5 p-12 rounded-[3rem] text-center">
         <Sparkles className="mx-auto text-indigo-400 mb-6" size={40} />
         <h3 className="text-3xl font-black italic tracking-tighter mb-4 uppercase">Identity Crafting</h3>
         <p className="text-slate-400 text-sm max-w-lg mx-auto leading-relaxed mb-8">
           COMMUNITY MEMBERS ARE ELIGIBLE TO CRAFT CUSTOM IDENTITY CARDS UPON REACHING TIER 8 (ELITE). FORGE YOUR MARK ON THE VEYRA LEDGER.
         </p>
         <button className="bg-white text-black px-10 py-4 rounded-full text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:scale-105 transition-transform">
           Start Crafting
         </button>
      </div>
    </div>
  );
}
