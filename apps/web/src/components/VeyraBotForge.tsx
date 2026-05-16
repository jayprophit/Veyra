import { motion, AnimatePresence } from "motion/react";
import { 
  Cpu, 
  Play, 
  Pause, 
  Zap, 
  BarChart3, 
  Database, 
  Plus, 
  Trash2, 
  Settings2, 
  Activity, 
  ShieldAlert,
  ChevronRight,
  TrendingUp,
  X,
  Target,
  Brain,
  Layers,
  ArrowRight
} from "lucide-react";
import { useState, useEffect } from "react";

interface BotStrategy {
  id: string;
  name: string;
  type: 'momentum' | 'arbitrage' | 'mean-reversion' | 'neural';
  riskLevel: 'low' | 'med' | 'high';
  description: string;
  entryThreshold: number;
  exitThreshold: number;
  maxTradesPerDay: number;
}

const INITIAL_STRATEGIES: BotStrategy[] = [
  { 
    id: 'S1', 
    name: 'Momentum_Core',
    type: 'momentum', 
    riskLevel: 'high', 
    description: 'Transformer-based trend identification with high-leverage execution.',
    entryThreshold: 0.85,
    exitThreshold: 0.92,
    maxTradesPerDay: 50
  },
  { 
    id: 'S2', 
    name: 'LST_Arbitrage', 
    type: 'arbitrage', 
    riskLevel: 'low', 
    description: 'Sub-millisecond cross-exchange price discrepancy exploitation.',
    entryThreshold: 0.15,
    exitThreshold: 0.05,
    maxTradesPerDay: 5000
  },
  { 
    id: 'S3', 
    name: 'Veyra_Equilibrium', 
    type: 'mean-reversion', 
    riskLevel: 'med', 
    description: 'Statistical mean-reversion using Bayesian neural networks.',
    entryThreshold: 0.65,
    exitThreshold: 0.45,
    maxTradesPerDay: 120
  },
];

interface LogEntry {
  timestamp: string;
  message: string;
}

interface BotInstance {
  id: string;
  name: string;
  status: 'RUNNING' | 'STANDBY' | 'OPTIMIZING';
  strategyId: string;
  allocation: number;
  stopLoss: number;
  takeProfit: number;
  profit: string;
  efficiency: number;
  logs: LogEntry[];
}

export function VeyraBotForge() {
  const [strategies, setStrategies] = useState<BotStrategy[]>(INITIAL_STRATEGIES);
  const [bots, setBots] = useState<BotInstance[]>([
    { 
      id: "A-01", 
      name: "Alpha_Scout", 
      status: "RUNNING", 
      strategyId: 'S1',
      allocation: 2500,
      stopLoss: 2.5,
      takeProfit: 5.0,
      profit: "+12.4%", 
      efficiency: 98,
      logs: [
        { timestamp: "08:42:15", message: "Detecting trend inertia..." },
        { timestamp: "08:42:18", message: "Order placed at $42,150" },
        { timestamp: "08:42:20", message: "Neural validation: SUCCESS" }
      ]
    },
    { 
      id: "V-12", 
      name: "Private_Node",
      status: "OPTIMIZING", 
      strategyId: 'S3',
      allocation: 5000,
      stopLoss: 1.5,
      takeProfit: 3.5,
      profit: "+28.9%", 
      efficiency: 99,
      logs: [
        { timestamp: "08:42:01", message: "Recalibrating weight gates..." },
        { timestamp: "08:42:05", message: "Backtesting 2.4M scenarios" },
        { timestamp: "08:42:10", message: "Epoch 452 relative loss: 0.002" }
      ]
    },
  ]);

  const [isCreating, setIsCreating] = useState(false);
  const [isDefiningStrategy, setIsDefiningStrategy] = useState(false);
  const [selectedBot, setSelectedBot] = useState<BotInstance | null>(null);
  
  const [newStrategy, setNewStrategy] = useState<Partial<BotStrategy>>({
    name: "Custom_Neural_Path",
    type: 'neural',
    riskLevel: 'med',
    description: "Multi-layered perception model for volatile market conditions.",
    entryThreshold: 0.75,
    exitThreshold: 0.25,
    maxTradesPerDay: 100
  });

  const [newBot, setNewBot] = useState<Partial<BotInstance>>({
    name: "New_Agent",
    strategyId: 'S1',
    allocation: 1000,
    stopLoss: 2.0,
    takeProfit: 4.0
  });

  const handleCreateBot = () => {
    const bot: BotInstance = {
      id: `${String.fromCharCode(65 + Math.floor(Math.random() * 26))}-${Math.floor(100 + Math.random() * 899)}`,
      name: newBot.name || "Unnamed_Agent",
      status: 'STANDBY',
      strategyId: newBot.strategyId || strategies[0].id,
      allocation: newBot.allocation || 1000,
      stopLoss: newBot.stopLoss || 2.0,
      takeProfit: newBot.takeProfit || 4.0,
      profit: "0.0%",
      efficiency: 0,
      logs: [{ 
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }), 
        message: "Initialized. Waiting for activation..." 
      }]
    };
    setBots([...bots, bot]);
    setIsCreating(false);
  };

  const handleCreateStrategy = () => {
    const strategy: BotStrategy = {
      id: `S-${Math.floor(1000 + Math.random() * 9000)}`,
      name: newStrategy.name || "Custom_Strategy",
      type: newStrategy.type || 'neural',
      riskLevel: newStrategy.riskLevel || 'med',
      description: newStrategy.description || "",
      entryThreshold: newStrategy.entryThreshold || 0.5,
      exitThreshold: newStrategy.exitThreshold || 0.5,
      maxTradesPerDay: newStrategy.maxTradesPerDay || 100
    };
    setStrategies([...strategies, strategy]);
    setIsDefiningStrategy(false);
  };

  const deleteBot = (id: string) => {
    setBots(bots.filter(b => b.id !== id));
    if (selectedBot?.id === id) setSelectedBot(null);
  };

  const toggleBotStatus = (id: string) => {
    setBots(bots.map(b => {
      if (b.id === id) {
        return { ...b, status: b.status === 'RUNNING' ? 'STANDBY' : 'RUNNING' };
      }
      return b;
    }));
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
           <h3 className="text-3xl font-black italic tracking-tighter uppercase text-white mb-2">Neural_Cluster</h3>
           <p className="text-slate-500 text-sm font-mono uppercase tracking-[0.2em]">Active Computational Agents: {bots.length}</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setIsDefiningStrategy(true)}
            className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-6 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-3 transition-all active:scale-95"
          >
            <Settings2 size={18} />
            Define_Strategy
          </button>
          <button 
            onClick={() => setIsCreating(true)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-3 transition-all active:scale-95 shadow-xl shadow-indigo-600/20"
          >
            <Plus size={18} />
            Create_New_Agent
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map((bot) => (
          <motion.div 
            layout
            key={bot.id} 
            className={`bg-[#0a0a0a] border ${selectedBot?.id === bot.id ? 'border-indigo-500/50 shadow-[0_0_30px_rgba(99,102,241,0.1)]' : 'border-white/10'} rounded-3xl p-6 relative overflow-hidden group transition-all`}
          >
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <Cpu size={84} />
            </div>
            
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className={`p-4 rounded-2xl ${bot.status === 'RUNNING' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                   {bot.status === 'RUNNING' ? <Activity size={20} className="animate-pulse" /> : <Zap size={20} />}
                </div>
                <div>
                   <h4 className="font-bold text-lg text-white italic tracking-tight">{bot.name}</h4>
                   <p className="text-[10px] text-slate-500 font-mono flex items-center gap-2">
                     <Target size={12} className="text-indigo-500" />
                     {strategies.find(s => s.id === bot.strategyId)?.name}
                   </p>
                </div>
              </div>
              <div className="text-right">
                 <p className={`text-lg font-black italic ${bot.profit.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'} font-mono`}>{bot.profit}</p>
                 <p className="text-[9px] text-slate-600 uppercase font-black tracking-tighter">Realized_Delta</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
               <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                  <p className="text-[9px] text-slate-500 uppercase font-black mb-1">Max Allocation</p>
                  <p className="text-sm font-bold text-white italic">${bot.allocation.toLocaleString()}</p>
               </div>
               <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                  <p className="text-[9px] text-slate-500 uppercase font-black mb-1">Risk Bounds</p>
                  <div className="flex items-center gap-2 text-xs">
                     <span className="text-rose-400 font-bold">-{bot.stopLoss}%</span>
                     <span className="text-slate-700">/</span>
                     <span className="text-emerald-400 font-bold">+{bot.takeProfit}%</span>
                  </div>
               </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center text-[10px] font-mono">
                 <span className="text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <Brain size={12} className="text-indigo-400" />
                   Neural Reliability
                 </span>
                 <span className="text-white font-bold">{bot.efficiency}%</span>
              </div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                 <motion.div 
                   initial={{ width: 0 }}
                   animate={{ width: `${bot.efficiency}%` }}
                   className={`h-full ${bot.efficiency > 90 ? 'bg-indigo-500' : 'bg-amber-500'}`} 
                 />
              </div>
            </div>

            {/* Micro Terminal */}
            <div className="bg-black/40 rounded-xl p-3 mb-6 font-mono text-[9px] border border-white/5 space-y-1">
              {bot.logs.slice(-2).map((log, i) => (
                <div key={i} className="flex gap-2">
                  <span className="text-slate-700 shrink-0">[{log.timestamp}]</span>
                  <span className="text-slate-400 truncate tracking-tight">{log.message}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
               <button 
                 onClick={() => toggleBotStatus(bot.id)}
                 className="flex-[2] bg-white text-black py-4 rounded-2xl text-[10px] font-black uppercase flex items-center justify-center gap-2 hover:bg-slate-200 transition-colors"
               >
                 {bot.status === 'RUNNING' ? <Pause size={14} fill="currentColor" /> : <Play size={14} fill="currentColor" />}
                 {bot.status === 'RUNNING' ? 'Shutdown' : 'Engage'}
               </button>
               <button 
                 onClick={() => setSelectedBot(bot)}
                 className="flex-1 bg-white/5 border border-white/10 rounded-2xl text-white hover:bg-white/10 flex items-center justify-center transition-colors"
               >
                 <Settings2 size={16} />
               </button>
               <button 
                onClick={() => deleteBot(bot.id)}
                className="flex-1 bg-rose-500/10 border border-rose-500/20 text-rose-500 rounded-2xl hover:bg-rose-500 hover:text-white transition-all flex items-center justify-center"
               >
                 <Trash2 size={16} />
               </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Bot Setting / Log Detail Drawer (Simple representation) */}
      <AnimatePresence>
        {selectedBot && (
          <div className="fixed inset-0 z-50 flex items-end justify-end pointer-events-none p-6">
            <motion.div 
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              className="w-full max-w-md bg-[#0d0d0d] border border-white/10 shadow-2xl rounded-3xl h-[80vh] pointer-events-auto overflow-hidden flex flex-col"
            >
              <div className="p-6 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-4">
                   <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30">
                     <Brain size={24} className="text-indigo-400" />
                   </div>
                   <div>
                     <h3 className="text-xl font-black italic tracking-tighter uppercase text-white">{selectedBot.name}</h3>
                     <p className="text-[10px] text-slate-500 font-mono">NODE_IDENTITY: {selectedBot.id}</p>
                   </div>
                </div>
                <button onClick={() => setSelectedBot(null)} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                  <X size={20} className="text-slate-500" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-8">
                 <section>
                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-4 flex items-center justify-between">
                       <span className="flex items-center gap-2"><Activity size={14} /> Execution_Logs</span>
                       <span className="text-[8px] text-slate-700">SCROLL_FOR_HISTORY</span>
                    </h5>
                    <div className="bg-black border border-white/5 rounded-2xl p-4 font-mono text-[11px] space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                       {selectedBot.logs.map((log, i) => (
                         <div key={i} className="flex gap-3 border-b border-white/5 pb-2 last:border-0 last:pb-0">
                           <span className="text-slate-700 shrink-0">[{log.timestamp}]</span>
                           <span className="text-slate-300 italic leading-relaxed">{log.message}</span>
                         </div>
                       ))}
                       <div className="flex gap-3 text-emerald-500 animate-pulse pt-1">
                         <span className="shrink-0">[{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}]</span>
                         <span className="font-bold">Awaiting next inference cycle...</span>
                       </div>
                    </div>
                 </section>

                 <section>
                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-4 flex items-center gap-2">
                       <Settings2 size={14} /> Live_Parameters
                    </h5>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label className="text-[10px] text-slate-600 uppercase font-bold">Max Drawdown Guard (%)</label>
                        <div className="flex items-center gap-4">
                           <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                              <div className="h-full bg-rose-500 w-[15%]" />
                           </div>
                           <span className="text-xs font-mono text-rose-400">15.0</span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-[10px] text-slate-600 uppercase font-bold">Inference Confidence Threshold</label>
                        <div className="flex items-center gap-4">
                           <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-500 w-[85%]" />
                           </div>
                           <span className="text-xs font-mono text-emerald-400">0.85</span>
                        </div>
                      </div>
                    </div>
                 </section>

                 <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-2xl p-4 flex items-center gap-4">
                    <ShieldAlert size={20} className="text-indigo-400 shrink-0" />
                    <p className="text-[10px] text-slate-400 leading-relaxed italic">
                      "Agent security protocols are active. All trades routed through decentralized dark-pool proxies to prevent front-running."
                    </p>
                 </div>
              </div>
              
              <div className="p-6 bg-black/40 border-t border-white/10">
                <button className="w-full py-4 bg-white text-black rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-200 transition-all flex items-center justify-center gap-2">
                  Update_Neural_Weights
                  <ArrowRight size={14} />
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Create Modal */}
      <AnimatePresence>
        {isDefiningStrategy && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-12">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsDefiningStrategy(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-xl"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-2xl bg-[#0d0d0d] border border-white/10 rounded-[2.5rem] shadow-2xl relative z-10 overflow-hidden"
            >
              <div className="p-8 md:p-12">
                 <div className="flex justify-between items-start mb-10">
                    <div>
                      <h3 className="text-4xl font-black italic tracking-tighter uppercase text-white mb-2">Strategy_Constructor</h3>
                      <p className="text-slate-500 text-sm font-mono tracking-widest">DEFINING NEW COMPUTATIONAL HEURISTICS</p>
                    </div>
                    <button 
                      onClick={() => setIsDefiningStrategy(false)}
                      className="p-3 bg-white/5 border border-white/10 rounded-full text-slate-400 hover:text-white transition-colors"
                    >
                      <X size={20} />
                    </button>
                 </div>

                 <div className="space-y-8">
                    <div className="grid md:grid-cols-2 gap-6">
                       <div className="space-y-4">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <Target size={14} className="text-indigo-500" />
                            Strategy Name
                          </label>
                          <input 
                            type="text" 
                            value={newStrategy.name}
                            onChange={(e) => setNewStrategy({...newStrategy, name: e.target.value})}
                            className="w-full bg-black border border-white/10 rounded-2xl p-5 text-lg font-bold italic text-white outline-none focus:border-indigo-500 transition-colors"
                          />
                       </div>
                       <div className="space-y-4">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <Zap size={14} className="text-amber-500" />
                            Execution Type
                          </label>
                          <select 
                            value={newStrategy.type}
                            onChange={(e) => setNewStrategy({...newStrategy, type: e.target.value as any})}
                            className="w-full bg-black border border-white/10 rounded-2xl p-5 text-sm font-bold text-white outline-none focus:border-indigo-500 transition-colors appearance-none"
                          >
                             <option value="momentum">Momentum_Pursuit</option>
                             <option value="arbitrage">LST_Arbitrage</option>
                             <option value="mean-reversion">Mean_Reversion</option>
                             <option value="neural">Neural_Inference</option>
                          </select>
                       </div>
                    </div>

                    <div className="space-y-4">
                       <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                         <ShieldAlert size={14} className="text-rose-500" />
                         Risk Tolerance Level
                       </label>
                       <div className="grid grid-cols-3 gap-4">
                          {(['low', 'med', 'high'] as const).map(risk => (
                            <button 
                              key={risk}
                              onClick={() => setNewStrategy({...newStrategy, riskLevel: risk})}
                              className={`py-4 rounded-2xl border text-[10px] font-black uppercase tracking-widest transition-all ${newStrategy.riskLevel === risk ? 'bg-indigo-600 border-indigo-400 text-white' : 'bg-white/5 border-white/10 text-slate-500 hover:border-white/20'}`}
                            >
                               {risk}
                            </button>
                          ))}
                       </div>
                    </div>

                    <div className="space-y-4">
                       <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                         <Layers size={14} className="text-indigo-500" />
                         Strategy Description
                       </label>
                       <textarea 
                         value={newStrategy.description}
                         onChange={(e) => setNewStrategy({...newStrategy, description: e.target.value})}
                         placeholder="Describe the computational logic..."
                         rows={3}
                         className="w-full bg-black border border-white/10 rounded-3xl p-6 text-sm italic text-slate-400 outline-none focus:border-indigo-500 transition-colors resize-none"
                       />
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                       <div className="space-y-4">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <TrendingUp size={14} className="text-emerald-500" />
                            Entry Threshold
                          </label>
                          <div className="relative">
                            <input 
                              type="number" 
                              step="0.01"
                              value={newStrategy.entryThreshold}
                              onChange={(e) => setNewStrategy({...newStrategy, entryThreshold: Number(e.target.value)})}
                              className="w-full bg-black border border-white/10 rounded-2xl p-5 text-white font-mono font-bold outline-none focus:border-indigo-500 transition-colors"
                            />
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[9px] font-black text-slate-700">SIG_CONF</span>
                          </div>
                       </div>
                       <div className="space-y-4">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <ArrowRight size={14} className="text-rose-500" />
                            Exit Threshold
                          </label>
                          <div className="relative">
                            <input 
                              type="number" 
                              step="0.01"
                              value={newStrategy.exitThreshold}
                              onChange={(e) => setNewStrategy({...newStrategy, exitThreshold: Number(e.target.value)})}
                              className="w-full bg-black border border-white/10 rounded-2xl p-5 text-white font-mono font-bold outline-none focus:border-indigo-500 transition-colors"
                            />
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[9px] font-black text-slate-700">SIG_BREAK</span>
                          </div>
                       </div>
                       <div className="space-y-4">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <Activity size={14} className="text-indigo-500" />
                            Max Trades / Day
                          </label>
                          <div className="relative">
                            <input 
                              type="number" 
                              value={newStrategy.maxTradesPerDay}
                              onChange={(e) => setNewStrategy({...newStrategy, maxTradesPerDay: Number(e.target.value)})}
                              className="w-full bg-black border border-white/10 rounded-2xl p-5 text-white font-mono font-bold outline-none focus:border-indigo-500 transition-colors"
                            />
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[9px] font-black text-slate-700">CAP_EX</span>
                          </div>
                       </div>
                    </div>

                    <div className="pt-4">
                       <button 
                         onClick={handleCreateStrategy}
                         className="w-full py-6 bg-white text-black rounded-3xl text-xs font-black uppercase tracking-widest flex items-center justify-center gap-3 hover:bg-slate-200 transition-all"
                       >
                         Save_Heuristic_Profile
                         <ChevronRight size={18} />
                       </button>
                    </div>
                 </div>
              </div>
            </motion.div>
          </div>
        )}

        {isCreating && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-12">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsCreating(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-xl"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-2xl bg-[#0d0d0d] border border-white/10 rounded-[2.5rem] shadow-2xl relative z-10 overflow-hidden"
            >
              <div className="p-8 md:p-12">
                 <div className="flex justify-between items-start mb-10">
                    <div>
                      <h3 className="text-4xl font-black italic tracking-tighter uppercase text-white mb-2">Forge_New_Bot</h3>
                      <p className="text-slate-500 text-sm font-mono tracking-widest">SEEDING REINFORCEMENT LEARNING AGENT</p>
                    </div>
                    <button 
                      onClick={() => setIsCreating(false)}
                      className="p-3 bg-white/5 border border-white/10 rounded-full text-slate-400 hover:text-white transition-colors"
                    >
                      <X size={20} />
                    </button>
                 </div>

                  <div className="space-y-10">
                    <div className="space-y-4">
                       <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                         <Target size={14} className="text-indigo-500" />
                         Agent Identifier
                       </label>
                       <input 
                         type="text" 
                         value={newBot.name}
                         onChange={(e) => setNewBot({...newBot, name: e.target.value})}
                         placeholder="e.g. ALPHA_TERMINAL_V1"
                         className="w-full bg-black border border-white/10 rounded-2xl py-6 px-8 text-2xl font-black italic tracking-tighter text-white outline-none focus:border-indigo-500 transition-all placeholder:text-slate-800"
                       />
                    </div>

                    <div className="space-y-4">
                       <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                         <Brain size={14} className="text-indigo-500" />
                         Heuristic Engine Selection
                       </label>
                       <div className="grid md:grid-cols-3 gap-4">
                          {strategies.map(s => (
                            <button 
                              key={s.id}
                              onClick={() => setNewBot({...newBot, strategyId: s.id})}
                              className={`p-6 rounded-[2rem] border text-left transition-all relative overflow-hidden group ${newBot.strategyId === s.id ? 'bg-indigo-600 border-indigo-400 shadow-2xl shadow-indigo-600/40' : 'bg-white/5 border-white/10 hover:border-white/20'}`}
                            >
                               <div className={`absolute -right-2 -top-2 opacity-10 ${newBot.strategyId === s.id ? 'text-white' : 'text-slate-500'}`}>
                                 <Cpu size={48} />
                               </div>
                               <p className={`text-[10px] font-black uppercase mb-3 tracking-widest ${newBot.strategyId === s.id ? 'text-white' : 'text-slate-400'}`}>{s.name}</p>
                               <p className={`text-[10px] leading-relaxed italic line-clamp-2 ${newBot.strategyId === s.id ? 'text-indigo-100' : 'text-slate-500'}`}>{s.description}</p>
                            </button>
                          ))}
                       </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                       <div className="space-y-3">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <Layers size={14} className="text-indigo-500" />
                            Allocation
                          </label>
                          <div className="relative group mb-2">
                             <input 
                               type="number" 
                               value={newBot.allocation}
                               onChange={(e) => setNewBot({...newBot, allocation: Number(e.target.value)})}
                               className="w-full bg-black border border-white/10 rounded-2xl p-5 text-white font-mono font-bold outline-none focus:border-indigo-500 transition-colors pr-12"
                             />
                             <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-slate-600 uppercase">USDT</span>
                          </div>
                          <div className="flex gap-2">
                             {[500, 1000, 5000].map(val => (
                               <button 
                                 key={val}
                                 onClick={() => setNewBot({...newBot, allocation: val})}
                                 className="flex-1 py-2 bg-white/5 border border-white/10 rounded-lg text-[9px] font-bold text-slate-500 hover:text-white hover:border-white/20 transition-all font-mono"
                               >
                                 ${val}
                               </button>
                             ))}
                          </div>
                       </div>
                       <div className="space-y-3">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                             <Trash2 size={14} className="text-rose-500" />
                             Stop Loss
                          </label>
                          <div className="relative group mb-2">
                            <input 
                              type="number" 
                              step="0.1"
                              value={newBot.stopLoss}
                              onChange={(e) => setNewBot({...newBot, stopLoss: Number(e.target.value)})}
                              className="w-full bg-black border border-white/10 rounded-2xl p-5 text-rose-400 font-mono font-bold outline-none focus:border-rose-500/50 transition-colors pr-10"
                            />
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-slate-600 uppercase">%</span>
                          </div>
                          <div className="flex gap-2">
                             {[1, 2, 5].map(val => (
                               <button 
                                 key={val}
                                 onClick={() => setNewBot({...newBot, stopLoss: val})}
                                 className="flex-1 py-2 bg-rose-500/5 border border-rose-500/10 rounded-lg text-[9px] font-bold text-rose-500/50 hover:text-rose-400 hover:border-rose-500/20 transition-all font-mono"
                               >
                                 {val}%
                               </button>
                             ))}
                          </div>
                       </div>
                       <div className="space-y-3">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                             <TrendingUp size={14} className="text-emerald-500" />
                             Take Profit
                          </label>
                          <div className="relative group mb-2">
                            <input 
                              type="number" 
                              step="0.1"
                              value={newBot.takeProfit}
                              onChange={(e) => setNewBot({...newBot, takeProfit: Number(e.target.value)})}
                              className="w-full bg-black border border-white/10 rounded-2xl p-5 text-emerald-400 font-mono font-bold outline-none focus:border-emerald-500/50 transition-colors pr-10"
                            />
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-slate-600 uppercase">%</span>
                          </div>
                          <div className="flex gap-2">
                             {[2, 5, 10].map(val => (
                               <button 
                                 key={val}
                                 onClick={() => setNewBot({...newBot, takeProfit: val})}
                                 className="flex-1 py-2 bg-emerald-500/5 border border-emerald-500/10 rounded-lg text-[9px] font-bold text-emerald-500/50 hover:text-emerald-400 hover:border-emerald-500/20 transition-all font-mono"
                               >
                                 {val}%
                               </button>
                             ))}
                          </div>
                       </div>
                    </div>

                    <div className="pt-6">
                       <button 
                         onClick={handleCreateBot}
                         className="w-full py-6 bg-white text-black rounded-3xl text-xs font-black uppercase tracking-widest flex items-center justify-center gap-3 hover:bg-slate-200 transition-all active:scale-[0.98]"
                       >
                         Compile_Neural_Network
                         <ChevronRight size={18} />
                       </button>
                    </div>
                 </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <div className="bg-zinc-900 border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden shadow-2xl">
         <div className="flex flex-col md:flex-row gap-12 items-center">
            <div className="flex-1">
               <div className="flex items-center gap-2 mb-4">
                 <Database size={16} className="text-indigo-400" />
                 <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Global Compute Cluster</span>
               </div>
               <h3 className="text-4xl font-black italic tracking-tighter mb-4 uppercase text-white">Strategy Training</h3>
               <p className="text-slate-400 text-sm leading-relaxed mb-8 max-w-lg">
                 Our agents are trained in a distributed GPU mesh across 12 global regions, utilizing real-time order-book telemetry to optimize hyper-parameters in sub-second intervals.
               </p>
               <div className="flex gap-4">
                 <button className="bg-indigo-600 text-white px-8 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-colors">
                   Provision_Extra_Nodes
                 </button>
                 <button className="bg-white/5 border border-white/10 text-white px-8 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-colors">
                   Network_Latency_Map
                 </button>
               </div>
            </div>
            <div className="w-full md:w-1/2">
               <div className="grid grid-cols-5 gap-3">
                 {new Array(25).fill(0).map((_, i) => (
                   <motion.div 
                     key={i}
                     animate={{ 
                       opacity: [0.1, 0.4, 0.1],
                       scale: [1, 1.05, 1],
                       backgroundColor: i % 7 === 0 ? ["rgba(244,63,94,0.1)", "rgba(244,63,94,0.3)", "rgba(244,63,94,0.1)"] : ["rgba(99,102,241,0.1)", "rgba(99,102,241,0.3)", "rgba(99,102,241,0.1)"]
                     }}
                     transition={{ duration: 2 + Math.random() * 3, repeat: Infinity, delay: Math.random() * 2 }}
                     className="aspect-square bg-indigo-500/10 rounded-xl border border-white/5 flex items-center justify-center"
                   >
                     <Layers size={12} className="text-white/10" />
                   </motion.div>
                 ))}
               </div>
            </div>
         </div>
      </div>
    </div>
  );
}
