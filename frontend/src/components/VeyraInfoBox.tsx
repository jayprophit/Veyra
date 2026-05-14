import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Info, ChevronRight } from 'lucide-react';

interface InfoBoxProps {
  label: string;
  value: string;
  details: { label: string; value: string; }[];
  children?: React.ReactNode;
}

export const VeyraInfoBox: React.FC<InfoBoxProps> = ({ label, value, details, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div 
      className="relative group"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      {children || (
        <div className="flex items-center gap-2 cursor-help group-hover:text-white transition-colors">
          <Info size={14} className="text-slate-600 group-hover:text-indigo-400" />
          <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">{label}</span>
        </div>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="absolute left-0 bottom-full mb-4 w-72 bg-zinc-950 border border-white/10 rounded-[2rem] p-6 shadow-2xl z-[100] backdrop-blur-xl"
          >
            <div className="mb-4">
               <p className="text-[9px] font-black text-slate-600 uppercase tracking-[0.3em] mb-1">{label}</p>
               <h6 className="text-2xl font-black italic tracking-tighter text-white uppercase">{value}</h6>
            </div>
            
            <div className="space-y-3">
              {details.map((detail, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 border-dashed">
                  <span className="text-[10px] font-black text-slate-500 uppercase">{detail.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-white">{detail.value}</span>
                    <ChevronRight size={10} className="text-indigo-500" />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-white/5">
               <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                  <span className="text-[8px] font-black uppercase text-slate-600 tracking-widest">Oracle_Feed_Nominal</span>
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
