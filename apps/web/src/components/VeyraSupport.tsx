import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  HelpCircle, 
  Book, 
  Terminal, 
  ShieldAlert, 
  Zap, 
  ChevronDown, 
  Search,
  MessageSquare,
  FileText,
  LifeBuoy
} from "lucide-react";

const faqs = [
  {
    category: "PROTOCOL",
    q: "How does Veyra achieve 2.4ms execution latency?",
    a: "Veyra utilizes a proprietary node-mesh architecture that bypasses standard RPC routing, establishing direct peer-to-peer tunnels with liquidity kernels globally."
  },
  {
    category: "ASSETS",
    q: "What are 'Mirror Assets' and how are they collateralized?",
    a: "Mirror Assets are synthetic representations of traditional equities and bonds, backed 1:1 by Veyra Protocol's decentralized reserve pool (DRP) and verified via real-time proof-of-reserve oracles."
  },
  {
    category: "SECURITY",
    q: "Is my data encrypted during cross-node migration?",
    a: "Yes. All packet transmission uses the Veyra_Protocol_v12 standard, featuring AES-256-GCM quantum-resistant encryption and hardware-level isolation."
  },
  {
    category: "FEES",
    q: "What is the fee structure for the Professional Terminal?",
    a: "Standard tier users enjoy 0% maker fees. Taker fees are scaled based on VRA token holdings, with a maximum cap of 0.05% per execution cycle."
  }
];

export function VeyraSupport() {
  const [activeItem, setActiveItem] = useState<number | null>(0);
  const [search, setSearch] = useState("");

  return (
    <div className="space-y-12 pb-24">
      {/* Search Hero */}
      <div className="bg-[#0a0a0a] border border-white/10 rounded-[3.5rem] p-12 md:p-20 relative overflow-hidden">
         <div className="absolute top-0 right-0 p-12 opacity-5">
            <LifeBuoy size={320} className="text-white" />
         </div>
         <div className="relative z-10 max-w-2xl">
            <h2 className="text-4xl md:text-6xl font-black italic tracking-tighter uppercase text-white mb-6">Knowledge_Base</h2>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-10 leading-relaxed italic">
               Access the Veyra Protocol documentation, technical specifications, and node troubleshooting manuals.
            </p>
            <div className="relative">
               <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-600" size={20} />
               <input 
                 type="text" 
                 placeholder="Search protocols, fees, or architecture..." 
                 className="w-full bg-black border border-white/10 rounded-2xl py-6 pl-16 pr-8 text-white font-mono text-sm focus:border-indigo-500 transition-all outline-none"
                 value={search}
                 onChange={e => setSearch(e.target.value)}
               />
            </div>
         </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-12">
        {/* Guides Column */}
        <div className="lg:col-span-4 space-y-6">
           <h5 className="text-[10px] font-black uppercase text-slate-500 tracking-[0.4em] mb-4">Support_Modules</h5>
           {[
             { title: "Technical Whitepaper", icon: Book, sub: "V12.0_REVISION" },
             { title: "Terminal User Guide", icon: Terminal, sub: "PRO_VERSION_3" },
             { title: "Node Setup Manual", icon: Zap, sub: "FEDERATED_GRID" },
             { title: "Risk Management", icon: ShieldAlert, sub: "SAFE_EXECUTION" },
           ].map((g, i) => (
             <button key={i} className="w-full flex items-center justify-between p-6 bg-white/5 border border-white/10 rounded-[2rem] hover:bg-white/10 transition-all group">
                <div className="flex items-center gap-4">
                   <div className="w-12 h-12 bg-black border border-white/5 rounded-2xl flex items-center justify-center text-slate-400 group-hover:text-indigo-400 group-hover:border-indigo-500/30 transition-all">
                      <g.icon size={20} />
                   </div>
                   <div className="text-left">
                      <p className="text-sm font-black italic text-white uppercase">{g.title}</p>
                      <p className="text-[9px] font-mono text-slate-600">{g.sub}</p>
                   </div>
                </div>
                <FileText size={16} className="text-slate-700" />
             </button>
           ))}

           <div className="p-8 bg-indigo-600 rounded-[2.5rem] text-white shadow-2xl mt-12 relative overflow-hidden group">
              <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform">
                 <MessageSquare size={96} />
              </div>
              <h5 className="text-xl font-black italic tracking-tighter uppercase mb-4">Direct Sync</h5>
              <p className="text-[10px] font-bold text-indigo-100 uppercase mb-8">
                 Need immediate node assistance? Connect with a protocol specialist in the encrypted bridge.
              </p>
              <button className="w-full py-4 bg-white text-indigo-600 rounded-2xl font-black uppercase tracking-widest text-[10px]">
                 Open_Support_Link
              </button>
           </div>
        </div>

        {/* FAQ Column */}
        <div className="lg:col-span-8 flex flex-col gap-4">
           <h5 className="text-[10px] font-black uppercase text-slate-500 tracking-[0.4em] mb-4">Frequently_Asked_Queries</h5>
           {faqs.map((f, i) => (
             <div key={i} className={`border border-white/5 rounded-[2.5rem] transition-all overflow-hidden ${activeItem === i ? 'bg-white/5 border-white/20' : 'bg-[#0a0a0a]'}`}>
               <button 
                 onClick={() => setActiveItem(activeItem === i ? null : i)}
                 className="w-full p-8 flex items-center justify-between group"
               >
                 <div className="flex items-center gap-6">
                    <span className="text-[10px] font-mono text-slate-600 uppercase tracking-widest">{f.category}</span>
                    <h4 className="text-lg font-black italic text-white group-hover:text-indigo-400 transition-colors uppercase">{f.q}</h4>
                 </div>
                 <ChevronDown size={20} className={`text-slate-700 transition-transform ${activeItem === i ? 'rotate-180' : ''}`} />
               </button>
               <AnimatePresence>
                 {activeItem === i && (
                   <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                   >
                     <div className="px-8 pb-8 pt-2">
                        <div className="w-full h-px bg-white/5 mb-6" />
                        <p className="text-sm font-bold text-slate-500 leading-relaxed italic uppercase tracking-wider">
                           {f.a}
                        </p>
                     </div>
                   </motion.div>
                 )}
               </AnimatePresence>
             </div>
           ))}
        </div>
      </div>
    </div>
  );
}
