import { useState } from "react";
import { motion } from "motion/react";
import { 
  Zap, 
  Shield, 
  Cpu, 
  Globe, 
  ChevronRight, 
  CheckCircle2, 
  CreditCard,
  Layers,
  ArrowUpRight
} from "lucide-react";

interface Plan {
  id: string;
  name: string;
  price: string;
  nodeLimit: string;
  latency: string;
  features: string[];
  color: string;
}

const plans: Plan[] = [
  {
    id: "standard",
    name: "Standard_Node",
    price: "$299",
    nodeLimit: "128 Nodes",
    latency: "24ms",
    features: ["Mirror Asset Sync", "Basic AI Forge", "Global Trading Access", "Community Node Support"],
    color: "slate"
  },
  {
    id: "professional",
    name: "Professional_Kernel",
    price: "$1,499",
    nodeLimit: "1,024 Nodes",
    latency: "1.2ms",
    features: ["Sub-Millisecond HFT", "Advanced Visual AI", "Private Extraction Lab", "24/7 Encrypted Bridge"],
    color: "indigo"
  },
  {
    id: "foundation",
    name: "Private_Alpha",
    price: "$9,999",
    nodeLimit: "Unlimited Nodes",
    latency: "0.2ms",
    features: ["Encrypted Workspace", "Bot Forge Slots", "Local Feed Access", "Dedicated Build Notes"],
    color: "emerald"
  }
];

export function VeyraMonetization() {
  const [selectedPlan, setSelectedPlan] = useState("professional");

  return (
    <div className="space-y-16 pb-24">
      {/* Header */}
      <header className="max-w-3xl">
         <h2 className="text-5xl md:text-7xl font-black italic tracking-tighter uppercase text-white mb-6">Revenue_Protocols</h2>
         <p className="text-base font-bold text-slate-500 uppercase italic tracking-widest leading-relaxed border-l-2 border-indigo-500/30 pl-8">
            SCALE YOUR NODE INFRASTRUCTURE THROUGH PRECISION KERNEL ALLOCATION. CHOOSE A PERFORMANCE TIER TAILORED TO YOUR EXECUTION FREQUENCY.
         </p>
      </header>

      {/* Pricing Grids */}
      <div className="grid lg:grid-cols-3 gap-10">
         {plans.map((plan) => (
           <div 
             key={plan.id}
             onClick={() => setSelectedPlan(plan.id)}
             className={`p-10 rounded-[3.5rem] border transition-all cursor-pointer relative overflow-hidden group ${
               selectedPlan === plan.id 
               ? 'bg-white/5 border-white/20 ring-4 ring-white/5 scale-105' 
               : 'bg-[#0a0a0a] border-white/5 hover:border-white/10'
             }`}
           >
              {plan.id === 'foundation' && (
                <div className="absolute top-0 right-0 p-8 text-emerald-500/10">
                   <Zap size={160} />
                </div>
              )}
              
              <div className="mb-12">
                 <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-2">{plan.name}</p>
                 <div className="flex items-baseline gap-2">
                    <h4 className="text-5xl font-black italic tracking-tighter text-white">{plan.price}</h4>
                    <span className="text-xs font-mono text-slate-600 uppercase">/Cycle</span>
                 </div>
              </div>

              <div className="space-y-8 mb-12">
                 <div className="flex items-center gap-4">
                    <Cpu size={18} className="text-slate-600" />
                    <div>
                       <p className="text-[10px] font-black text-white uppercase">{plan.nodeLimit}</p>
                       <p className="text-[8px] font-mono text-slate-600 uppercase">Capacity_Limit</p>
                    </div>
                 </div>
                 <div className="flex items-center gap-4">
                    <Globe size={18} className="text-slate-600" />
                    <div>
                       <p className="text-[10px] font-black text-white uppercase">{plan.latency}</p>
                       <p className="text-[8px] font-mono text-slate-600 uppercase">Sync_Fidelity</p>
                    </div>
                 </div>
              </div>

              <div className="space-y-4 mb-12">
                 {plan.features.map((f, i) => (
                   <div key={i} className="flex items-center gap-3">
                      <CheckCircle2 size={14} className={selectedPlan === plan.id ? 'text-indigo-400' : 'text-slate-700'} />
                      <span className="text-[10px] font-bold text-slate-400 uppercase italic">{f}</span>
                   </div>
                 ))}
              </div>

              <button className={`w-full py-5 rounded-2xl font-black uppercase text-[10px] tracking-widest transition-all ${
                selectedPlan === plan.id 
                ? 'bg-white text-black shadow-2xl hover:scale-105' 
                : 'bg-white/5 text-slate-500 hover:bg-white/10 hover:text-white'
              }`}>
                 Activate_Kernel
              </button>
           </div>
         ))}
      </div>

      {/* Corporate Features */}
      <div className="bg-[#0a0a0a] border border-white/5 rounded-[4rem] p-12 md:p-20 flex flex-col md:flex-row items-center justify-between gap-12">
         <div className="max-w-xl">
            <div className="flex items-center gap-3 mb-6">
               <Layers size={24} className="text-amber-500" />
               <p className="text-[10px] font-black text-amber-500 uppercase tracking-[0.4em]">Enterprise_Solution</p>
            </div>
            <h3 className="text-4xl font-black italic uppercase tracking-tighter text-white mb-6">Custom_Grid_Architect</h3>
            <p className="text-sm font-bold text-slate-500 leading-relaxed uppercase italic mb-10">
               Need a private cloud partition or sovereign node cluster? Our engineers can build a bespoke extraction environment with 0.00ms local hop latency.
            </p>
            <button className="flex items-center gap-4 text-white hover:text-indigo-400 transition-colors group">
               <span className="text-[12px] font-black uppercase tracking-[0.2em]">Contact_Engineers</span>
               <ArrowUpRight size={20} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            </button>
         </div>
         <div className="grid grid-cols-2 gap-4 w-full md:w-auto">
            {[
              { label: "Uptime", val: "100%" },
              { label: "SLA", val: "Grade_A" },
              { label: "Safety", val: "Coil_V4" },
              { label: "Nodes", val: "Static" }
            ].map((stat, i) => (
              <div key={i} className="p-8 bg-black/40 border border-white/5 rounded-3xl text-center">
                 <p className="text-[9px] font-mono text-slate-600 uppercase mb-1">{stat.label}</p>
                 <h5 className="text-xl font-black italic text-white uppercase">{stat.val}</h5>
              </div>
            ))}
         </div>
      </div>
    </div>
  );
}
