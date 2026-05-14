/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Zap, Target, Activity } from "lucide-react";
import { useCurrency } from "../context/CurrencyContext";

const data = [
  { time: '00:00', price: 4000, volume: 2400 },
  { time: '04:00', price: 3000, volume: 1398 },
  { time: '08:00', price: 2000, volume: 9800 },
  { time: '12:00', price: 2780, volume: 3908 },
  { time: '16:00', price: 1890, volume: 4800 },
  { time: '20:00', price: 2390, volume: 3800 },
  { time: '23:59', price: 3490, volume: 4300 },
];

import { VeyraInfoBox } from "./VeyraInfoBox";

export function VeyraTradingDashboard() {
  const { formatValue } = useCurrency();

  const getDetails = (label: string) => {
    switch(label) {
      case "VRA_SYSTEM_INDEX": return [
        { label: "Aggregate Price", value: "$42.4k" },
        { label: "Mirror Drift", value: "0.002%" },
        { label: "Node Count", value: "1,240" }
      ];
      case "AI_CONFIDENCE": return [
        { label: "Neural Load", value: "12%" },
        { label: "Signal Purity", value: "98.2%" },
        { label: "Latency", value: "24ms" }
      ];
      default: return [
        { label: "Refresh Rate", value: "0.5s" },
        { label: "Data Integrity", value: "High" }
      ];
    }
  };

  return (
    <div className="space-y-10 text-white font-sans">
      {/* 5-Star Bento Grid Dashboard */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: "VRA_SYSTEM_INDEX", val: formatValue(42442.20), delta: "+5.2%", up: true, desc: "Protocol Avg" },
          { label: "AI_CONFIDENCE", val: "94.8%", delta: "OPTIMAL", up: true, desc: "Neural Load" },
          { label: "24H_VOL_INTEGRATED", val: formatValue(1200000000).replace(/\.00$/, ''), delta: "-2.1%", up: false, desc: "Market Heat" },
          { label: "NETWORK_LATENCY", val: "0.002ms", delta: "ULTRA", up: true, desc: "Edge Nodes" },
        ].map((s, i) => (
          <VeyraInfoBox key={i} label={s.label} value={s.val} details={getDetails(s.label)}>
            <div className="bg-[#0a0a0a] border border-white/10 p-8 rounded-[2.5rem] h-full relative overflow-hidden group transition-all hover:bg-white/5 active:scale-95 cursor-help">
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                 <Activity size={48} />
              </div>
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{s.label}</p>
              <h4 className="text-3xl font-black italic tracking-tighter text-white mb-2">{s.val}</h4>
              <div className="flex items-center justify-between">
                 <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${s.up ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                   {s.delta}
                 </span>
                 <span className="text-[8px] font-mono text-slate-600 uppercase tracking-widest">{s.desc}</span>
              </div>
            </div>
          </VeyraInfoBox>
        ))}
      </div>

      <div className="grid lg:grid-cols-12 gap-8">
        {/* Main Performance Chart */}
        <div className="lg:col-span-8 bg-[#0a0a0a] border border-white/10 p-10 rounded-[3.5rem] relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
            <div>
              <h3 className="text-3xl font-black italic tracking-tighter uppercase mb-1">Global_Performance</h3>
              <div className="flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
                 <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Real-time Asset Synthesis Kernels Active</p>
              </div>
            </div>
            <div className="flex items-center gap-4 bg-white/5 p-2 rounded-2xl border border-white/5">
              {['1H', '4H', '1D', 'ALL'].map(t => (
                <button key={t} className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${t === '1D' ? 'bg-white text-black shadow-xl shadow-white/10' : 'text-slate-500 hover:text-white'}`}>
                  {t}
                </button>
              ))}
            </div>
          </div>
          
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="dashboardGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                <XAxis dataKey="time" hide />
                <YAxis hide domain={['dataMin - 100', 'dataMax + 100']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '1.5rem', padding: '1.5rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}
                  cursor={{ stroke: '#6366f1', strokeWidth: 1 }}
                />
                <Area type="monotone" dataKey="price" stroke="#6366f1" strokeWidth={5} fillOpacity={1} fill="url(#dashboardGradient)" animationDuration={3000} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Intelligence Side Block */}
        <div className="lg:col-span-4 space-y-8">
           <div className="bg-[#0a0a0a] border border-white/10 p-10 rounded-[3rem] relative overflow-hidden group h-full flex flex-col justify-between">
              <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:rotate-12 transition-transform duration-700">
                 <Target size={120} />
              </div>
              <div>
                 <div className="flex items-center gap-3 mb-8">
                    <div className="w-10 h-10 bg-indigo-500 text-white rounded-2xl flex items-center justify-center shadow-2xl">
                       <Zap size={20} />
                    </div>
                    <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Neural_Intelligence</h5>
                 </div>
                 <h4 className="text-4xl font-black italic tracking-tighter text-white mb-6 uppercase">Alpha_Signal Established</h4>
                 <p className="text-sm font-bold text-slate-500 leading-relaxed italic mb-8">
                    Divergence detected in VRA/BTC corridor. Mirror-equities showing 92% correlation with lead indicators. High-confidence execution window opening now.
                 </p>
              </div>
              
              <div className="space-y-4">
                 <div className="flex justify-between items-end">
                    <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Confidence_Score</span>
                    <span className="text-xl font-black italic text-indigo-400">92.4%</span>
                 </div>
                 <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: '92.4%' }}
                      className="h-full bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"
                    />
                 </div>
                 <button className="w-full py-5 bg-white text-black rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-slate-200 transition-all active:scale-95 shadow-2xl">
                    Deploy_Intelligence
                 </button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
