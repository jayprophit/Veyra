import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Brain, 
  Upload, 
  Settings2, 
  Play, 
  Clock, 
  History, 
  ChevronRight, 
  Database, 
  Cpu, 
  Zap,
  CheckCircle2,
  AlertCircle,
  FileJson,
  X
} from "lucide-react";

interface ModelVersion {
  id: string;
  name: string;
  accuracy: string;
  loss: string;
  timestamp: string;
  status: 'deployed' | 'archive';
}

export function VeyraModelTraining() {
  const [isTraining, setIsTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState<'config' | 'logs'>('config');
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [versions, setVersions] = useState<ModelVersion[]>([
    { id: "V12.4.1", name: "Alpha_Liquidity_Splicer", accuracy: "98.2%", loss: "0.002", timestamp: "12h ago", status: 'deployed' },
    { id: "V12.4.0", name: "Beta_Sentiment_Kernel", accuracy: "94.5%", loss: "0.041", timestamp: "2d ago", status: 'archive' },
    { id: "V12.3.9", name: "Old_Genesis_Grid", accuracy: "91.2%", loss: "0.082", timestamp: "5d ago", status: 'archive' },
  ]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'deployed' | 'archive'>('all');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const filteredVersions = versions.filter(v => 
    statusFilter === 'all' ? true : v.status === statusFilter
  );

  const startTraining = () => {
    setIsTraining(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsTraining(false);
          // Add new version on complete
          const newId = `V12.4.${versions.length + 1}`;
          setVersions(prevVersions => [
            { 
              id: newId, 
              name: `Forge_Result_${Math.floor(Math.random() * 1000)}`, 
              accuracy: `${(99 + Math.random() * 0.9).toFixed(1)}%`, 
              loss: `${(Math.random() * 0.001).toFixed(4)}`, 
              timestamp: "Just now", 
              status: 'archive' 
            },
            ...prevVersions
          ]);
          setUploadProgress(null);
          setUploadedFile(null);
          return 100;
        }
        return prev + 1;
      });
    }, 100);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setUploadedFile(file);
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev !== null && prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return (prev || 0) + 10;
        });
      }, 200);
    }
  };

  return (
    <div className="space-y-12 pb-24">
      {/* Header */}
      <header className="max-w-3xl">
         <h2 className="text-5xl md:text-7xl font-black italic tracking-tighter uppercase text-white mb-6">Neural_Forge</h2>
         <p className="text-base font-bold text-slate-500 uppercase italic tracking-widest leading-relaxed border-l-2 border-indigo-500/30 pl-8">
            TRAIN PROPRIETARY LIQUIDITY MODELS USING GLOBAL DATASET CLUSTERS. CONFIGURE HYPERPARAMETERS FOR SUB-MILLISECOND SIGNAL EXTRACTION.
         </p>
      </header>

      <div className="grid lg:grid-cols-12 gap-10">
        {/* Main Workspace */}
        <div className="lg:col-span-8 space-y-8">
           {/* Dataset Upload Area */}
           <div 
             onClick={() => fileInputRef.current?.click()}
             className="bg-[#0a0a0a] border-2 border-dashed border-white/10 rounded-[3.5rem] p-16 flex flex-col items-center justify-center text-center group cursor-pointer hover:border-indigo-500/30 hover:bg-white/[0.02] transition-all relative overflow-hidden"
           >
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                onChange={handleFileUpload}
                accept=".json,.csv,.bin"
              />
              <div className="absolute top-0 left-0 w-full h-1">
                 {uploadProgress !== null && uploadProgress < 100 && (
                   <motion.div 
                     initial={{ width: 0 }}
                     animate={{ width: `${uploadProgress}%` }}
                     className="h-full bg-indigo-500"
                   />
                 )}
              </div>
              
              <div className="w-20 h-20 bg-white/5 rounded-[2rem] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                 {uploadProgress === 100 ? (
                   <div className="relative">
                      <CheckCircle2 className="text-emerald-500" size={32} />
                      <div className="absolute inset-0 bg-emerald-500/20 blur-xl animate-pulse" />
                   </div>
                 ) : (
                   <Upload className="text-slate-600 group-hover:text-indigo-400 transition-colors" size={32} />
                 )}
              </div>
              <h4 className="text-xl font-black italic uppercase text-white mb-2">
                {uploadProgress === 100 ? `DATASET_READY: ${uploadedFile?.name || 'VRA_BUNDLE'}` : 'Upload_Training_Dataset'}
              </h4>
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                {uploadProgress === 100 ? `${(uploadedFile?.size || 0 / 1024 / 1024).toFixed(2)} MB • VERIFIED_BLAKE3_HASH` : 'Drag .JSON, .CSV or .BIN Liquidity Bundles'}
              </p>
           </div>

           {/* Configuration Panel */}
           <div className="bg-[#0a0a0a] border border-white/5 rounded-[3.5rem] overflow-hidden">
              <AnimatePresence>
                {isTraining && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-b border-white/5 bg-white/[0.01]"
                  >
                    <div className="p-10 space-y-6">
                      <div className="flex justify-between items-end">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em]">Neural_Sync_Active</span>
                          </div>
                          <h4 className="text-3xl font-black italic text-white uppercase tracking-tighter">Forge_In_Progress</h4>
                        </div>
                        <div className="text-right">
                          <motion.span 
                            key={progress}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-4xl font-black italic text-white uppercase tracking-tighter tabular-nums"
                          >
                            {progress}%
                          </motion.span>
                        </div>
                      </div>
                      <div className="h-6 bg-white/5 rounded-2xl overflow-hidden relative p-1 border border-white/5">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${progress}%` }}
                          className="h-full bg-gradient-to-r from-indigo-600 via-indigo-500 to-indigo-400 rounded-xl relative shadow-[0_0_30px_rgba(99,102,241,0.2)]"
                        >
                          <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent)] w-1/2 animate-[shimmer_2s_infinite]" />
                        </motion.div>
                      </div>
                      <div className="flex justify-between items-center text-[8px] font-black text-slate-600 uppercase tracking-widest">
                        <span>Cluster_Prophit_Node_A100</span>
                        <span>Estimated_Time_Remaining: {Math.max(0, (100 - progress) * 0.1).toFixed(1)}m</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="flex border-b border-white/5">
                 {['config', 'logs'].map((tab) => (
                   <button 
                     key={tab}
                     onClick={() => setActiveTab(tab as any)}
                     className={`px-10 py-6 text-[10px] font-black uppercase tracking-widest transition-all ${
                       activeTab === tab ? 'text-white bg-white/5 border-b-2 border-indigo-500' : 'text-slate-500 hover:text-white'
                     }`}
                   >
                     {tab === 'config' ? 'Hyper_Parameters' : 'Epoch_Telemetry'}
                   </button>
                 ))}
              </div>

              <div className="p-12">
                 <AnimatePresence mode="wait">
                    {activeTab === 'config' ? (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-10"
                      >
                         <div className="grid sm:grid-cols-2 gap-10">
                            {[
                              { label: 'Learning_Rate', val: '0.0001', icon: Zap },
                              { label: 'Batch_Size', val: '2,048', icon: Database },
                              { label: 'Epoch_Count', val: '500', icon: Clock },
                              { label: 'Hidden_Layers', val: '12_Block', icon: Cpu },
                            ].map((param, i) => (
                              <div key={i} className="space-y-4">
                                 <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                       <param.icon size={12} className="text-slate-600" />
                                       <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{param.label}</span>
                                    </div>
                                    <span className="text-[10px] font-mono text-white">{param.val}</span>
                                 </div>
                                 <div className="h-1.5 bg-white/5 rounded-full relative">
                                    <div className="absolute top-0 left-0 h-full w-2/3 bg-indigo-500/30 rounded-full" />
                                    <div className="absolute top-1/2 left-[66%] -translate-y-1/2 w-4 h-4 rounded-full bg-white shadow-xl cursor-grab" />
                                 </div>
                              </div>
                            ))}
                         </div>

                         <div className="pt-10 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-6">
                            <div className="flex items-center gap-6">
                               <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                                  <span className="text-[10px] font-black text-emerald-500 uppercase italic">GCP_A100_AUTO_SYNC</span>
                               </div>
                               <div className="flex items-center gap-2">
                                  <AlertCircle size={14} className="text-slate-700" />
                                  <span className="text-[10px] font-black text-slate-700 uppercase">Estimated_Time: 12.4m</span>
                               </div>
                            </div>
                            <button 
                              onClick={startTraining}
                              disabled={isTraining || uploadProgress !== 100}
                              className="px-12 py-5 bg-indigo-500 text-white font-black uppercase text-[10px] tracking-widest rounded-2xl hover:bg-indigo-400 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed shadow-2xl shadow-indigo-500/20 flex items-center gap-3"
                            >
                               {isTraining ? 'Training_In_Progress...' : 'Initiate_Neural_Forge'} <Play size={14} className="fill-white" />
                            </button>
                         </div>
                      </motion.div>
                    ) : (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-4 font-mono text-[10px] h-[300px] overflow-y-auto scrollbar-hide"
                      >
                         {isTraining ? (
                           <>
                             <div className="text-emerald-500">[SYSTEM] INITIALIZING GPU_CLUSTER_PROPHIT_01...</div>
                             <div className="text-slate-500">[KERNAL] ALLOCATING 24GB VRAM FOR LIQUIDITY_BATCH_001</div>
                             <div className="text-white">EPOCH 01/500 - LOSS: 0.842 - ACC: 0.124</div>
                             <div className="text-white">EPOCH 42/500 - LOSS: 0.322 - ACC: 0.442</div>
                             <div className="text-white">EPOCH {Math.floor(progress * 5)}/500 - LOSS: {(1 - progress/100).toFixed(3)} - ACC: {(progress/100).toFixed(3)}</div>
                           </>
                         ) : (
                           <div className="text-slate-800 italic uppercase">Waiting for training cycle...</div>
                         )}
                      </motion.div>
                    )}
                 </AnimatePresence>
              </div>
           </div>
        </div>

        {/* Model Versioning Sidebar */}
        <div className="lg:col-span-4 space-y-8">
           <div className="bg-zinc-950 border border-white/5 rounded-[3.5rem] p-10">
              <div className="flex items-center justify-between mb-10">
                 <div className="flex items-center gap-4">
                    <History size={24} className="text-slate-600" />
                    <h5 className="text-[10px] font-black uppercase text-slate-500 tracking-[0.4em]">Model_History</h5>
                 </div>
                 <div className="flex gap-1 bg-white/5 p-1 rounded-xl border border-white/5">
                   {(['all', 'deployed', 'archive'] as const).map((f) => (
                     <button 
                       key={f}
                       onClick={() => setStatusFilter(f)}
                       className={`px-3 py-1.5 rounded-lg text-[8px] font-black uppercase tracking-widest transition-all ${statusFilter === f ? 'bg-indigo-500 text-black shadow-lg shadow-indigo-500/20' : 'text-slate-500 hover:text-white'}`}
                     >
                       {f[0]}
                     </button>
                   ))}
                </div>
              </div>

              <div className="space-y-6">
                 {filteredVersions.map((v) => (
                   <div key={v.id} className="p-6 bg-white/2 border border-white/5 rounded-3xl hover:bg-white/5 transition-all group cursor-help">
                      <div className="flex justify-between items-start mb-4">
                         <div>
                            <p className="text-[10px] font-black text-white uppercase italic group-hover:text-indigo-400 transition-colors">{v.name}</p>
                            <p className="text-[9px] font-mono text-slate-600 uppercase">{v.id}</p>
                         </div>
                         <div className={`px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest ${v.status === 'deployed' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-500/10 text-slate-500'}`}>
                            {v.status}
                         </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                         <div className="p-3 bg-black/40 rounded-xl border border-white/5">
                            <p className="text-[8px] font-black text-slate-600 uppercase mb-1">Accuracy</p>
                            <p className="text-sm font-black italic text-white uppercase">{v.accuracy}</p>
                         </div>
                         <div className="p-3 bg-black/40 rounded-xl border border-white/5">
                            <p className="text-[8px] font-black text-slate-600 uppercase mb-1">Loss</p>
                            <p className="text-sm font-black italic text-white uppercase">{v.loss}</p>
                         </div>
                      </div>
                      <div className="flex items-center justify-between">
                         <span className="text-[8px] font-mono text-slate-700">{v.timestamp}</span>
                         <button className="text-[9px] font-black text-slate-500 uppercase hover:text-white transition-colors flex items-center gap-1 group/btn">
                            Deploy_Kernel <ChevronRight size={10} className="group-hover/btn:translate-x-1 transition-transform" />
                         </button>
                      </div>
                   </div>
                 ))}
              </div>

              <button className="w-full mt-10 py-5 bg-white/[0.03] border border-white/5 rounded-2xl text-[10px] font-black uppercase text-slate-500 hover:bg-white/5 hover:text-white transition-all">
                Export_All_Manifests
              </button>
           </div>

           {/* Resource Usage Card */}
           <div className="bg-indigo-600 rounded-[3rem] p-10 text-white relative overflow-hidden group">
              <div className="absolute -right-8 -bottom-8 opacity-10 group-hover:scale-110 transition-transform">
                 <Brain size={160} />
              </div>
              <h5 className="text-xl font-black italic tracking-tighter uppercase mb-2">Neural_Compute</h5>
              <p className="text-[10px] font-bold text-indigo-100 uppercase italic mb-8">
                Your current cycle is utilizing 0.2% of the Veyra Transcendent Grid.
              </p>
              <div className="h-px bg-white/20 mb-8" />
              <div className="flex justify-between items-center">
                 <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                    <span className="text-[10px] font-black uppercase">Nodes Active: 12,402</span>
                 </div>
                 <ChevronRight size={20} />
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
