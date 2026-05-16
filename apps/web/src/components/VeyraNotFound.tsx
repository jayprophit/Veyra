/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { Search, MoveLeft, Terminal } from "lucide-react";
import { VeyraBadge } from "./VeyraBadge";
import { useState } from "react";

interface NotFoundProps {
  onReturn?: () => void;
}

export function VeyraNotFound({ onReturn }: NotFoundProps) {
  const [isExiting, setIsExiting] = useState(false);

  const handleReturn = () => {
    setIsExiting(true);
    setTimeout(() => {
      onReturn?.();
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">
      {/* Background Atmosphere */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-30">
        <div 
          className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-red-900/20 rounded-full blur-[120px]" 
          style={{ animation: 'float 20s infinite alternate' }}
        />
        <div 
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-violet-900/20 rounded-full blur-[150px]" 
          style={{ animation: 'float 25s infinite reverse' }}
        />
      </div>

      <AnimatePresence>
        {!isExiting && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, filter: "blur(20px)" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="z-10 flex flex-col items-center text-center max-w-2xl"
          >
            <div className="mb-8">
              <VeyraBadge tier="404" size="lg" />
            </div>

            <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter mb-4 bg-gradient-to-b from-white to-white/40 bg-clip-text text-transparent italic">
              Lost in the Void
            </h1>
            
            <p className="text-slate-400 text-lg md:text-xl font-mono mb-12 max-w-lg leading-relaxed">
              THE DATA ASSET YOU ARE SEEKING HAS TRANSCENDED BEYOND THIS DIMENSION. 
              IT IS NO LONGER PART OF THE LOCAL QUANTUM STATE.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 items-center">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleReturn}
                className="flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold uppercase tracking-wider text-sm"
              >
                <MoveLeft size={18} />
                Return to Core
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.1)' }}
                className="flex items-center gap-2 border border-white/20 px-8 py-4 rounded-full font-bold uppercase tracking-wider text-sm transition-colors"
              >
                <Terminal size={18} />
                Check System Logs
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Decorative Matrix Elements */}
      <div className="absolute bottom-10 left-10 text-[10px] font-mono text-slate-800 hidden md:block">
        <p>VEYRA_OS_V12.4.0_FINAL</p>
        <p>SYSTEM_STATUS: ERROR_ASSET_NULL</p>
        <p>LATENCY: 0.0003MS</p>
      </div>

      <div className="absolute bottom-10 right-10 flex items-center gap-4 text-slate-500 opacity-50">
        <Search size={16} />
        <span className="text-xs uppercase tracking-[0.3em]">Search Miss</span>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes float {
          0% { transform: translate(0, 0) scale(1); }
          100% { transform: translate(50px, 30px) scale(1.1); }
        }
      `}} />
    </div>
  );
}
