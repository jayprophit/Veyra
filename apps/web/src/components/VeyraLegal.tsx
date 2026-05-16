import { 
  ShieldCheck, 
  Scaling, 
  Lock, 
  Scale, 
  AlertCircle,
  FileCheck,
  Globe,
  Gavel
} from "lucide-react";

export function VeyraLegal() {
  return (
    <div className="space-y-16 pb-24">
      {/* Legal Header */}
      <div className="bg-gradient-to-br from-[#0c0c0c] to-black border border-white/10 p-12 md:p-20 rounded-[3.5rem] relative overflow-hidden">
         <div className="absolute top-0 right-0 p-12 opacity-5">
            <Gavel size={320} className="text-white" />
         </div>
         <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-3 mb-6">
               <ShieldCheck size={24} className="text-emerald-500" />
               <p className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.4em]">Foundation Verification 0.1.0</p>
            </div>
            <h2 className="text-5xl md:text-7xl font-black italic tracking-tighter uppercase text-white mb-8">Legal_Framework</h2>
            <p className="text-base font-bold text-slate-500 leading-relaxed italic uppercase tracking-widest border-l-2 border-indigo-500/30 pl-8">
               THE VEYRA PROTOCOL OPERATES AS A DECENTRALIZED NODE INFRASTRUCTURE. BY ACCESSING THE TERMINAL, YOU ACKNOWLEDGE THE INHERENT RISKS OF SYNTHETIC ASSET TRADING AND PROTOCOL SYNTHESIS.
            </p>
         </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-12">
         {/* Terms Section */}
         <div className="space-y-8">
            <div className="flex items-center gap-4 mb-8">
               <Scale size={24} className="text-indigo-400" />
               <h3 className="text-2xl font-black italic uppercase tracking-tighter">Terms_Of_Service</h3>
            </div>
            {[
               { t: "01. Acceptance of Risk", d: "Trading synthetic assets carries high risk. Veyra Protocol does not provide financial advice. All node executions are final and non-reversible." },
               { t: "02. Node Integrity", d: "Users must maintain the security of their private keys and authentication hardware. Veyra is not responsible for losses due to compromised user identities." },
               { t: "03. Liquidity Oracles", d: "While we aim for 100% accuracy, node-level oracle discrepancies may occur during high volatility periods. Execution is based on aggregate kernel prices." },
               { t: "04. Regulatory Compliance", d: "Users are responsible for ensuring their use of the protocol complies with local jurisdiction laws and taxation requirements." }
            ].map((item, i) => (
               <div key={i} className="p-8 bg-[#0a0a0a] border border-white/10 rounded-[2.5rem] group hover:border-white/20 transition-all">
                  <h4 className="text-xs font-black italic uppercase text-indigo-400 mb-3 tracking-widest">{item.t}</h4>
                  <p className="text-sm font-bold text-slate-500 leading-relaxed italic uppercase">{item.d}</p>
               </div>
            ))}
         </div>

         {/* Privacy & Compliance Section */}
         <div className="space-y-8">
            <div className="flex items-center gap-4 mb-8">
               <Lock size={24} className="text-emerald-400" />
               <h3 className="text-2xl font-black italic uppercase tracking-tighter">Privacy_&_Data</h3>
            </div>
            <div className="bg-zinc-950 border border-white/10 rounded-[3rem] p-10 space-y-10">
               <div>
                  <h5 className="flex items-center gap-3 text-sm font-black uppercase tracking-widest text-white mb-4">
                     <Globe size={18} className="text-slate-600" /> Decentralized Identity
                  </h5>
                  <p className="text-xs font-bold text-slate-500 leading-relaxed uppercase italic">
                     WE DO NOT STORE PERSONALLY IDENTIFIABLE INFORMATION (PII). ALL IDENTITIES ARE HASHED VIA VEYRA_IDENTITY_PROTOCOL AND STORED ON-CHAIN. YOUR IP ADDRESS IS SCRUBBED VIA NODE-SPLICING.
                  </p>
               </div>
               <div className="h-px bg-white/5" />
               <div>
                  <h5 className="flex items-center gap-3 text-sm font-black uppercase tracking-widest text-white mb-4">
                     <Scaling size={18} className="text-slate-600" /> Data Retention
                  </h5>
                  <p className="text-xs font-bold text-slate-500 leading-relaxed uppercase italic">
                     TRANSACTION HISTORY IS RETAINED FOR PROTOCOL INTEGRITY AND CAN BE EXPORTED VIA THE SETTINGS MODULE. AUDIT LOGS ARE ENCRYPTED AND COMPLIANT WITH GLOBAL PRIVACY STANDARDS.
                  </p>
               </div>
               <div className="h-px bg-white/5" />
               <div className="p-6 bg-rose-500/5 border border-rose-500/20 rounded-2xl">
                  <div className="flex items-center gap-3 mb-4">
                     <AlertCircle size={18} className="text-rose-500" />
                     <h5 className="text-[10px] font-black uppercase tracking-widest text-rose-500">Risk Disclosure</h5>
                  </div>
                  <p className="text-[10px] font-mono text-rose-500/80 leading-relaxed uppercase">
                     PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS. LEVERAGED TRADING CARRIES A SIGNIFICANT RISK OF TOTAL LIQUIDATION. USE VEYRA_SAFETY_COILS AT ALL TIMES.
                  </p>
               </div>
            </div>

            <div className="flex items-center gap-4 p-8 bg-white/5 border border-white/10 rounded-[2.5rem]">
               <FileCheck size={32} className="text-indigo-500" />
               <div>
                  <p className="text-[10px] font-black text-white uppercase tracking-widest mb-1">Signed_Compliance_Cert</p>
                  <p className="text-[8px] font-mono text-slate-500 uppercase">NODE_V12_COMPLIANT // ISO_27001_EQUIVALENT</p>
               </div>
            </div>
         </div>
      </div>
    </div>
  );
}
