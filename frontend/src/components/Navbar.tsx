import React from 'react';
import { 
  ShieldCheck, 
  Activity, 
  ShieldAlert, 
  Wallet, 
  Terminal, 
  ArrowLeft,
  BookOpen,
  Cable
} from 'lucide-react';

import { AgentryApi } from '../services/api.ts';

interface NavbarProps {
  currentView: 'showcase' | 'console' | 'defense' | 'docs' | 'mcp';
  onViewChange: (view: 'showcase' | 'console' | 'defense' | 'docs' | 'mcp') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onViewChange }) => {
  const isConsoleMode = currentView === 'console' || currentView === 'defense' || currentView === 'docs' || currentView === 'mcp';
  const [cloudMode, setCloudMode] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    AgentryApi.getHealth()
      .then((data) => setCloudMode(Boolean(data.tabpfn_cloud_mode)))
      .catch(() => setCloudMode(false));
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full bg-black/95 backdrop-blur-md border-b border-white/10 px-4 lg:px-8 py-3 transition-all duration-300">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-6">
          <button 
            onClick={() => onViewChange('showcase')}
            className="flex items-center gap-2.5 group text-left"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sentry-cyan via-emerald-500 to-sentry-emerald p-0.5 glow-cyan transition-transform group-hover:scale-105">
              <div className="w-full h-full bg-void rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-sentry-cyan" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-display font-bold text-xl tracking-tight text-white">Agentry</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-semibold border border-emerald-500/30">
                  {currentView === 'docs' ? 'DOCS' : currentView === 'mcp' ? 'MCP' : isConsoleMode ? 'WAR ROOM' : 'v0.1.0'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono hidden sm:block">
                {currentView === 'docs' ? 'Developer Hub & API Reference' : currentView === 'mcp' ? 'MCP Integration Monitor' : isConsoleMode ? 'Live Fleet Command Center' : 'TabPFN-3.5 Autonomous Sentry'}
              </p>
            </div>
          </button>

          {/* LANDING PAGE NAVIGATION (Only visible on showcase mode) */}
          {!isConsoleMode && (
            <nav className="hidden md:flex items-center gap-1 text-xs font-medium text-slate-300">
              <a 
                href="#playground" 
                className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors"
              >
                Simulator
              </a>
              <a 
                href="#traps" 
                className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors"
              >
                Fatal Traps
              </a>
              <a 
                href="#architecture" 
                className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors"
              >
                Architecture
              </a>
              <a 
                href="#benchmarks" 
                className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors"
              >
                Benchmarks
              </a>
              <a 
                href="#calculator" 
                className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors"
              >
                ROI Calc
              </a>
              <button 
                onClick={() => onViewChange('docs')}
                className="px-3 py-1.5 rounded-lg text-sentry-cyan hover:bg-white/5 font-semibold transition-colors flex items-center gap-1"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Docs</span>
              </button>
            </nav>
          )}

          {/* CONSOLE VIEW SWITCHER (Only visible when user has launched console or docs) */}
          {isConsoleMode && (
            <nav className="flex items-center p-1 bg-surface-1/80 rounded-xl border border-white/10 animate-fade-in overflow-x-auto">
              <button 
                onClick={() => onViewChange('console')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  currentView === 'console'
                    ? 'text-white bg-surface-2 border border-white/10 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Activity className="w-3.5 h-3.5 text-sentry-emerald" />
                <span>Mission Control</span>
                <span className="w-2 h-2 rounded-full bg-sentry-emerald animate-pulse"></span>
              </button>

              <button 
                onClick={() => onViewChange('defense')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  currentView === 'defense'
                    ? 'text-white bg-surface-2 border border-white/10 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5 text-sentry-red" />
                <span>Active Defense</span>
              </button>

              <button 
                onClick={() => onViewChange('docs')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  currentView === 'docs'
                    ? 'text-white bg-surface-2 border border-white/10 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5 text-sentry-cyan" />
                <span>Docs & Ideas</span>
              </button>

              <button 
                onClick={() => onViewChange('mcp')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  currentView === 'mcp'
                    ? 'text-white bg-surface-2 border border-white/10 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Cable className="w-3.5 h-3.5 text-sentry-violet" />
                <span>MCP Monitor</span>
              </button>
            </nav>
          )}
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center gap-3">
          
          {/* GitHub Repo Link (Always visible on desktop) */}
          <a 
            href="https://github.com/IrrhammCode/agentry" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-surface-3 border border-white/10 text-xs font-medium text-slate-200 transition-colors"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span>Star</span>
            <span className="px-1.5 py-0.2 rounded bg-black/40 text-[10px] text-sentry-cyan font-mono border border-cyan-500/20">
              88 Pass
            </span>
          </a>

          {/* Cloud Mode vs Fallback Badge */}
          {cloudMode !== null && (
            <div 
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-medium border transition-colors ${
                cloudMode 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}
              title={cloudMode ? "Prior Labs TabPFN Cloud API Active" : "Scikit-Learn Fallback Engine Active (Not TabPFN)"}
            >
              <span className={`w-2 h-2 rounded-full ${cloudMode ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="hidden sm:inline">{cloudMode ? 'TabPFN cloud' : 'scikit-learn fallback (not TabPFN)'}</span>
              <span className="sm:hidden">{cloudMode ? 'TabPFN' : 'fallback'}</span>
            </div>
          )}

          {/* Primary View Switcher Button */}
          {!isConsoleMode ? (
            <button 
              onClick={() => onViewChange('console')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-sentry-cyan to-sentry-emerald text-void font-bold text-xs glow-cyan hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              <Terminal className="w-4 h-4" />
              <span>Launch Console</span>
            </button>
          ) : (
            <button 
              onClick={() => onViewChange('showcase')}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-surface-2 hover:bg-surface-3 border border-white/10 text-xs font-semibold text-slate-200 hover:text-white transition-all"
            >
              <ArrowLeft className="w-3.5 h-3.5 text-sentry-cyan" />
              <span>Exit Console</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
};
