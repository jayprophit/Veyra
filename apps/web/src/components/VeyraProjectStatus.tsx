import { CheckCircle2, Circle, Clock, ArrowUpRight, Zap, Target, Shield, Info } from "lucide-react";
import { motion } from "motion/react";
import { VeyraInfoBox } from "./VeyraInfoBox";

interface TodoItem {
  id: string;
  category: "FOUNDATION" | "CORE" | "PRIVATE" | "RELEASE";
  task: string;
  status: "completed" | "in-progress" | "backlog";
  description: string;
}

export function VeyraProjectStatus() {
  const todos: TodoItem[] = [
    {
      id: "1",
      category: "FOUNDATION",
      task: "Runnable Local Core",
      status: "completed",
      description: "Web app, API gateway, market normalization, portfolio endpoints, and paper-trading endpoints are wired for local development."
    },
    {
      id: "2",
      category: "CORE",
      task: "Data, Auth, And Reliability",
      status: "in-progress",
      description: "Add durable models, migrations, auth hardening, replay tests, observability, and backup discipline."
    },
    {
      id: "3",
      category: "PRIVATE",
      task: "AI Broker And Agents",
      status: "backlog",
      description: "Build model routing, policy enforcement, memory, bounded agents, and human approval for sensitive actions."
    },
    {
      id: "4",
      category: "PRIVATE",
      task: "Broker Execution",
      status: "backlog",
      description: "Progress from paper ledger to sandbox adapters, then human-approved live execution with reconciliation."
    },
    {
      id: "5",
      category: "PRIVATE",
      task: "Mobile And Smart Devices",
      status: "backlog",
      description: "Ship stable mobile and companion-device clients after the API contract is reliable."
    },
    {
      id: "6",
      category: "PRIVATE",
      task: "Web3 And Quantum Tracks",
      status: "backlog",
      description: "Keep Web3 isolated and read-only first; keep quantum work benchmarked against classical baselines."
    },
    {
      id: "7",
      category: "RELEASE",
      task: "Public Release Gate",
      status: "backlog",
      description: "Require security review, recovery drills, load tests, support process, and honest public documentation."
    },
    {
      id: "8",
      category: "RELEASE",
      task: "Enterprise Deployment",
      status: "backlog",
      description: "Add tenant isolation, SSO, managed secrets, compliance evidence, and multi-environment operations last."
    }
  ];

  const completedCount = todos.filter(t => t.status === "completed").length;
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
      case "FOUNDATION": return "text-blue-400 bg-blue-400/10";
      case "CORE": return "text-emerald-400 bg-emerald-400/10";
      case "PRIVATE": return "text-indigo-400 bg-indigo-400/10";
      case "RELEASE": return "text-rose-400 bg-rose-400/10";
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between">
        <div>
           <h3 className="text-3xl font-black italic tracking-tighter uppercase text-white mb-2">Private_Roadmap</h3>
           <p className="text-slate-500 text-sm font-mono uppercase tracking-[0.2em]">Foundation To Public Release Sequence</p>
        </div>
        <div className="text-right">
           <div className="text-4xl font-black italic tracking-tighter text-white mb-1">{progressPercent}%</div>
           <div className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Tracked Completion</div>
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
            className={`group p-6 rounded-[2rem] border transition-all ${todo.status === "completed" ? "bg-white/5 border-white/5" : "bg-black border-white/10 hover:border-white/20"}`}
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
                  <h4 className={`text-sm font-bold uppercase tracking-tight ${todo.status === "completed" ? "text-slate-400 line-through" : "text-white"}`}>
                    {todo.task}
                  </h4>
                </div>
                  <VeyraInfoBox 
                    label="Task_Metadata" 
                    value={todo.task} 
                    details={[
                      { label: "Mode", value: todo.category === "FOUNDATION" ? "ACTIVE" : "PRIVATE" },
                      { label: "Status", value: todo.status.toUpperCase() },
                      { label: "Branch", value: "foundation" }
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
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Durable data, auth, replay tests, and observability starter.</p>
         </div>
         <div className="p-8 bg-zinc-950 border border-white/5 rounded-[2.5rem]">
            <Shield className="text-rose-500 mb-6" size={32} />
            <h5 className="text-xl font-black italic tracking-tighter uppercase text-white mb-2">Policy_Gate</h5>
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Agents and execution stay private until approval and audit controls exist.</p>
         </div>
         <div className="p-8 bg-zinc-950 border border-white/5 rounded-[2.5rem]">
            <Target className="text-indigo-500 mb-6" size={32} />
            <h5 className="text-xl font-black italic tracking-tighter uppercase text-white mb-2">Release_Order</h5>
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">Private capability first, public launch second, enterprise deployment last.</p>
         </div>
      </div>
    </div>
  );
}
