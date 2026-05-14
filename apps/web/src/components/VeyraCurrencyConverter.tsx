import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  RefreshCw, 
  ArrowRightLeft, 
  TrendingUp, 
  TrendingDown, 
  Globe, 
  Coins, 
  DollarSign, 
  Zap,
  Info,
  ChevronDown,
  Search,
  Activity
} from "lucide-react";

interface Currency {
  code: string;
  name: string;
  type: "fiat" | "crypto";
  symbol: string;
  baseRate: number; // Rate relative to USD
}

const currencies: Currency[] = [
  { code: "USD", name: "US Dollar", type: "fiat", symbol: "$", baseRate: 1 },
  { code: "EUR", name: "Euro", type: "fiat", symbol: "€", baseRate: 0.92 },
  { code: "GBP", name: "British Pound", type: "fiat", symbol: "£", baseRate: 0.79 },
  { code: "JPY", name: "Japanese Yen", type: "fiat", symbol: "¥", baseRate: 151.2 },
  { code: "BTC", name: "Bitcoin", type: "crypto", symbol: "₿", baseRate: 0.000015 },
  { code: "ETH", name: "Ethereum", type: "crypto", symbol: "Ξ", baseRate: 0.00028 },
  { code: "VRA", name: "Veyra Protocol", type: "crypto", symbol: "V", baseRate: 235.4 },
  { code: "SOL", name: "Solana", type: "crypto", symbol: "S", baseRate: 0.0068 },
  { code: "AUD", name: "Australian Dollar", type: "fiat", symbol: "A$", baseRate: 1.52 },
  { code: "CAD", name: "Canadian Dollar", type: "fiat", symbol: "C$", baseRate: 1.35 },
];

export function VeyraCurrencyConverter() {
  const [fromCurrency, setFromCurrency] = useState(currencies[0]);
  const [toCurrency, setToCurrency] = useState(currencies[6]);
  const [amount, setAmount] = useState<string>("1000");
  const [isFlipped, setIsFlipped] = useState(false);
  const [lastSync, setLastSync] = useState(new Date());
  const [isSyncing, setIsSyncing] = useState(false);
  const [showFromList, setShowFromList] = useState(false);
  const [showToList, setShowToList] = useState(false);

  // Simulate real-time rate fluctuations
  const [fluctuation, setFluctuation] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsSyncing(true);
      setTimeout(() => {
        setFluctuation(0.98 + Math.random() * 0.04); // +/- 2%
        setLastSync(new Date());
        setIsSyncing(false);
      }, 800);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const convert = (val: string) => {
    const num = parseFloat(val) || 0;
    const rate = (toCurrency.baseRate / fromCurrency.baseRate) * fluctuation;
    return (num * rate).toLocaleString(undefined, { 
      maximumFractionDigits: toCurrency.type === 'crypto' ? 6 : 2,
      minimumFractionDigits: 2
    });
  };

  const swapCurrencies = () => {
    setIsFlipped(!isFlipped);
    const temp = fromCurrency;
    setFromCurrency(toCurrency);
    setToCurrency(temp);
  };

  return (
    <div className="space-y-8">
      <div className="grid lg:grid-cols-12 gap-8">
        {/* Converter Core */}
        <div className="lg:col-span-8">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-10 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Globe size={120} className="animate-pulse" />
            </div>

            <div className="flex items-center justify-between mb-12">
               <div>
                  <h3 className="text-3xl font-black italic tracking-tighter uppercase text-white mb-1 whitespace-nowrap">Currency_Oracle</h3>
                  <div className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${isSyncing ? 'bg-amber-500 animate-ping' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'}`} />
                    <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest whitespace-nowrap">
                      {isSyncing ? "Syncing_Protocol..." : `Last Node Sync: ${lastSync.toLocaleTimeString()}`}
                    </span>
                  </div>
               </div>
               <button 
                onClick={() => {
                  setIsSyncing(true);
                  setTimeout(() => setIsSyncing(false), 1000);
                }}
                className="p-4 bg-white/5 border border-white/10 rounded-2xl text-slate-500 hover:text-white transition-all active:scale-95"
               >
                 <RefreshCw size={20} className={isSyncing ? "animate-spin" : ""} />
               </button>
            </div>

            <div className="relative flex flex-col gap-4">
              {/* From Section */}
              <div className="bg-black border border-white/5 rounded-3xl p-8 group focus-within:border-indigo-500/50 transition-all">
                <div className="flex justify-between items-center mb-6">
                  <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Input_Value</span>
                  <div className="relative">
                    <button 
                      onClick={() => setShowFromList(!showFromList)}
                      className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl border border-white/10 hover:border-white/30 transition-all"
                    >
                      <span className="text-xs font-black italic">{fromCurrency.code}</span>
                      <ChevronDown size={14} className={showFromList ? "rotate-180" : ""} />
                    </button>
                    <AnimatePresence>
                      {showFromList && (
                        <motion.div 
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 10 }}
                          className="absolute right-0 top-full mt-2 w-48 bg-[#0d0d0d] border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden"
                        >
                          <div className="max-h-64 overflow-y-auto">
                            {currencies.map(c => (
                              <button 
                                key={c.code}
                                onClick={() => { setFromCurrency(c); setShowFromList(false); }}
                                className="w-full px-5 py-4 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 flex items-center justify-between"
                              >
                                <div>
                                  <p className="text-xs font-black italic">{c.code}</p>
                                  <p className="text-[9px] text-slate-500 font-mono uppercase">{c.name}</p>
                                </div>
                                <span className="text-slate-700 text-[10px]">{c.symbol}</span>
                              </button>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
                <input 
                  type="text" 
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full bg-transparent text-5xl md:text-7xl font-black italic tracking-tighter text-white outline-none placeholder:text-slate-900"
                  placeholder="0.00"
                />
              </div>

              {/* Swap Button */}
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
                <button 
                  onClick={swapCurrencies}
                  className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-2xl shadow-indigo-600/40 border-4 border-[#0a0a0a] hover:scale-110 active:scale-95 transition-all group"
                >
                  <ArrowRightLeft size={24} className="group-hover:rotate-180 transition-transform duration-500" />
                </button>
              </div>

              {/* To Section */}
              <div className="bg-white/5 border border-white/5 rounded-3xl p-8 group transition-all">
                <div className="flex justify-between items-center mb-6">
                  <span className="text-[10px] font-black uppercase text-slate-600 tracking-widest">Calculated_Output</span>
                  <div className="relative">
                    <button 
                      onClick={() => setShowToList(!showToList)}
                      className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl border border-white/10 hover:border-white/30 transition-all"
                    >
                      <span className="text-xs font-black italic">{toCurrency.code}</span>
                      <ChevronDown size={14} className={showToList ? "rotate-180" : ""} />
                    </button>
                    <AnimatePresence>
                      {showToList && (
                        <motion.div 
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 10 }}
                          className="absolute right-0 top-full mt-2 w-48 bg-[#0d0d0d] border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden"
                        >
                          <div className="max-h-64 overflow-y-auto">
                            {currencies.map(c => (
                              <button 
                                key={c.code}
                                onClick={() => { setToCurrency(c); setShowToList(false); }}
                                className="w-full px-5 py-4 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 flex items-center justify-between"
                              >
                                <div>
                                  <p className="text-xs font-black italic">{c.code}</p>
                                  <p className="text-[9px] text-slate-500 font-mono uppercase">{c.name}</p>
                                </div>
                                <span className="text-slate-700 text-[10px]">{c.symbol}</span>
                              </button>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
                <div className="text-5xl md:text-7xl font-black italic tracking-tighter text-indigo-400 break-all">
                  {convert(amount)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Info Sidebar */}
        <div className="lg:col-span-4 space-y-6">
           <div className="bg-zinc-950 border border-white/10 rounded-[2.5rem] p-8 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:rotate-12 transition-transform">
                 <Zap size={48} className="text-amber-500" />
              </div>
              <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
                 <Activity size={14} className="text-indigo-500" /> 
                 Live_Rate_Dynamic
              </h5>
              <div className="space-y-6">
                 <div>
                    <h4 className="text-3xl font-black italic tracking-tighter text-white mb-2">
                       1 {fromCurrency.code} = { (toCurrency.baseRate / fromCurrency.baseRate * fluctuation).toFixed(4) } {toCurrency.code}
                    </h4>
                    <div className="flex items-center gap-2 text-emerald-400">
                       <TrendingUp size={16} />
                       <span className="text-xs font-bold font-mono">+0.24% in last 5m</span>
                    </div>
                 </div>
                 <p className="text-[10px] text-slate-500 font-mono leading-relaxed uppercase italic">
                    CONVERSION CALCULATED VIA VEYRA_ORACLE_V4 ON-CHAIN AGGREGATOR. HIGH-PRECISION FLOATING POINT ARITHMETIC ACTIVE.
                 </p>
              </div>
           </div>

           <div className="bg-[#0a0a0a] border border-white/10 rounded-[2.5rem] p-8">
              <h5 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-6">Popular_Pairs</h5>
              <div className="space-y-4">
                 {[
                   { pair: "BTC / USD", rate: "$64,242.00", up: true },
                   { pair: "EUR / USD", rate: "$1.08", up: false },
                   { pair: "VRA / ETH", rate: "124.5Ξ", up: true },
                   { pair: "SOL / USD", rate: "$174.12", up: true },
                 ].map((p, i) => (
                   <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 hover:border-white/10 transition-all">
                      <div>
                        <p className="text-[10px] font-black italic tracking-tight uppercase text-slate-300">{p.pair}</p>
                        <p className="text-xs font-mono font-bold text-white mt-1">{p.rate}</p>
                      </div>
                      {p.up ? <TrendingUp size={14} className="text-emerald-500" /> : <TrendingDown size={14} className="text-rose-500" />}
                   </div>
                 ))}
              </div>
           </div>

           <div className="p-8 bg-indigo-600 rounded-[2.5rem] text-white shadow-2xl shadow-indigo-600/20 group cursor-pointer relative overflow-hidden">
              <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform">
                 <Coins size={96} />
              </div>
              <div className="relative z-10">
                 <h5 className="text-xl font-black italic tracking-tighter uppercase mb-2">Automated Payouts</h5>
                 <p className="text-[10px] font-bold text-indigo-100 uppercase leading-relaxed mb-6 opacity-80">
                    Connect your wallet to enable instant cross-currency node settlements.
                 </p>
                 <button className="w-full py-4 bg-white text-indigo-600 rounded-2xl font-black uppercase tracking-widest text-[10px] hover:bg-slate-100 transition-colors">
                    Sync_Wallet_Now
                 </button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
