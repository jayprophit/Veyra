import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, ComposedChart, Line
} from 'recharts';
import { 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight, 
  Zap, 
  Target,
  ArrowRight,
  Clock,
  History,
  Activity,
  ChevronDown,
  Info,
  Layers,
  Search,
  Settings2,
  Maximize2
} from "lucide-react";
import { useCurrency } from "../context/CurrencyContext";

// Mock Data
const priceData = [
  { time: '09:00', price: 4050, open: 4000, close: 4050, high: 4060, low: 3990, volume: 2400 },
  { time: '10:00', price: 4120, open: 4050, close: 4120, high: 4150, low: 4040, volume: 3200 },
  { time: '11:00', price: 4080, open: 4120, close: 4080, high: 4130, low: 4070, volume: 1800 },
  { time: '12:00', price: 4110, open: 4080, close: 4110, high: 4120, low: 4050, volume: 4500 },
  { time: '13:00', price: 4190, open: 4110, close: 4190, high: 4210, low: 4100, volume: 2900 },
  { time: '14:00', price: 4160, open: 4190, close: 4160, high: 4200, low: 4150, volume: 2100 },
  { time: '15:00', price: 4250, open: 4160, close: 4250, high: 4280, low: 4140, volume: 5600 },
  { time: '16:00', price: 4230, open: 4250, close: 4230, high: 4260, low: 4210, volume: 3100 },
];

const orderBook = {
  asks: [
    { price: 4252.50, size: 0.45, total: 0.45 },
    { price: 4251.20, size: 1.2, total: 1.65 },
    { price: 4250.75, size: 0.82, total: 2.47 },
    { price: 4250.40, size: 2.4, total: 4.87 },
    { price: 4250.10, size: 0.15, total: 5.02 },
  ],
  bids: [
    { price: 4249.80, size: 0.35, total: 0.35 },
    { price: 4249.50, size: 2.1, total: 2.45 },
    { price: 4249.10, size: 1.15, total: 3.60 },
    { price: 4248.60, size: 0.95, total: 4.55 },
    { price: 4248.20, size: 1.8, total: 6.35 },
  ]
};

const recentTrades = [
  { price: 4250.10, size: 0.15, time: '16:02:11', side: 'buy' },
  { price: 4249.80, size: 0.35, time: '16:02:08', side: 'sell' },
  { price: 4250.10, size: 0.05, time: '16:01:54', side: 'buy' },
  { price: 4250.05, size: 1.2, time: '16:01:42', side: 'buy' },
  { price: 4249.90, size: 0.8, time: '16:01:30', side: 'sell' },
  { price: 4249.80, size: 2.4, time: '16:01:12', side: 'sell' },
];

export function VeyraTradingView() {
  const { formatValue } = useCurrency();
  const [activeTab, setActiveTab] = useState<'limit' | 'market' | 'stop'>('limit');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [price, setPrice] = useState('4250.10');
  const [amount, setAmount] = useState('1.0');
  const [data, setData] = useState(priceData);
  const [isFetching, setIsFetching] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [pendingOrder, setPendingOrder] = useState<any>(null);
  const [priceError, setPriceError] = useState<string | null>(null);
  const [amountError, setAmountError] = useState<string | null>(null);

  const total = (parseFloat(price) || 0) * (parseFloat(amount) || 0);

  const validateInputs = () => {
    let isValid = true;
    const p = parseFloat(price);
    const a = parseFloat(amount);

    if (price === "" || isNaN(p) || p <= 0) {
      setPriceError("Amount required");
      isValid = false;
    } else {
      setPriceError(null);
    }

    if (amount === "" || isNaN(a) || a <= 0) {
      setAmountError("Size required");
      isValid = false;
    } else {
      setAmountError(null);
    }

    return isValid;
  };

  const handleOpenOrder = () => {
    if (!validateInputs()) return;
    
    setPendingOrder({
      asset: 'VRA/USDT',
      side: side === 'buy' ? 'LONG' : 'SHORT',
      type: activeTab.toUpperCase(),
      price: activeTab === 'market' ? 'MARKET' : price,
      amount: amount
    });
    setIsConfirming(true);
  };

  const handleConfirmOrder = () => {
    // Logic for submitting order would go here
    setIsConfirming(false);
    setPendingOrder(null);
  };

  const handleFetchLatest = () => {
    setIsFetching(true);
    setTimeout(() => {
      const lastPoint = data[data.length - 1];
      const newPrice = lastPoint.price + (Math.random() - 0.5) * 40;
      const newTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      setData([...data.slice(1), { 
        ...lastPoint, 
        time: newTime, 
        price: Math.floor(newPrice) 
      }]);
      setIsFetching(false);
    }, 1200);
  };

  const [activeSubTab, setActiveSubTab] = useState<'orders' | 'history' | 'positions'>('orders');

  const tradeHistoryData = [
    { time: '16:04:12', asset: 'VRA/USDT', price: 4252.10, size: 120.00, side: 'buy', status: 'filled' },
    { time: '16:02:45', asset: 'VRA/USDT', price: 4248.50, size: 50.00, side: 'sell', status: 'filled' },
    { time: '15:58:20', asset: 'VRA/USDT', price: 4245.00, size: 210.40, side: 'buy', status: 'filled' },
    { time: '15:42:11', asset: 'VRA/USDT', price: 4238.10, size: 15.00, side: 'buy', status: 'filled' },
    { time: '15:12:04', asset: 'VRA/USDT', price: 4260.00, size: 85.00, side: 'sell', status: 'filled' },
  ];

  return (
    <div className="min-h-screen text-white font-sans pb-12">
      {/* Trading Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6 pt-2">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600/20 rounded-xl flex items-center justify-center border border-indigo-500/30">
              <Zap size={20} className="text-indigo-400" />
            </div>
            <div>
              <h2 className="text-xl font-black italic tracking-tighter uppercase">VRA / USDT</h2>
              <div className="flex items-center gap-2">
                 <span className="text-[10px] font-mono text-emerald-400 tracking-wider">LIVE_FEED</span>
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="hidden lg:flex items-center gap-8 border-l border-white/10 pl-8">
            <div>
              <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-0.5">Price</p>
              <p className="text-lg font-bold italic">{formatValue(4250.10)}</p>
            </div>
            <div>
              <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-0.5">24h Change</p>
              <p className="text-sm font-bold text-emerald-400">+{formatValue(242.40)} (5.8%)</p>
            </div>
            <div>
              <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-0.5">24h High</p>
              <p className="text-sm font-bold text-slate-300">{formatValue(4288.10)}</p>
            </div>
            <div>
              <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-0.5">24h Low</p>
              <p className="text-sm font-bold text-slate-300">{formatValue(3992.50)}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-bold hover:bg-white/10 transition-colors flex items-center gap-2">
            <Search size={14} className="text-slate-500" />
            VRA_ASSET
          </button>
          <button className="p-2 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors">
            <Settings2 size={16} className="text-slate-400" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Market Data Feed (Order Book) */}
        <div className="lg:col-span-3 order-2 lg:order-1 flex flex-col gap-4">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl flex flex-col overflow-hidden">
            <div className="p-4 border-bottom border-white/10 flex items-center justify-between">
               <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                 <Layers size={14} className="text-indigo-400" />
                 Order Book
               </h3>
               <div className="flex gap-1">
                 <div className="w-4 h-4 bg-emerald-500/20 rounded-sm" />
                 <div className="w-4 h-4 bg-rose-500/20 rounded-sm" />
                 <div className="w-4 h-4 bg-slate-500/20 rounded-sm" />
               </div>
            </div>
            
            <div className="p-2">
              <div className="grid grid-cols-3 text-[9px] font-mono text-slate-500 uppercase tracking-tighter px-2 mb-2">
                <span>Price (USDT)</span>
                <span className="text-right">Size (VRA)</span>
                <span className="text-right">Total</span>
              </div>

              {/* Asks (Sells) */}
              <div className="space-y-0.5 mb-4">
                {orderBook.asks.map((ask, i) => (
                  <div key={i} className="relative group cursor-pointer h-6 flex items-center px-2">
                    <div 
                      className="absolute right-0 top-0 bottom-0 bg-rose-500/5 transition-all duration-300"
                      style={{ width: `${(ask.total / 6) * 100}%` }}
                    />
                    <div className="grid grid-cols-3 w-full text-[11px] font-mono relative z-10">
                      <span className="text-rose-400 font-bold">{ask.price.toFixed(2)}</span>
                      <span className="text-right text-slate-300">{ask.size.toFixed(2)}</span>
                      <span className="text-right text-slate-500">{ask.total.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Spread */}
              <div className="px-4 py-3 border-y border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-black text-emerald-400">{formatValue(4250.10, { notation: 'standard' }).replace(/^[^\d]*/, '')}</span>
                  <ArrowUpRight size={14} className="text-emerald-400" />
                </div>
                <span className="text-[9px] font-mono text-slate-500">{formatValue(4249.95)} Index</span>
              </div>

              {/* Bids (Buys) */}
              <div className="space-y-0.5 mt-4">
                {orderBook.bids.map((bid, i) => (
                  <div key={i} className="relative group cursor-pointer h-6 flex items-center px-2">
                    <div 
                      className="absolute right-0 top-0 bottom-0 bg-emerald-500/5 transition-all duration-300"
                      style={{ width: `${(bid.total / 7) * 100}%` }}
                    />
                    <div className="grid grid-cols-3 w-full text-[11px] font-mono relative z-10">
                      <span className="text-emerald-400 font-bold">{bid.price.toFixed(2)}</span>
                      <span className="text-right text-slate-300">{bid.size.toFixed(2)}</span>
                      <span className="text-right text-slate-500">{bid.total.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-4">
             <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 mb-4">
               <History size={14} className="text-slate-400" />
               Recent Trades
             </h3>
             <div className="space-y-2">
               {recentTrades.map((trade, i) => (
                 <div key={i} className="flex justify-between items-center text-[11px] font-mono">
                   <span className={trade.side === 'buy' ? 'text-emerald-400' : 'text-rose-400'}>
                     {trade.price.toFixed(2)}
                   </span>
                   <span className="text-slate-300">{trade.size.toFixed(2)}</span>
                   <span className="text-slate-600">{trade.time}</span>
                 </div>
               ))}
             </div>
          </div>
        </div>

        {/* Chart & Active Orders */}
        <div className="lg:col-span-6 order-1 lg:order-2 space-y-4">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-3xl p-6 relative min-h-[500px]">
             <div className="flex items-center justify-between mb-8">
               <div className="flex gap-4">
                 <button className="text-xs font-bold text-white border-b-2 border-indigo-500 pb-1 px-1">Price Chart</button>
                 <button className="text-xs font-bold text-slate-500 hover:text-slate-300 pb-1 px-1 transition-colors">Depth Chart</button>
               </div>
               <div className="flex items-center gap-4">
                  <button 
                    onClick={handleFetchLatest}
                    disabled={isFetching}
                    className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg text-[10px] font-bold hover:bg-emerald-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
                  >
                    <Activity size={12} className={isFetching ? "animate-pulse" : ""} />
                    {isFetching ? "Fetching_Global_Data..." : "Fetch Latest Data"}
                  </button>
                  <div className="flex bg-white/5 p-1 rounded-lg">
                    {['1M', '5M', '15M', '1H', '4H', '1D'].map(t => (
                      <button 
                        key={t} 
                        className={`px-3 py-1 rounded-md text-[10px] font-bold transition-all ${t === '1H' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                  <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
                    <Maximize2 size={16} className="text-slate-400" />
                  </button>
               </div>
             </div>

             <div className="h-[400px] w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <ComposedChart data={data}>
                   <defs>
                     <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                       <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2}/>
                       <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                     </linearGradient>
                   </defs>
                   <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                   <XAxis dataKey="time" stroke="#4b5563" fontSize={10} tickLine={false} axisLine={false} />
                   <YAxis 
                     orientation="right" 
                     stroke="#4b5563" 
                     fontSize={10} 
                     tickLine={false} 
                     axisLine={false} 
                     domain={['dataMin - 100', 'dataMax + 100']}
                   />
                   <Tooltip 
                     contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '12px', fontSize: '10px' }}
                     itemStyle={{ color: '#fff' }}
                   />
                   <Area type="monotone" dataKey="price" stroke="none" fill="url(#chartGradient)" />
                   <Bar dataKey="volume" fill="#1f2937" yAxisId={1} hide />
                   <Line type="monotone" dataKey="price" stroke="#6366f1" strokeWidth={2} dot={false} animationDuration={1000} />
                 </ComposedChart>
               </ResponsiveContainer>
             </div>

             <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between text-[10px] font-mono text-slate-500 pointer-events-none">
                <div className="flex gap-4">
                  <span>O: <span className="text-slate-300">4,250.10</span></span>
                  <span>H: <span className="text-emerald-400">4,288.10</span></span>
                  <span>L: <span className="text-rose-400">4,220.50</span></span>
                  <span>C: <span className="text-slate-300">4,262.40</span></span>
                </div>
                <div>VOL: 12.45M VRA</div>
             </div>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden">
            <div className="p-4 border-b border-white/10 flex gap-6">
              <button 
                onClick={() => setActiveSubTab('orders')}
                className={`text-xs font-bold transition-colors pb-2 ${activeSubTab === 'orders' ? 'text-indigo-400 border-b-2 border-indigo-400' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Active Orders (2)
              </button>
              <button 
                onClick={() => setActiveSubTab('history')}
                className={`text-xs font-bold transition-colors pb-2 ${activeSubTab === 'history' ? 'text-indigo-400 border-b-2 border-indigo-400' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Trade History
              </button>
              <button 
                onClick={() => setActiveSubTab('positions')}
                className={`text-xs font-bold transition-colors pb-2 ${activeSubTab === 'positions' ? 'text-indigo-400 border-b-2 border-indigo-400' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Positions
              </button>
            </div>
            <div className="p-4">
              {activeSubTab === 'orders' && (
                <table className="w-full text-left text-[11px] font-mono">
                  <thead>
                    <tr className="text-slate-500 uppercase tracking-widest">
                      <th className="pb-3 font-medium">Time</th>
                      <th className="pb-3 font-medium">Asset</th>
                      <th className="pb-3 font-medium">Type</th>
                      <th className="pb-3 font-medium">Side</th>
                      <th className="pb-3 font-medium text-right">Price</th>
                      <th className="pb-3 font-medium text-right">Amount</th>
                      <th className="pb-3 font-medium text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    <tr className="border-t border-white/5">
                      <td className="py-3">16:05:22</td>
                      <td className="py-3 font-bold text-white uppercase italic">VRA/USDT</td>
                      <td className="py-3 uppercase text-slate-500">Limit</td>
                      <td className="py-3 text-emerald-400 font-black uppercase italic tracking-tighter">Buy</td>
                      <td className="py-3 text-right text-white font-black">{formatValue(4248.50)}</td>
                      <td className="py-3 text-right">240.00</td>
                      <td className="py-3 text-right">
                        <button className="text-rose-400 font-black uppercase text-[9px] hover:text-rose-300 transition-colors bg-rose-500/10 px-2 py-1 rounded-md border border-rose-500/20">Cancel</button>
                      </td>
                    </tr>
                    <tr className="border-t border-white/5">
                      <td className="py-3">11:12:05</td>
                      <td className="py-3 font-bold text-white uppercase italic">VRA/USDT</td>
                      <td className="py-3 uppercase text-slate-500">Limit</td>
                      <td className="py-3 text-rose-400 font-black uppercase italic tracking-tighter">Sell</td>
                      <td className="py-3 text-right text-white font-black">{formatValue(4350.00)}</td>
                      <td className="py-3 text-right">100.00</td>
                      <td className="py-3 text-right">
                        <button className="text-rose-400 font-black uppercase text-[9px] hover:text-rose-300 transition-colors bg-rose-500/10 px-2 py-1 rounded-md border border-rose-500/20">Cancel</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              )}

              {activeSubTab === 'history' && (
                <table className="w-full text-left text-[11px] font-mono">
                  <thead>
                    <tr className="text-slate-500 uppercase tracking-widest">
                      <th className="pb-3 font-medium">Time</th>
                      <th className="pb-3 font-medium">Asset</th>
                      <th className="pb-3 font-medium text-right">Price</th>
                      <th className="pb-3 font-medium text-right">Size</th>
                      <th className="pb-3 font-medium text-center">Side</th>
                      <th className="pb-3 font-medium text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    {tradeHistoryData.map((trade, i) => (
                      <tr key={i} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                        <td className="py-3">{trade.time}</td>
                        <td className="py-3 font-bold text-white uppercase italic">{trade.asset}</td>
                        <td className="py-3 text-right text-white font-black">{formatValue(trade.price)}</td>
                        <td className="py-3 text-right">{trade.size.toFixed(2)}</td>
                        <td className="py-3 text-center">
                          <span className={`px-2 py-0.5 rounded-md text-[9px] font-black uppercase italic tracking-tighter ${trade.side === 'buy' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                            {trade.side}
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                             <div className="w-1 h-1 rounded-full bg-emerald-500" />
                             <span className="text-[9px] font-black uppercase text-slate-500 tracking-widest">{trade.status}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {activeSubTab === 'positions' && (
                <div className="py-12 flex flex-col items-center justify-center text-center">
                   <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 mb-4">
                      <Target size={20} className="text-slate-500" />
                   </div>
                   <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">No Active Positions Detected</p>
                   <p className="text-[9px] text-slate-600 mt-1 uppercase italic font-mono">Neural_Scanner_Nominal_Alpha_0</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Order Form */}
        <div className="lg:col-span-3 order-3 flex flex-col gap-4">
          <div className={`bg-[#0a0a0a] border rounded-2xl p-6 flex flex-col gap-6 transition-all duration-500 ${side === 'buy' ? 'border-emerald-500/20 shadow-[0_0_40px_rgba(16,185,129,0.05)]' : 'border-rose-500/20 shadow-[0_0_40px_rgba(244,63,94,0.05)]'}`}>
            <div className="flex p-1 bg-white/5 rounded-xl">
              <button 
                onClick={() => setSide('buy')}
                className={`flex-1 py-3 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${side === 'buy' ? 'bg-emerald-500 text-black shadow-[0_0_20px_rgba(16,185,129,0.3)]' : 'text-slate-500 hover:text-white'}`}
              >
                Buy
              </button>
              <button 
                onClick={() => setSide('sell')}
                className={`flex-1 py-3 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${side === 'sell' ? 'bg-rose-500 text-black shadow-[0_0_20px_rgba(244,63,94,0.3)]' : 'text-slate-500 hover:text-white'}`}
              >
                Sell
              </button>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {(['limit', 'market', 'stop'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === tab ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-400'}`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                  <span className={priceError ? 'text-rose-400 font-black' : ''}>Price</span>
                  <span>USDT</span>
                </div>
                <div className={`flex items-center bg-black border rounded-xl p-3 transition-colors group ${priceError ? 'border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.1)]' : 'border-white/10 focus-within:border-indigo-500'}`}>
                  <input 
                    type="number" 
                    value={price} 
                    onChange={e => {
                      setPrice(e.target.value);
                      if (priceError) setPriceError(null);
                    }}
                    onBlur={() => validateInputs()}
                    className="bg-transparent w-full outline-none font-bold italic text-lg [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none placeholder:text-slate-800"
                    placeholder="0.00"
                    disabled={activeTab === 'market'}
                  />
                  {activeTab === 'market' && <span className="text-[10px] text-slate-600 font-bold italic">Latest Market</span>}
                </div>
                <AnimatePresence>
                  {priceError && (
                    <motion.p 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="text-[9px] font-black uppercase text-rose-500 tracking-widest italic"
                    >
                      {priceError}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                  <span className={amountError ? 'text-rose-400 font-black' : ''}>Amount</span>
                  <span>VRA</span>
                </div>
                <div className={`flex items-center bg-black border rounded-xl p-3 transition-colors ${amountError ? 'border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.1)]' : 'border-white/10 focus-within:border-indigo-500'}`}>
                  <input 
                    type="number" 
                    value={amount} 
                    onChange={e => {
                      setAmount(e.target.value);
                      if (amountError) setAmountError(null);
                    }}
                    onBlur={() => validateInputs()}
                    className="bg-transparent w-full outline-none font-bold italic text-lg [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none placeholder:text-slate-800"
                    placeholder="0.00"
                  />
                </div>
                <AnimatePresence>
                  {amountError && (
                    <motion.p 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="text-[9px] font-black uppercase text-rose-500 tracking-widest italic"
                    >
                      {amountError}
                    </motion.p>
                  )}
                </AnimatePresence>
                <div className="grid grid-cols-4 gap-2 pt-2">
                   {['25%', '50%', '75%', 'MAX'].map(p => (
                     <button key={p} className="py-1 bg-white/5 hover:bg-white/10 border border-white/5 rounded-md text-[9px] font-bold text-slate-500 transition-colors">
                       {p}
                     </button>
                   ))}
                </div>
              </div>

              <div className="pt-4 border-t border-white/5 space-y-2">
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-slate-500">Estimated Total:</span>
                  <span className={`font-black italic ${total > 0 ? 'text-white' : 'text-slate-700'}`}>{formatValue(total)}</span>
                </div>
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-slate-500">Balance:</span>
                  <span className="text-slate-300">12,450.00 USDT</span>
                </div>
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-slate-500">Fee:</span>
                  <span className="text-slate-300">0.05% ($2.12)</span>
                </div>
              </div>

              <button 
                onClick={handleOpenOrder}
                className={`w-full py-5 rounded-2xl font-black uppercase tracking-widest text-sm transition-all relative overflow-hidden group ${side === 'buy' ? 'bg-emerald-500 hover:bg-emerald-400 text-black' : 'bg-rose-500 hover:bg-rose-400 text-black'}`}
              >
                <div className="absolute inset-x-0 bottom-0 h-1 bg-black/20" />
                <span className="relative z-10 flex items-center justify-center gap-2">
                  {side === 'buy' ? 'Open Long' : 'Open Short'}
                  <ArrowRight size={18} />
                </span>
              </button>
            </div>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-4">
            <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Info size={14} className="text-indigo-400" />
              Intelligence Insights
            </h5>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                <p className="text-[11px] text-slate-400 leading-relaxed italic">
                  "Institutional buy walls detected at <span className="text-emerald-400 font-bold">$4,220</span>. Short-term momentum is bullish."
                </p>
              </div>
              <div className="flex items-center gap-3 px-1">
                 <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 w-[72%]" />
                 </div>
                 <span className="text-[10px] font-mono text-emerald-400">72% LONG</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isConfirming && pendingOrder && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsConfirming(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="w-full max-w-md bg-[#0d0d0d] border border-white/10 rounded-3xl shadow-2xl relative z-10 overflow-hidden"
            >
              <div className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${pendingOrder.side === 'LONG' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    <Target size={24} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black italic tracking-tighter uppercase">Confirm_Order</h3>
                    <p className="text-[10px] font-mono text-slate-500 tracking-widest uppercase">Verification Required</p>
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="flex justify-between items-center py-3 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Asset_Pair</span>
                    <span className="text-sm font-bold text-white font-mono">{pendingOrder.asset}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Order_Side</span>
                    <span className={`text-sm font-black italic ${pendingOrder.side === 'LONG' ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {pendingOrder.side}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Execution_Type</span>
                    <span className="text-sm font-bold text-slate-300 uppercase font-mono">{pendingOrder.type}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Target_Price</span>
                    <span className="text-sm font-bold text-white font-mono">${pendingOrder.price}</span>
                  </div>
                  <div className="flex justify-between items-center py-3">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Order_Quantity</span>
                    <span className="text-sm font-bold text-white font-mono">{pendingOrder.amount} VRA</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <button 
                    onClick={() => setIsConfirming(false)}
                    className="py-4 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/10 transition-all"
                  >
                    Abort_Order
                  </button>
                  <button 
                    onClick={handleConfirmOrder}
                    className={`py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest text-black shadow-lg transition-all active:scale-95 ${pendingOrder.side === 'LONG' ? 'bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/20' : 'bg-rose-500 hover:bg-rose-400 shadow-rose-500/20'}`}
                  >
                    Confirm_Execution
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
