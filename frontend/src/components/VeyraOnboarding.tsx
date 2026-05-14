/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  ShieldCheck, 
  Terminal, 
  Cpu, 
  Globe, 
  ArrowRight, 
  Zap,
  CheckCircle2,
  ChevronRight,
  Sparkles
} from "lucide-react";
import { VeyraLogo } from "./VeyraLogo";

interface Step {
  title: string;
  description: string;
  icon: any;
  color: string;
}

const steps: Step[] = [
  {
    title: "Kernel_Initialization",
    description: "Welcome to Veyra Labs. Your identity kernel is now synchronized with the global extraction grid.",
    icon: ShieldCheck,
    color: "text-indigo-400"
  },
  {
    title: "Protocol_Extraction",
    description: "Our high-latency extraction labs allow you to mine liquidity across 12 unique tiers of neural depth.",
    icon: Pickaxe,
    color: "text-emerald-400"
  },
  {
    title: "Neural_Trading",
    description: "Access the terminal to execute trades with sub-millisecond precision using the forged assets.",
    icon: Terminal,
    color: "text-amber-400"
  },
  {
    title: "Network_Status",
    description: "Monitor your cluster status and manage your Transcendent tier identity from the manifest.",
    icon: Globe,
    color: "text-violet-400"
  }
];

function Pickaxe(props: any) {
  return <Zap {...props} />; // Using alternative icon for variety
}

export function VeyraOnboarding({ onComplete }: { onComplete: () => void }) {
  const [currentStep, setCurrentStep] = useState(0);

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/90 backdrop-blur-2xl">
      <AnimatePresence mode="wait">
        <motion.div 
          key={currentStep}
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 1.1, y: -20 }}
          className="w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-[3rem] p-12 relative overflow-hidden"
        >
          {/* Progress Indicator */}
          <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              className="h-full bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.5)]"
            />
          </div>

          <div className="space-y-12">
            <header className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-6">
                <VeyraLogo size="lg" />
                <div className="h-12 w-px bg-white/10 hidden sm:block" />
                <div>
                   <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1 italic">Protocol_Onboarding_Step_{currentStep + 1}</p>
                   <h2 className="text-3xl font-black italic text-white uppercase tracking-tighter">
                     {steps[currentStep].title}
                   </h2>
                </div>
              </div>
              <div className="text-right">
                <span className="text-4xl font-black italic text-slate-800 tabular-nums">0{currentStep + 1}</span>
              </div>
            </header>

            <div className="space-y-6">
              <p className="text-xl font-bold text-slate-400 italic leading-relaxed uppercase tracking-wide">
                {steps[currentStep].description}
              </p>

              <div className="flex gap-2">
                {steps.map((_, i) => (
                  <div 
                    key={i} 
                    className={`h-1 rounded-full transition-all duration-500 ${i <= currentStep ? 'w-8 bg-indigo-500' : 'w-2 bg-white/5'}`} 
                  />
                ))}
              </div>
            </div>

            <footer className="flex justify-between items-center border-t border-white/5 pt-8">
              <button 
                onClick={onComplete}
                className="text-[10px] font-black text-slate-600 uppercase tracking-widest hover:text-white transition-colors"
              >
                Skip_Calibration
              </button>
              
              <button 
                onClick={nextStep}
                className="flex items-center gap-4 px-10 py-4 bg-white text-black rounded-2xl font-black uppercase text-[10px] tracking-widest hover:scale-105 transition-all shadow-2xl"
              >
                {currentStep === steps.length - 1 ? 'Enter_The_Void' : 'Next_Phase'}
                <ChevronRight size={16} />
              </button>
            </footer>
          </div>

          {/* Decorative Elements */}
          <div className="absolute -right-20 -bottom-20 opacity-5 pointer-events-none">
            {React.createElement(steps[currentStep].icon, { size: 320 })}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
