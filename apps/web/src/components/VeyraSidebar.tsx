/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, AnimatePresence } from "motion/react";
import { 
  Layout, 
  Landmark, 
  ShieldCheck, 
  ChevronRight,
  ChevronDown, 
  Settings, 
  Briefcase,
  Activity,
  HelpCircle,
  Bell,
  Search,
  Menu,
  Gavel,
  X,
  MessageCircle,
  FileText,
  BookOpen
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { VeyraLogo } from "./VeyraLogo";

interface SidebarProps {
  currentView: string;
  onViewChange: (view: any) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function VeyraSidebar({ currentView, onViewChange, isOpen, onToggle }: SidebarProps) {
  const { user } = useAuth();
  const [expandedGroups, setExpandedGroups] = useState<string[]>(["Foundation", "Operations"]);

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => 
      prev.includes(group) ? prev.filter(g => g !== group) : [...prev, group]
    );
  };

  const SidebarGroup = ({ group, expandedGroups, toggleGroup, currentView, onViewChange, onToggle }: any) => (
    <div className="space-y-1">
      <button 
        onClick={() => toggleGroup(group.name)}
        className="w-full flex items-center justify-between px-4 py-2 text-slate-600 hover:text-slate-400 transition-colors"
      >
        <div className="flex items-center gap-2">
           <group.icon size={14} className="opacity-50" />
           <span className="text-[10px] font-black uppercase tracking-widest">{group.name}</span>
        </div>
        <ChevronDown size={14} className={`transition-transform duration-300 ${expandedGroups.includes(group.name) ? 'rotate-180' : ''}`} />
      </button>
      
      <AnimatePresence initial={false}>
        {expandedGroups.includes(group.name) && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden space-y-1 pl-4"
          >
            {group.items.map((item: any) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onViewChange(item.id);
                    if (window.innerWidth < 1024) onToggle();
                  }}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-bold transition-all group/item ${
                    isActive 
                      ? "bg-white text-black shadow-xl" 
                      : "text-slate-500 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <div className="flex items-center gap-3">
                     <Icon size={18} className={isActive ? "text-black" : "text-slate-700 group-hover/item:text-indigo-400"} />
                     <span className="tracking-tight">{item.label}</span>
                  </div>
                  <ChevronRight size={14} className={`opacity-0 -translate-x-2 transition-all duration-300 group-hover/item:opacity-40 group-hover/item:translate-x-0 ${isActive ? "opacity-0" : ""}`} />
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  const menuGroups = [
    {
      name: "Foundation",
      icon: Landmark,
      items: [
        { id: "dashboard", label: "Overview", icon: Layout },
        { id: "markets", label: "Market Data", icon: Briefcase },
        { id: "trading", label: "Paper Trading", icon: Activity },
        { id: "portfolio", label: "My Portfolio", icon: Landmark },
        { id: "research", label: "Research Reader", icon: BookOpen },
      ]
    },
    {
      name: "Operations",
      icon: Activity,
      items: [
        { id: "diagnostics", label: "Health Checks", icon: Activity },
      ]
    }
  ];

  const bottomGroups = [
    {
      name: "System",
      icon: Settings,
      items: [
        { id: "account", label: "Account Settings", icon: Settings },
      ]
    },
    {
      name: "Support_Center",
      icon: HelpCircle,
      items: [
        { id: "support", label: "Knowledge Base", icon: FileText },
        { id: "onboarding", label: "FAQ / Q&A", icon: MessageCircle },
        { id: "legal", label: "Protocol & Risk", icon: Gavel },
      ]
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onToggle}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm lg:hidden z-[60]"
          />
        )}
      </AnimatePresence>

      <motion.aside 
        className={`fixed lg:relative top-0 left-0 bottom-0 w-72 lg:w-80 bg-black/80 border-r border-white/5 flex flex-col z-[70] transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Sidebar Header */}
        <div className="p-8 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-4">
             <VeyraLogo size="sm" />
             <div>
                <h1 className="font-bold tracking-tight text-white uppercase italic">Veyra_Foundation</h1>
                <p className="text-[10px] text-slate-500 font-mono font-bold tracking-widest uppercase italic">Local.Core.0.1</p>
             </div>
          </div>
          <button onClick={onToggle} className="lg:hidden p-2 text-slate-500 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Navigation Area */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar flex flex-col">
          <div className="flex-1 space-y-6">
            {menuGroups.map((group) => (
              <SidebarGroup 
                key={group.name} 
                group={group} 
                expandedGroups={expandedGroups} 
                toggleGroup={toggleGroup} 
                currentView={currentView} 
                onViewChange={onViewChange} 
                onToggle={onToggle} 
              />
            ))}
          </div>

          <div className="pt-6 mt-6 border-t border-white/5 space-y-4">
             <p className="px-4 text-[8px] font-black text-slate-700 uppercase tracking-[0.3em]">System_Integrity</p>
             {bottomGroups.map((group) => (
               <SidebarGroup 
                 key={group.name} 
                 group={group} 
                 expandedGroups={expandedGroups} 
                 toggleGroup={toggleGroup} 
                 currentView={currentView} 
                 onViewChange={onViewChange} 
                 onToggle={onToggle} 
               />
             ))}
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-6 border-t border-white/5 bg-white/[0.02]">
           <button 
             onClick={() => onViewChange('account')}
             className="w-full flex items-center gap-3 p-4 bg-black/40 border border-white/5 rounded-2xl mb-4 group cursor-pointer hover:border-indigo-500/30 transition-all text-left"
           >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold italic text-white ring-2 ring-white/5 group-hover:ring-indigo-500/50 overflow-hidden shrink-0">
                 {user?.avatar ? (
                   <img src={user.avatar} alt="Avatar" className="w-full h-full object-cover" />
                 ) : (
                   user?.name.split(' ').map(n => n[0]).join('') || 'J'
                 )}
              </div>
              <div className="flex-1 min-w-0">
                 <p className="text-xs font-bold text-white truncate uppercase tracking-tight">{user?.name || 'Jay Prophit'}</p>
                 <p className="text-[10px] text-slate-500 font-mono truncate">{user?.username || '@prophit_alpha'}</p>
              </div>
              <ChevronDown size={14} className="text-slate-600" />
           </button>

           <div className="flex justify-between items-center px-4">
              <button className="text-slate-500 hover:text-white transition-colors relative">
                <Bell size={18} />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full border border-black animate-pulse"></span>
              </button>
              <button className="text-slate-500 hover:text-white transition-colors">
                <Search size={18} />
              </button>
              <button className="text-slate-500 hover:text-white transition-colors">
                <HelpCircle size={18} />
              </button>
           </div>
        </div>
      </motion.aside>
    </>
  );
}
