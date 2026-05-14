import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Activity, 
  Terminal, 
  Cpu, 
  HardDrive, 
  ShieldAlert, 
  Zap, 
  Globe, 
  Search,
  ArrowRight,
  Code
} from "lucide-react";

interface LogEntry {
  id: string;
  time: string;
  level: 'info' | 'warn' | 'error' | 'critical';
  service: string;
  message: string;
}

export function VeyraDiagnostics() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    // Simulate real-time logs
    const services = ["AI_KERNEL", "NODE_BRIDGE", "ORACLE_FEED", "LIQUIDITY_LOCK", "IDENTITY_CORE"];
    const messages = [
      "Node handoff successful at [NODE_324]",
      "Latency spike detected in Frankfurt bridge",
      "Sovereign identity verified via hardware key",
      "Batch execution confirmed for block_92144",
      "Neural signal purity at 98.2%",
      "Buffer overflow attempt blocked from 192.x.x.x"
    ];

    const interval = setInterval(() => {
      const newLog: LogEntry = {
        id: Math.random().toString(36),
        time: new Date().toLocaleTimeString(),
        level: Math.random() > 0.8 ? 'warn' : Math.random() > 0.95 ? 'error' : 'info',
        service: services[Math.floor(Math.random() * services.length)],
        message: messages[Math.floor(Math.random() * messages.length)]
      };
      setLogs(prev => [newLog, ...prev].slice(0, 50));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const runDeepScan = () => {
    setIsScanning(true);
    setTimeout(() => setIsScanning(false), 3000);
  };

  return (
    <div className="space-y-12 pb-24">
      {/* Search Header */}
      <div className="relative group">
        <div className="absolute inset-y-0 left-8 flex items-center pointer-events-none">
          <Search className="text-slate-600 group-hover:text-indigo-400 transition-colors" size={24} />
        </div>
        <input 
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="DEEP_DIAGNOSTIC_SEARCH: ENTER_QUERY_OR_TXID..."
          className="w-full bg-[#0a0a0a] border-2 border-white/5 rounded-[3rem] py-10 pl-24 pr-40 text-xl font-black italic uppercase tracking-tighter text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-800"
        />
        <div className="absolute inset-y-4 right-4 group">
          <button 
            onClick={runDeepScan}
            disabled={isScanning}
            className="h-full px-10 bg-indigo-500 text-white rounded-[2rem] font-black uppercase text-xs tracking-widest hover:bg-indigo-400 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden relative"
          >
             <span className="relative z-10">{isScanning ? 'SCANNING_CLUSTER...' : 'RUN_FULL_ANALYSIS'}</span>
             {isScanning && (
               <motion.div 
                 initial={{ x: "-100%" }}
                 animate={{ x: "100%" }}
                 transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                 className="absolute inset-0 bg-white/20"
               />
             )}
          </button>
        </div>
      </div>

      {/* Grid Stats */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
         {[
           { label: "CPU_STABILITY", val: "99.2%", icon: Cpu, color: "text-emerald-400" },
           { label: "NODE_HEALTH", val: "NOMINAL", icon: Zap, color: "text-amber-400" },
           { label: "MEMORY_ISOLATION", val: "L3_SECURE", icon: HardDrive, color: "text-indigo-400" },
           { label: "ORACLE_LAG", val: "0.2ms", icon: Globe, color: "text-rose-400" }
         ].map((stat, i) => (
           <div key={i} className="bg-[#0a0a0a] border border-white/5 p-8 rounded-[2.5rem] relative group hover:bg-white/5 transition-all">
              <stat.icon size={20} className={`mb-4 ${stat.color}`} />
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest italic mb-1">{stat.label}</p>
              <h4 className="text-3xl font-black italic tracking-tighter text-white uppercase">{stat.val}</h4>
           </div>
         ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Real-time Web Log */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-white/5 rounded-[3rem] p-4 flex flex-col h-[600px] relative overflow-hidden">
           <div className="p-6 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                 <Terminal size={18} className="text-indigo-500" />
                 <h5 className="text-xs font-black text-white uppercase tracking-widest italic">Live_System_Telemetry</h5>
              </div>
              <div className="flex gap-1">
                 <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                 <div className="w-2 h-2 rounded-full bg-amber-500" />
                 <div className="w-2 h-2 rounded-full bg-emerald-500" />
              </div>
           </div>
           
           <div className="flex-1 p-6 overflow-y-auto space-y-3 font-mono text-[10px] scrollbar-hide">
              {logs.map((log) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={log.id} 
                  className={`flex items-start gap-4 p-3 rounded-xl border border-transparent hover:border-white/5 hover:bg-white/[0.02] transition-all group`}
                >
                   <span className="text-slate-700 font-bold shrink-0">{log.time}</span>
                   <span className={`font-black tracking-tighter uppercase px-2 py-0.5 rounded ${
                     log.level === 'error' ? 'bg-rose-500/10 text-rose-500' :
                     log.level === 'warn' ? 'bg-amber-500/10 text-amber-500' :
                     'bg-emerald-500/10 text-emerald-500'
                   }`}>[{log.level}]</span>
                   <span className="text-indigo-400 font-bold">[{log.service}]</span>
                   <span className="text-slate-400 italic">:: {log.message}</span>
                </motion.div>
              ))}
           </div>

           <div className="p-6 border-t border-white/5 flex items-center justify-between bg-black/40">
              <p className="text-[9px] font-black text-slate-700 uppercase tracking-widest italic">Node ID: PROPHIT_NODE_ALPHA_3242</p>
              <div className="flex items-center gap-2">
                 <Activity size={12} className="text-emerald-500 animate-bounce" />
                 <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest italic">Stream_Active</span>
              </div>
           </div>
        </div>

        {/* Diagnostic Actions */}
        <div className="space-y-6">
           <div className="bg-gradient-to-br from-indigo-500/10 to-violet-500/10 border border-indigo-500/20 p-10 rounded-[3rem]">
              <ShieldAlert size={32} className="text-indigo-400 mb-6" />
              <h5 className="text-xl font-black italic text-white uppercase tracking-tighter mb-4">Identity_Isolation</h5>
              <p className="text-[10px] font-bold text-slate-500 leading-relaxed uppercase italic italic mb-8">
                ENABLE HYPER-ISOLATED EXECUTION MODE. YOUR SESSION WILL BE DECOUPLED FROM PUBLIC WEB TRAFFIC AND ROUTED THROUGH QUANTUM-RESISTANT TUNNELS.
              </p>
              <button className="w-full py-4 bg-white text-black rounded-2xl font-black uppercase text-[10px] tracking-widest hover:bg-slate-200 transition-all">
                Enter_Stealth_State
              </button>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-10 rounded-[3rem]">
              <h5 className="text-xs font-black text-white uppercase tracking-widest mb-6 italic">Quick_Diagnostic_Scripts</h5>
              <div className="space-y-3">
                 {[
                   { label: "Trace_Network_Hop", icon: Globe },
                   { label: "Verify_Oracle_Proofs", icon: ShieldAlert },
                   { label: "Clear_Session_Tokens", icon: Zap },
                   { label: "Export_Node_Manifest", icon: Code }
                 ].map((item, i) => (
                   <button key={i} className="w-full flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-transparent hover:border-white/10 hover:bg-white/10 transition-all group">
                      <div className="flex items-center gap-4">
                         <item.icon size={16} className="text-slate-600 group-hover:text-indigo-400" />
                         <span className="text-[10px] font-black text-slate-400 group-hover:text-white uppercase tracking-widest italic">{item.label}</span>
                      </div>
                      <ArrowRight size={14} className="text-slate-800 group-hover:text-indigo-500 transition-transform group-hover:translate-x-1" />
                   </button>
                 ))}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
