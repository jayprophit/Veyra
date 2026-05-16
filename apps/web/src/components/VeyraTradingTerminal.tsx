import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ComposedChart, Line, BarChart, Bar
} from 'recharts';
import { 
  TrendingUp, 
  ArrowUpRight, 
  Zap, 
  Target,
  ArrowRight,
  Activity,
  Layers,
  Search,
  Settings2,
  Maximize2,
  RefreshCcw,
  ShieldCheck,
  ChevronRight,
  Info
} from "lucide-react";
import { useCurrency } from "../context/CurrencyContext";

const chartData = [
  { time: '09:00', price: 4050, volume: 2400 },
  { time: '10:00', price: 4120, volume: 3200 },
  { time: '11:00', price: 4080, volume: 1800 },
  { time: '12:00', price: 4110, volume: 4500 },
  { time: '13:00', price: 4190, volume: 2900 },
  { time: '14:00', price: 4160, volume: 2100 },
  { time: '15:00', price: 4250, volume: 5600 },
  { time: '16:00', price: 4230, volume: 3100 },
];

const listedAssets = [
  { symbol: "VRA/USDT", price: "4,250.10", delta: "+5.8%", up: true },
  { symbol: "BTC/VRA", price: "12.44", delta: "+1.2%", up: true },
  { symbol: "AAPL Mirror", price: "182.10", delta: "-0.4%", up: false },
  { symbol: "TSLA Mirror", price: "172.44", delta: "+4.1%", up: true },
  { symbol: "ETH/VRA", price: "0.88", delta: "-2.1%", up: false },
];

export function VeyraTradingTerminal() {
  const { formatValue } = useCurrency();
  const [activeAsset, setActiveAsset] = useState(listedAssets[0]);
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [isConfirming, setIsConfirming] = useState(false);
  const [amount, setAmount] = useState('1400.00');

  return (
    <div className="space-y-6 text-white min-h-screen">
      {/* Dynamic Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "INDEX_STABILITY", val: "99.98%", sub: "ORACLE_ACTIVE" },
          { label: "LIQUIDITY_DEPTH", val: formatValue(14800000).replace(/\.00$/, ''), sub: "VRA_POOL_B" },
          { label: "EXECUTION_LANC", val: "2.4ms", sub: "NODE_ALPHA" },
          { label: "VOL_INTENSITY", val: "CRITICAL", sub: "HIGH_CONF" },
        ].map((s, i) => (
          <div key={i} className="bg-white/5 border border-white/10 p-5 rounded-3xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
              <Activity size={20} />
            </div>
            <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-1">{s.label}</p>
            <h4 className="text-xl font-black italic tracking-tighter text-white">{s.val}</h4>
            <p className="text-[8px] text-indigo-400 font-black mt-1 uppercase tracking-widest">{s.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Sidebar: Market Feed */}
        <div className="lg:col-span-3 space-y-4">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-3xl overflow-hidden">
              <div className="p-5 border-b border-white/5 flex items-center justify-between">
                 <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Market_Feed</h5>
                 <Search size={14} className="text-slate-700" />
              </div>
              <div className="p-2 space-y-1">
                 {listedAssets.map((asset, i) => (
                   <button 
                     key={i} 
                     onClick={() => setActiveAsset(asset)}
                     className={`w-full p-4 rounded-2xl flex items-center justify-between transition-all group ${activeAsset.symbol === asset.symbol ? 'bg-indigo-600/20 border border-indigo-500/30' : 'hover:bg-white/5 border border-transparent'}`}
                   >
                     <div className="text-left">
                        <p className="text-xs font-black italic tracking-tight">{asset.symbol}</p>
                        <p className={`text-[10px] font-bold ${asset.up ? 'text-emerald-400' : 'text-rose-400'}`}>{asset.delta}</p>
                     </div>
                     <div className="text-right">
                        <p className="text-xs font-mono font-bold">{formatValue(parseFloat(asset.price.replace(',', '')))}</p>
                        <ChevronRight size={14} className={`ml-auto transition-transform ${activeAsset.symbol === asset.symbol ? 'translate-x-0' : '-translate-x-2 opacity-0 group-hover:opacity-100 group-hover:translate-x-0'}`} />
                     </div>
                   </button>
                 ))}
              </div>
           </div>

           <div className="p-8 bg-gradient-to-br from-indigo-950/20 to-transparent border border-indigo-500/20 rounded-[2.5rem]">
              <Target size={32} className="text-indigo-400 mb-6" />
              <h5 className="text-xl font-black italic tracking-tighter uppercase mb-2">Alpha Signal</h5>
              <p className="text-[10px] text-slate-500 font-mono leading-relaxed uppercase mb-4">
                 Divergence detected on VRA/USDT relative to mirror assets. Optimal entry established.
              </p>
              <div className="flex items-center gap-2">
                 <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 w-[88%]" />
                 </div>
                 <span className="text-[9px] font-black text-indigo-400 tracking-widest">88% CONF</span>
              </div>
           </div>
        </div>

        {/* Center: Charting Engine */}
        <div className="lg:col-span-6 space-y-6">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-8 relative">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
                 <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-white text-black rounded-2xl flex items-center justify-center font-black italic text-xl shadow-2xl">
                       {activeAsset.symbol[0]}
                    </div>
                    <div>
                       <h3 className="text-2xl font-black italic tracking-tighter uppercase">{activeAsset.symbol}</h3>
                       <div className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                          <span className="text-[10px] font-mono text-slate-500 tracking-wider">REALTIME_LIQUIDITY_FEED</span>
                       </div>
                    </div>
                 </div>
                 <div className="flex items-center bg-white/5 p-1.5 rounded-2xl border border-white/5">
                    {['1H', '4H', '1D', '1W'].map(t => (
                      <button key={t} className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${t === '1D' ? 'bg-white text-black' : 'text-slate-500 hover:text-white'}`}>
                        {t}
                      </button>
                    ))}
                 </div>
              </div>

              <div className="h-[400px] w-full">
                 <ResponsiveContainer width="100%" height="100%">
                   <ComposedChart data={chartData}>
                     <defs>
                       <linearGradient id="tradingGradient" x1="0" y1="0" x2="0" y2="1">
                         <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2}/>
                         <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                       </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                     <XAxis dataKey="time" hide />
                     <YAxis hide domain={['dataMin - 100', 'dataMax + 100']} />
                     <Tooltip 
                       contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '1.5rem', padding: '1rem' }}
                       cursor={{ stroke: '#6366f1', strokeWidth: 1 }}
                     />
                     <Area type="monotone" dataKey="price" stroke="none" fill="url(#tradingGradient)" />
                     <Line 
                       type="monotone" 
                       dataKey="price" 
                       stroke="#6366f1" 
                       strokeWidth={4} 
                       dot={false} 
                       animationDuration={2000}
                     />
                   </ComposedChart>
                 </ResponsiveContainer>
              </div>

              <div className="mt-8 flex items-center justify-between pt-8 border-t border-white/5">
                 <div className="flex gap-8">
                    <div>
                       <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-1">Spread</p>
                       <p className="text-xs font-black text-slate-400">0.02%</p>
                    </div>
                    <div>
                       <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-1">Index Price</p>
                       <p className="text-xs font-black text-slate-400">{formatValue(4249.95)}</p>
                    </div>
                 </div>
                 <div className="flex gap-4">
                    <button className="p-3 bg-white/5 border border-white/10 rounded-2xl text-slate-500 hover:text-white transition-colors">
                       <Maximize2 size={18} />
                    </button>
                    <button className="p-3 bg-white/5 border border-white/10 rounded-2xl text-slate-500 hover:text-white transition-colors">
                       <Settings2 size={18} />
                    </button>
                 </div>
              </div>
           </div>

           <div className="bg-[#0a0a0a] border border-white/10 rounded-[2.5rem] p-6">
              <div className="flex items-center gap-3 mb-6">
                 <Layers size={18} className="text-slate-500" />
                 <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Position_Overview</h5>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                 <div>
                    <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-2">Net Value</p>
                    <p className="text-sm font-black italic">{formatValue(42204.12)}</p>
                 </div>
                 <div>
                    <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-2">Unrealized PNL</p>
                    <p className="text-sm font-black italic text-emerald-400">+{formatValue(2112.00)}</p>
                 </div>
                 <div>
                    <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-2">Margin Use</p>
                    <p className="text-sm font-black italic text-indigo-400">12.4%</p>
                 </div>
                 <div>
                    <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest mb-2">Leverage</p>
                    <p className="text-sm font-black italic">5X CRIT</p>
                 </div>
              </div>
           </div>
        </div>

        {/* Right: Order Configuration */}
        <div className="lg:col-span-3 space-y-6">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-8 space-y-8">
              <div className="flex p-1.5 bg-black border border-white/5 rounded-2xl">
                 <button 
                  onClick={() => setSide('buy')}
                  className={`flex-1 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${side === 'buy' ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20' : 'text-slate-600 hover:text-slate-400'}`}
                 >
                   Long
                 </button>
                 <button 
                  onClick={() => setSide('sell')}
                  className={`flex-1 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${side === 'sell' ? 'bg-rose-500 text-black shadow-lg shadow-rose-500/20' : 'text-slate-600 hover:text-slate-400'}`}
                 >
                   Short
                 </button>
              </div>

              <div className="space-y-6">
                 <div className="space-y-3">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-600 flex justify-between">
                       <span>Entrance Size</span>
                       <span className="text-slate-400">USDT</span>
                    </label>
                    <div className="bg-black border border-white/10 rounded-2xl p-5 focus-within:border-indigo-500 transition-colors">
                       <input 
                         type="text" 
                         value={amount} 
                         onChange={e => setAmount(e.target.value)}
                         className="bg-transparent w-full outline-none font-black italic text-2xl" 
                       />
                    </div>
                 </div>

                 <div className="space-y-3">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-600 flex justify-between">
                       <span>Target Asset</span>
                       <span className="text-slate-400">VRA</span>
                    </label>
                    <div className="bg-black/40 border border-white/5 rounded-2xl p-5">
                       <p className="text-2xl font-black italic text-slate-400 opacity-50">112,442.20</p>
                    </div>
                 </div>

                 <div className="pt-4 border-t border-white/5 flex flex-col gap-2">
                    <div className="flex justify-between text-[10px] font-mono">
                      <span className="text-slate-500">Max Slippage</span>
                      <span className="text-indigo-400">0.05%</span>
                    </div>
                    <div className="flex justify-between text-[10px] font-mono">
                      <span className="text-slate-500">Node Fee</span>
                      <span className="text-slate-300">Free_Tier</span>
                    </div>
                 </div>

                 <button 
                   onClick={() => setIsConfirming(true)}
                   className={`w-full py-6 rounded-3xl font-black uppercase tracking-widest text-sm transition-all shadow-2xl relative overflow-hidden group ${side === 'buy' ? 'bg-white text-black hover:bg-slate-200' : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'}`}
                 >
                   <div className="relative z-10 flex items-center justify-center gap-3">
                      {side === 'buy' ? 'Execute Long' : 'Execute Short'}
                      <Zap size={18} className={side === 'buy' ? 'text-indigo-600' : 'text-slate-400'} />
                   </div>
                 </button>
              </div>
           </div>

           <div className="bg-zinc-950 border border-white/10 rounded-[2.5rem] p-6 overflow-hidden relative group">
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:rotate-12 transition-transform">
                 <ShieldCheck size={48} />
              </div>
              <div className="flex items-center gap-3 mb-4">
                 <ShieldCheck size={18} className="text-emerald-400" />
                 <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Node Security</h5>
              </div>
              <p className="text-[10px] text-slate-500 font-mono italic leading-relaxed">
                 TRANSACTION PACKETS ARE ENCRYPTED VIA VEYRA_PROTOCOL_V12. ANTIFRONT-RUNNING PROTECTION ACTIVE.
              </p>
           </div>
        </div>
      </div>

      <AnimatePresence>
         {isConfirming && (
           <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsConfirming(false)}
                className="absolute inset-0 bg-black/90 backdrop-blur-md"
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.9, y: 40 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 40 }}
                className="w-full max-w-lg bg-[#080808] border border-white/10 rounded-[3rem] shadow-[0_50px_100px_rgba(0,0,0,1)] relative z-10 overflow-hidden"
              >
                 <div className="p-12">
                    <div className="flex items-center gap-6 mb-12">
                       <div className={`w-16 h-16 rounded-[2rem] flex items-center justify-center shadow-2xl ${side === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                          <RefreshCcw size={32} className="animate-spin-slow" />
                       </div>
                       <div>
                          <h3 className="text-3xl font-black italic tracking-tighter uppercase">Confirm_Node_Write</h3>
                          <p className="text-[10px] font-mono text-slate-500 tracking-[0.3em] uppercase">Protocol Verification Required</p>
                       </div>
                    </div>

                    <div className="space-y-6 mb-12">
                       <div className="flex justify-between items-center py-4 border-b border-white/5">
                          <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Asset_Pair</span>
                          <span className="text-lg font-black italic">{activeAsset.symbol}</span>
                       </div>
                       <div className="flex justify-between items-center py-4 border-b border-white/5">
                          <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Operation</span>
                          <span className={`text-lg font-black italic uppercase ${side === 'buy' ? 'text-emerald-400' : 'text-rose-400'}`}>{side === 'buy' ? 'LONG_EXEC' : 'SHORT_EXEC'}</span>
                       </div>
                       <div className="flex justify-between items-center py-4 border-b border-white/5">
                          <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Order_Size</span>
                          <span className="text-lg font-black italic">{amount} USDT</span>
                       </div>
                       <div className="flex justify-between items-center py-4">
                          <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Expected_Return</span>
                          <span className="text-lg font-black italic text-indigo-400">112,442.20 VRA</span>
                       </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                       <button 
                         onClick={() => setIsConfirming(false)}
                         className="py-6 bg-white/5 border border-white/10 rounded-3xl text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-white transition-all"
                       >
                         Abort_Cycle
                       </button>
                       <button 
                         onClick={() => setIsConfirming(false)}
                         className={`py-6 rounded-3xl text-[10px] font-black uppercase tracking-widest text-black transition-all shadow-xl active:scale-95 ${side === 'buy' ? 'bg-emerald-500 hover:bg-emerald-400' : 'bg-rose-500 hover:bg-rose-400'}`}
                       >
                         Sync_Confirm
                       </button>
                    </div>
                 </div>
              </motion.div>
           </div>
         )}
      </AnimatePresence>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }
      `}} />
    </div>
  );
}
