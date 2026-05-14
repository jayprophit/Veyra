import { CheckCircle2, Circle, Clock, ArrowUpRight, Zap, Target, Shield, Brain, Layers, Info } from "lucide-react";
import { motion } from "motion/react";
import { VeyraInfoBox } from "./VeyraInfoBox";

interface TodoItem {
  id: string;
  category: "CORE" | "TRADING" | "AI" | "DEFI";
  task: string;
  status: "completed" | "in-progress" | "backlog";
  description: string;
}

export function VeyraProjectStatus() {
  const todos: TodoItem[] = [
    {
      id: "1",
      category: "CORE",
      task: "Universal Navigation Shell",
      status: "completed",
      description: "High-performance sidebar with multi-view state management and active node search."
    },
    {
      id: "2",
      category: "TRADING",
      task: "Execution Terminal v1",
      status: "completed",
      description: "Advanced charting with multi-timeframe overlays and synthetic data generation kernel."
    },
    {
      id: "3",
      category: "AI",
      task: "Neural Bot Forge",
      status: "completed",
      description: "Agent deployment engine with allocation presets and advanced risk parameterization."
    },
    {
      id: "4",
      category: "AI",
      task: "Strategy Constructor",
      status: "completed",
      description: "Dynamic heuristic definition engine with entry/exit thresholds and volatility caps."
    },
    {
      id: "5",
      category: "TRADING",
      task: "Order Security Protocol",
      status: "completed",
      description: "Multi-layered confirmation modals for buy/sell execution to prevent fat-finger errors."
    },
    {
      id: "6",
      category: "CORE",
      task: "Per-Instance Telemetry",
      status: "completed",
      description: "Real-time execution logs and efficiency metrics for deep-dive logic auditing."
    },
    {
      id: "7",
      category: "AI",
      task: "Sentiment Intelligence",
      status: "completed",
      description: "Integrating NLP modules to ingest social 'heat' and adjust trade confidence thresholds."
    },
    {
      id: "8",
      category: "TRADING",
      task: "HFT WebSocket Node",
      status: "completed",
      description: "Transitioning to sub-millisecond price streams from global centralized exchanges."
    },
    {
      id: "9",
      category: "DEFI",
      task: "Multi-Chain Liquidity Vault",
      status: "completed",
      description: "Cross-chain asset bridging and automated yield-rebalacing across L2 networks."
    },
    {
      id: "10",
      category: "CORE",
      task: "Identity Hardening",
      status: "completed",
      description: "Biometric and hardware wallet authentication for high-value execution cycles."
    },
    {
      id: "11",
      category: "TRADING",
      task: "Professional Terminal",
      status: "completed",
      description: "Ultra-high performance trading interface with mirrored asset feeds and instant node execution."
    },
    {
      id: "12",
      category: "DEFI",
      task: "Universal Oracle",
      status: "completed",
      description: "Real-time cross-currency conversion matrix supporting 10+ fiat and crypto assets."
    },
    {
      id: "13",
      category: "CORE",
      task: "Industrial UI Re-Skin",
      status: "completed",
      description: "Mass-adoption design overhaul involving high-fidelity charts, bento grids, and pro-tier shadows."
    },
    {
      id: "14",
      category: "CORE",
      task: "Governance & Legal Shell",
      status: "completed",
      description: "Comprehensive risk disclosure, terms of service, and knowledge base integration."
    }
  ];

  const completedCount = todos.filter(t => t.status === 'completed').length;
  const progressPercent = Math.round((completedCount / todos.length) * 100);

  const getStatusIcon = (status: TodoItem["status"]) => {
    switch (status) {
      case "completed": return <CheckCircle2 className="text-emerald-500" size={18} />;
      case "in-progress": return <Clock className="text-amber-500 animate-pulse" size={18} />;
      case "backlog": return <Circle className="text-slate-700" size={18} />;
    }
  };

  const getCategoryColor = (cat: TodoItem["category"]) => {
    switch (cat) {
      case "CORE": return "text-blue-400 bg-blue-400/10";
      case "TRADING": return "text-emerald-400 bg-emerald-400/10";
      case "AI": return "text-indigo-400 bg-indigo-400/10";
      case "DEFI": return "text-rose-400 bg-rose-400/10";
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between">
        <div>
           <h3 className="text-3xl font-black italic tracking-tighter uppercase text-white mb-2">Protocol_Roadmap</h3>
           <p className="text-slate-500 text-sm font-mono uppercase tracking-[0.2em]">Development Status & Task Backlog</p>
        </div>
        <div className="text-right">
           <div className="text-4xl font-black italic tracking-tighter text-white mb-1">{progressPercent}%</div>
           <div className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Protocol Completion</div>
        </div>
      </div>

      <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${progressPercent}%` }}
          className="h-full bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.5)]"
        />
      </div>

      <div className="grid gap-4">
        {todos.map((todo, idx) => (
          <motion.div 
            key={todo.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`group p-6 rounded-[2rem] border transition-all ${todo.status === 'completed' ? 'bg-white/5 border-white/5' : 'bg-black border-white/10 hover:border-white/20'}`}
          >
            <div className="flex gap-6 items-start">
              <div className="pt-1">
                {getStatusIcon(todo.status)}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest ${getCategoryColor(todo.category)}`}>
                    {todo.category}
                  </span>
                  <h4 className={`text-sm font-bold uppercase tracking-tight ${todo.status === 'completed' ? 'text-slate-400 line-through' : 'text-white'}`}>
                    {todo.task}
                  </h4>
                </div>
                  <VeyraInfoBox 
                    label="Task_Metadata" 
                    value={todo.task} 
                    details={[
                      { label: "Assigned", value: "Neural_Link_01" },
                      { label: "Priority", value: "CRITICAL" },
                      { label: "Branch", value: "master_v12" }
                    ]}
                  >
                    <p className="text-xs text-slate-500 leading-relaxed max-w-2xl italic flex items-center gap-2 cursor-help group-hover:text-indigo-400 transition-colors">
                      <Info size={12} className="opacity-50" />
                      {todo.description}
                    </p>
                  </VeyraInfoBox>
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowUpRight className="text-slate-700" size={20} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid sm:grid-cols-3 gap-6 pt-8">
         <div className="p-8 bg-zinc-950 border border-white/5 rounded-[2.5rem]">
            <Zap className="text-amber-500 mb-6" size={32} />
            <h5 className="text-xl font-black italic tracking-tighter uppercase text-white mb-2">Next_Sprint</h5>
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Activating real-time node synchronization kernels.</p>
         </div>
         <div className="p-8 bg-zinc-950 border border-white/5 rounded-[2.5rem]">
            <Shield className="text-rose-500 mb-6" size={32} />
            <h5 className="text-xl font-black italic tracking-tighter uppercase text-white mb-2">Sec_Audit</h5>
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Firebase security rules penetration testing phase.</p>
         </div>
         <div className="p-8 bg-zinc-950 border border-white/5 rounded-[2.5rem]">
            <Target className="text-indigo-500 mb-6" size={32} />
            <h5 className="text-xl font-black italic tracking-tighter uppercase text-white mb-2">Phase_Final</h5>
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Full infrastructure deployment across multichain endpoints.</p>
         </div>
      </div>
    </div>
  );
}
