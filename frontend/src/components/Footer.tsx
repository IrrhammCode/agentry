import React from 'react';
import { Shield } from 'lucide-react';

interface FooterProps {
  onViewChange: (view: 'showcase' | 'console' | 'defense' | 'docs') => void;
}

export const Footer: React.FC<FooterProps> = ({ onViewChange }) => {
  return (
    <footer className="mt-auto border-t border-white/10 bg-black px-4 lg:px-8 py-8">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-sentry-cyan" />
          <span className="text-slate-200 font-semibold">Agentry</span>
          <span>• Prior Labs TabPFN-3.5 Global Hackathon 2026</span>
        </div>

        <div className="flex items-center gap-6 flex-wrap">
          <a 
            href="https://github.com/IrrhammCode/agentry" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="hover:text-white transition-colors"
          >
            GitHub Repository
          </a>
          <button 
            onClick={() => onViewChange('showcase')} 
            className="hover:text-white transition-colors"
          >
            Simulator
          </button>
          <button 
            onClick={() => onViewChange('console')} 
            className="hover:text-white transition-colors"
          >
            Mission Control
          </button>
          <button 
            onClick={() => onViewChange('defense')} 
            className="hover:text-white transition-colors"
          >
            Active Defense
          </button>
          <button 
            onClick={() => onViewChange('docs')} 
            className="text-sentry-cyan hover:underline transition-colors font-bold"
          >
            Documentation
          </button>
          <span className="text-emerald-400">MIT Open Source</span>
        </div>
      </div>
    </footer>
  );
};
