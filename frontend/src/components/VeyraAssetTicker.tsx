/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { TrendingUp, TrendingDown, Coins, Info, Search, RotateCcw, Bell, ChevronUp, ChevronDown, X } from "lucide-react";
import React, { useState, useMemo } from "react";

type AssetCategory = 'All' | 'Metals' | 'Forex' | 'Crypto' | 'Veyra';
type SortKey = 'symbol' | 'price' | 'change';
type SortDirection = 'asc' | 'desc';

interface PriceAlert {
  symbol: string;
  targetPrice: string;
  condition: 'above' | 'below';
}

const assetsData = [
  { symbol: "XAU", name: "Gold", price: "2,341.20", change: "+1.2%", marketCap: "14.2T", category: 'Metals' },
  { symbol: "XAG", name: "Silver", price: "28.45", change: "-0.5%", marketCap: "1.3T", category: 'Metals' },
  { symbol: "XPT", name: "Platinum", price: "982.10", change: "+0.8%", marketCap: "240B", category: 'Metals' },
  { symbol: "VRA", name: "Veyra Utility", price: "12.44", change: "+5.1%", marketCap: "12.4B", category: 'Veyra' },
  { symbol: "LITH", name: "Lithium", price: "14,200", change: "-2.3%", marketCap: "820B", category: 'Metals' },
  { symbol: "CU", name: "Copper", price: "4.55", change: "+0.2%", marketCap: "45B", category: 'Metals' },
  { symbol: "BTC", name: "Bitcoin", price: "64,231.50", change: "+2.4%", marketCap: "1.2T", category: 'Crypto' },
  { symbol: "ETH", name: "Ethereum", price: "3,452.12", change: "+1.8%", marketCap: "412B", category: 'Crypto' },
  { symbol: "EUR/USD", name: "Euro / US Dollar", price: "1.0842", change: "-0.1%", marketCap: "N/A", category: 'Forex' },
];

export function VeyraAssetTicker() {
  const [hoveredAsset, setHoveredAsset] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<AssetCategory>('All');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: SortDirection }>({ key: 'symbol', direction: 'asc' });
  const [alertConfigAsset, setAlertConfigAsset] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);

  const filteredAndSortedAssets = useMemo(() => {
    let result = assetsData.filter(asset => {
      const matchesSearch = asset.symbol.toLowerCase().includes(searchQuery.toLowerCase()) || 
                           asset.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = activeFilter === 'All' || asset.category === activeFilter;
      return matchesSearch && matchesFilter;
    });

    result.sort((a, b) => {
      let valA: any = a[sortConfig.key];
      let valB: any = b[sortConfig.key];

      if (sortConfig.key === 'price') {
        valA = parseFloat(a.price.replace(/,/g, ''));
        valB = parseFloat(b.price.replace(/,/g, ''));
      } else if (sortConfig.key === 'change') {
        valA = parseFloat(a.change.replace(/[+%]/g, ''));
        valB = parseFloat(b.change.replace(/[+%]/g, ''));
      }

      if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
      if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [searchQuery, activeFilter, sortConfig]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const sanitized = value.replace(/[^a-zA-Z0-9\s\/\-]/g, '');
    setSearchQuery(sanitized);
  };

  const handleSort = (key: SortKey) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const toggleAlert = (symbol: string) => {
    setAlertConfigAsset(symbol);
  };

  const categories: AssetCategory[] = ['All', 'Metals', 'Forex', 'Crypto', 'Veyra'];

  return (
    <div className="bg-black/60 border border-white/10 rounded-2xl p-6 font-mono relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/2 to-transparent pointer-events-none" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Coins size={14} className="text-amber-400 border border-amber-400/20 rounded-full p-0.5" />
            <span className="text-[10px] font-black text-white uppercase tracking-widest italic">Market_Feeds (V.12)</span>
          </div>
          <div className="flex items-center gap-3">
             <motion.button 
               onClick={handleRefresh}
               disabled={isRefreshing}
               whileTap={{ scale: 0.9 }}
               animate={isRefreshing ? { rotate: 360 } : { rotate: 0 }}
               transition={isRefreshing ? { repeat: Infinity, duration: 1, ease: "linear" } : { duration: 0.5 }}
               className={`text-slate-500 hover:text-white transition-colors p-1 rounded-full hover:bg-white/5 ${isRefreshing ? 'text-indigo-400' : ''}`}
             >
                <RotateCcw size={12} />
             </motion.button>
             <div className="flex items-center gap-2 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
               <div className="w-1 h-1 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
               <span className="text-[7px] font-black text-emerald-400 tracking-tighter">LIVE_FEED</span>
             </div>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="space-y-4 mb-6">
          <div className="relative group">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-indigo-400 transition-colors" />
            <input 
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="SEARCH_ASSETS..."
              className="w-full bg-white/[0.02] border border-white/10 rounded-xl py-2.5 pl-9 pr-4 text-[10px] font-bold text-slate-300 focus:outline-none focus:border-indigo-500/40 focus:bg-white/[0.05] transition-all uppercase tracking-widest placeholder:text-slate-700 font-sans"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveFilter(cat)}
                className={`px-3 py-1.5 rounded-lg text-[8px] font-black uppercase tracking-widest transition-all relative ${
                  activeFilter === cat 
                    ? 'bg-indigo-500 text-black shadow-[0_0_20px_rgba(99,102,241,0.4)]' 
                    : 'bg-white/5 text-slate-500 hover:text-white hover:bg-white/10'
                }`}
              >
                {cat}
                {activeFilter === cat && (
                  <motion.div 
                    layoutId="activeFilter"
                    className="absolute inset-0 rounded-lg border-2 border-white/20"
                    initial={false}
                  />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Sorting Headers */}
        <div className="grid grid-cols-2 gap-3 mb-2 px-1">
          <div className="flex items-center gap-2">
            <button 
              onClick={() => handleSort('symbol')}
              className={`text-[8px] font-black uppercase tracking-widest flex items-center gap-1 transition-colors ${sortConfig.key === 'symbol' ? 'text-indigo-400' : 'text-slate-600 hover:text-slate-400'}`}
            >
              Ticker {sortConfig.key === 'symbol' && (sortConfig.direction === 'asc' ? <ChevronUp size={8} /> : <ChevronDown size={8} />)}
            </button>
          </div>
          <div className="flex items-center justify-end gap-3 pr-2">
            <button 
              onClick={() => handleSort('price')}
              className={`text-[8px] font-black uppercase tracking-widest flex items-center gap-1 transition-colors ${sortConfig.key === 'price' ? 'text-indigo-400' : 'text-slate-600 hover:text-slate-400'}`}
            >
              Price {sortConfig.key === 'price' && (sortConfig.direction === 'asc' ? <ChevronUp size={8} /> : <ChevronDown size={8} />)}
            </button>
            <button 
              onClick={() => handleSort('change')}
              className={`text-[8px] font-black uppercase tracking-widest flex items-center gap-1 transition-colors ${sortConfig.key === 'change' ? 'text-indigo-400' : 'text-slate-600 hover:text-slate-400'}`}
            >
              24H% {sortConfig.key === 'change' && (sortConfig.direction === 'asc' ? <ChevronUp size={8} /> : <ChevronDown size={8} />)}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <AnimatePresence mode="popLayout" initial={false}>
            {filteredAndSortedAssets.map((asset) => (
              <motion.div 
                layout
                initial={{ opacity: 0, scale: 0.9, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: -10 }}
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
                key={asset.symbol} 
                onMouseEnter={() => setHoveredAsset(asset.symbol)}
                onMouseLeave={() => setHoveredAsset(null)}
                whileHover={{ 
                  y: -4,
                  backgroundColor: "rgba(255, 255, 255, 0.08)",
                  borderColor: "rgba(255, 255, 255, 0.2)"
                }}
                className="p-3 bg-white/5 border border-white/5 rounded-lg transition-colors cursor-help relative group/asset"
              >
                {isRefreshing && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-black/40 backdrop-blur-[1px] rounded-lg z-20 flex items-center justify-center overflow-hidden"
                  >
                     <motion.div 
                       animate={{ x: ["-100%", "200%"] }}
                       transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                       className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent skew-x-12"
                     />
                     <div className="w-1 h-1 bg-white/40 rounded-full animate-ping" />
                  </motion.div>
                )}

                <div className="flex justify-between items-start mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black text-slate-300 group-hover/asset:text-white transition-colors">{asset.symbol}</span>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleAlert(asset.symbol);
                      }}
                      className="p-1 rounded-md opacity-0 group-hover/asset:opacity-100 hover:bg-white/10 transition-all text-slate-500 hover:text-amber-400"
                    >
                      <Bell size={10} fill={alerts.some(a => a.symbol === asset.symbol) ? "currentColor" : "none"} />
                    </button>
                  </div>
                  <span className={`text-[8px] font-bold ${asset.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {asset.change}
                  </span>
                </div>
                <div className="text-xs font-black tracking-tight text-white italic transition-transform group-hover/asset:translate-x-0.5">${asset.price}</div>

                <AnimatePresence>
                  {hoveredAsset === asset.symbol && (
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95, y: 5, filter: "blur(4px)" }}
                      animate={{ opacity: 1, scale: 1, y: 0, filter: "blur(0px)" }}
                      exit={{ opacity: 0, scale: 0.95, y: 5, filter: "blur(4px)" }}
                      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                      className="absolute bottom-full left-0 mb-3 w-60 bg-black/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-50 overflow-hidden"
                    >
                      <div className="absolute inset-0 bg-indigo-500/5" />
                      <div className="relative z-10 space-y-3">
                        <div className="flex items-center justify-between">
                           <div className="flex items-center gap-1.5">
                              <div className="w-1 h-1 bg-indigo-400 rounded-full" />
                              <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Market_Dossier</span>
                           </div>
                           <span className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-[6px] font-black text-slate-400 uppercase tracking-tighter">{asset.category}</span>
                        </div>
                        
                        <div>
                          <p className="text-xs font-black text-white uppercase italic tracking-tighter mb-0.5">{asset.name}</p>
                          <p className="text-[9px] font-bold text-slate-500 tabular-nums">${asset.price}</p>
                        </div>

                        <div className="pt-2 border-t border-white/5 grid grid-cols-2 gap-4">
                           <div>
                              <span className="text-[7px] font-black text-slate-600 uppercase block tracking-widest mb-1">24h_Delta</span>
                              <div className={`flex items-center gap-1 text-[9px] font-black ${asset.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {asset.change.startsWith('+') ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                                {asset.change}
                              </div>
                           </div>
                           <div>
                              <span className="text-[7px] font-black text-slate-600 uppercase block tracking-widest mb-1">Cap_Weight</span>
                              <span className="text-[9px] font-black text-indigo-300 tabular-nums">{asset.marketCap}</span>
                           </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Alert Config Modal */}
        <AnimatePresence>
          {alertConfigAsset && (
            <div className="absolute inset-0 z-[100] flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setAlertConfigAsset(null)}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="relative w-full bg-zinc-950 border border-white/10 rounded-2xl p-6 shadow-2xl space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bell size={16} className="text-amber-400" />
                    <h4 className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Set_Price_Alert</h4>
                  </div>
                  <button onClick={() => setAlertConfigAsset(null)} className="text-slate-600 hover:text-white transition-colors">
                    <X size={14} />
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                    <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Asset_Identity</p>
                    <p className="text-sm font-black text-white uppercase italic">{alertConfigAsset}</p>
                  </div>

                  <div className="space-y-2">
                    <p className="text-[8px] font-black text-slate-500 uppercase pl-1">Threshold_Price (USDT)</p>
                    <input 
                      type="number"
                      placeholder="0.00"
                      className="w-full bg-black border border-white/5 rounded-xl p-3 text-xs font-bold text-white focus:outline-none focus:border-indigo-500/50 transition-all"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button className="py-3 bg-white/5 border border-white/5 rounded-xl text-[8px] font-black uppercase text-slate-500 hover:text-white transition-all">Price_Above</button>
                    <button className="py-3 bg-white/5 border border-white/5 rounded-xl text-[8px] font-black uppercase text-slate-500 hover:text-white transition-all">Price_Below</button>
                  </div>
                </div>

                <button 
                  onClick={() => {
                    setAlerts([...alerts, { symbol: alertConfigAsset!, targetPrice: "0", condition: 'above' }]);
                    setAlertConfigAsset(null);
                  }}
                  className="w-full py-4 bg-indigo-500 text-black rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-400 transition-all shadow-lg shadow-indigo-500/20"
                >
                  Save_Alert_Protocol
                </button>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        <div className="mt-6 pt-4 border-t border-white/5 flex gap-2 overflow-x-auto no-scrollbar">
          <div className="shrink-0 px-2 py-1 bg-white/5 rounded text-[7px] text-slate-500">INDICES_LINKED</div>
          <div className="shrink-0 px-2 py-1 bg-white/5 rounded text-[7px] text-slate-500">METALS_SYNC</div>
          <div className="shrink-0 px-2 py-1 bg-white/5 rounded text-[7px] text-slate-500">NEURAL_DATA_V12</div>
        </div>
      </div>
    </div>
  );
}
