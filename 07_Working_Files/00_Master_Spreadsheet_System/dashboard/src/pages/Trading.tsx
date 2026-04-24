import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Activity, 
  Clock, 
  Zap,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Loader2,
  ShieldCheck,
  History,
  Search,
  Filter,
  Cpu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Trading sessions
const sessions = [
  { id: 'london', name: 'London', startAt: '08:00', endAt: '16:00', active: true },
  { id: 'ny', name: 'New York', startAt: '13:00', endAt: '21:00', active: true },
  { id: 'tokyo', name: 'Tokyo', startAt: '00:00', endAt: '09:00', active: false },
  { id: 'sydney', name: 'Sydney', startAt: '22:00', endAt: '07:00', active: false },
];

// Mock AI recommendation
const mockAiInsight = {
  side: 'BUY',
  asset: 'BTC',
  quantity: 0.002,
  justification: 'Bitcoin showing support at £52k with institutional inflows increasing. Risk-reward favorable for micro-position.',
  confidence: 98
};

// Mock trade history
const mockTrades = [
  { id: 1, asset: 'BTC/GBP', side: 'BUY', amount: 52431, timestamp: new Date(Date.now() - 3600000) },
  { id: 2, asset: 'ETH/GBP', side: 'SELL', amount: 2847, timestamp: new Date(Date.now() - 7200000) },
  { id: 3, asset: 'VWRP', side: 'BUY', amount: 1250, timestamp: new Date(Date.now() - 86400000) },
  { id: 4, asset: 'BTC/GBP', side: 'BUY', amount: 52100, timestamp: new Date(Date.now() - 172800000) },
];

interface Trade {
  id: number;
  asset: string;
  side: string;
  amount: number;
  timestamp: Date;
}

const Trading: React.FC = () => {
  const [isRunning, setIsRunning] = useState(true);
  const [trades, setTrades] = useState<Trade[]>(mockTrades);
  const [aiInsight, setAiInsight] = useState(mockAiInsight);
  const [isGenerating, setIsGenerating] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("ALL");
  const [currency, setCurrency] = useState('GBP');

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: currency
    }).format(val);
  };

  const getGeminiRecommendation = async () => {
    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setAiInsight({
        ...mockAiInsight,
        asset: ['BTC', 'ETH', 'VWRP'][Math.floor(Math.random() * 3)],
        side: Math.random() > 0.5 ? 'BUY' : 'SELL'
      });
      setIsGenerating(false);
    }, 1500);
  };

  const simulateTrade = () => {
    const newTrade: Trade = {
      id: trades.length + 1,
      asset: "BTC/GBP",
      side: "BUY",
      amount: 52431,
      timestamp: new Date()
    };
    setTrades([newTrade, ...trades]);
  };

  const filteredTrades = trades.filter(trade => {
    const matchesSearch = trade.asset.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "ALL" || trade.side === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-8 pb-32">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">AI Trading Engine</h1>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
              <Activity className="w-3 h-3" />
              Live Execution
            </div>
            <div className="text-gray-500 text-sm font-mono tracking-tighter">
              v2.4.0-autonomous
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsRunning(!isRunning)}
            className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
              isRunning 
                ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20 hover:bg-rose-500/20' 
                : 'bg-emerald-500 text-black hover:bg-emerald-400'
            }`}
          >
            {isRunning ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current" />}
            {isRunning ? 'Pause Engine' : 'Resume Engine'}
          </button>
          <button 
            onClick={simulateTrade}
            className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-2xl font-bold hover:bg-white/10 active:scale-95 transition-all text-sm text-white"
          >
            Manual Exec
          </button>
        </div>
      </div>

      {/* AI Insight Box */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-r from-blue-600/20 to-emerald-600/20 border border-white/10 rounded-3xl p-6 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 p-8 opacity-10">
           <Cpu className="w-32 h-32 text-white" />
        </div>
        <div className="flex items-start gap-4 relative z-10">
          <div className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center shrink-0">
             <Zap className="w-6 h-6 text-emerald-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
               <div>
                  <h4 className="font-bold text-lg text-white">Engine Reasoning (Gemini v3 Flash)</h4>
                  <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Autonomous Strategy Synthesis</p>
               </div>
               <button 
                  onClick={getGeminiRecommendation}
                  disabled={isGenerating}
                  className="px-4 py-2 bg-white/10 border border-white/10 rounded-xl text-xs font-bold hover:bg-white/20 transition-all flex items-center gap-2 text-white"
               >
                  {isGenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                  Resync Intelligence
               </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               <div className="md:col-span-2 space-y-3">
                  <p className="text-emerald-400 font-medium leading-relaxed italic text-sm">
                     "{aiInsight.justification}"
                  </p>
                  <div className="flex items-center gap-4 text-[10px] text-gray-500 font-bold uppercase">
                     <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3 text-blue-400" /> Risk: Verified</span>
                     <span className="flex items-center gap-1"><Activity className="w-3 h-3 text-emerald-400" /> Confidence: {aiInsight.confidence}%</span>
                  </div>
               </div>
               <div className="bg-black/20 rounded-2xl p-4 border border-white/5 flex flex-col justify-center">
                  <div className="flex items-center justify-between mb-2">
                     <span className="text-[10px] text-gray-500 font-bold uppercase">Recommendation</span>
                     <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${
                       aiInsight.side === 'BUY' ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                     }`}>
                        {aiInsight.side}
                     </span>
                  </div>
                  <div className="flex items-baseline gap-2">
                     <span className="text-xl font-mono font-bold text-white">{aiInsight.asset}</span>
                     <span className="text-[10px] text-gray-600 font-mono">@{aiInsight.quantity}</span>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trading Sessions */}
        <div className="grid grid-cols-2 gap-4">
          {sessions.map((sess) => (
            <div 
              key={sess.id}
              className={`p-6 rounded-2xl border transition-all duration-300 ${
                sess.active 
                  ? 'bg-emerald-500/5 border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                  : 'bg-[#0d0d0d] border-white/5 grayscale'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className="font-semibold text-white">{sess.name}</span>
                <Clock className="w-4 h-4 text-gray-500" />
              </div>
              <div className="space-y-1">
                <div className="text-xl font-mono text-white">{sess.startAt} - {sess.endAt}</div>
                <div className={`text-[10px] font-bold uppercase tracking-widest ${
                  sess.active ? 'text-emerald-400' : 'text-gray-600'
                }`}>
                  {sess.active ? 'Operational' : 'Paused'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trade History */}
        <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-6 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg text-white flex items-center gap-2">
              <History className="w-5 h-5 text-emerald-500" />
              Sovereign Ledger
            </h3>
            <div className="flex items-center gap-2">
               <div className="relative">
                 <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                 <input 
                   type="text" 
                   placeholder="Search..."
                   value={searchTerm}
                   onChange={(e) => setSearchTerm(e.target.value)}
                   className="bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-xs outline-none focus:border-emerald-500/50 transition-colors w-32 text-white placeholder:text-gray-500"
                 />
               </div>
               <select 
                 value={filterType}
                 onChange={(e) => setFilterType(e.target.value)}
                 className="bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-[10px] font-bold uppercase tracking-wider outline-none cursor-pointer text-white"
               >
                 <option value="ALL">All</option>
                 <option value="BUY">Buy</option>
                 <option value="SELL">Sell</option>
               </select>
            </div>
          </div>
          <div className="space-y-4 flex-1 overflow-y-auto">
            <AnimatePresence initial={false}>
              {filteredTrades.map((trade) => (
                <motion.div 
                  key={trade.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 group hover:border-white/20 transition-all shadow-sm"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs ${
                      trade.side === 'BUY' ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                    }`}>
                      {trade.side}
                    </div>
                    <div>
                      <div className="font-semibold text-sm text-white">{trade.asset}</div>
                      <div className="text-[10px] text-gray-500 uppercase font-bold tracking-tighter">Chain Confirmed</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-semibold text-sm text-white">
                      {formatCurrency(trade.amount)}
                    </div>
                    <div className="text-[9px] text-gray-600 font-bold uppercase">{trade.timestamp.toLocaleTimeString()}</div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Zero-Waste Sweep */}
      <div className="bg-gradient-to-br from-indigo-600/10 to-purple-600/10 border border-indigo-500/20 rounded-3xl p-8">
         <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
            <div>
               <h2 className="text-2xl font-bold tracking-tight text-white mb-1">Zero-Waste Sweep</h2>
               <p className="text-gray-500 text-sm font-medium">Consolidate micro-balances (dust) across exchanges and protocols.</p>
            </div>
            <button 
              className="px-6 py-3 bg-indigo-500 text-white font-bold rounded-2xl hover:bg-indigo-400 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(99,102,241,0.2)]"
            >
               <Zap className="w-4 h-4" />
               Audit & Sweep
            </button>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
               { asset: 'USDT', balance: 0.000042, value: 0.04, source: 'Binance', type: 'CEX Dust' },
               { asset: 'MATIC', balance: 0.12, value: 0.08, source: 'Polygon', type: 'Idle Gas' },
               { asset: 'LINK', balance: 0.002, value: 0.31, source: 'Kraken', type: 'Stale Bal' }
            ].map((dust, i) => (
               <div key={i} className="bg-black/20 border border-white/5 p-5 rounded-2xl flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-pointer">
                  <div>
                     <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-white">{dust.asset}</span>
                        <span className="text-[8px] bg-white/5 text-gray-500 px-1.5 py-0.5 rounded font-black uppercase tracking-tighter">{dust.source}</span>
                     </div>
                     <p className="text-[10px] text-gray-500 font-mono">{dust.balance} {dust.asset}</p>
                  </div>
                  <div className="text-right">
                     <div className="text-sm font-bold text-indigo-400">~{formatCurrency(dust.value)}</div>
                     <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">{dust.type}</p>
                  </div>
               </div>
            ))}
         </div>
      </div>
    </div>
  );
};

export default Trading;
