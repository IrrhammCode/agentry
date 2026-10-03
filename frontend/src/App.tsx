import React, { useState } from 'react';
import { Navbar } from './components/Navbar.tsx';
import { Footer } from './components/Footer.tsx';
import { LandingPage } from './views/LandingPage.tsx';
import { MissionControl } from './views/MissionControl.tsx';
import { ActiveDefense } from './views/ActiveDefense.tsx';
import { Documentation } from './views/Documentation.tsx';
import { McpUsageMonitor } from './views/McpUsageMonitor.tsx';

export function App() {
  const [currentView, setCurrentView] = useState<'showcase' | 'console' | 'defense' | 'docs' | 'mcp'>('showcase');

  const handleViewChange = (view: 'showcase' | 'console' | 'defense' | 'docs' | 'mcp') => {
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col font-sans antialiased text-slate-100 bg-black">
      {/* Global Navbar */}
      <Navbar currentView={currentView} onViewChange={handleViewChange} />

      {/* Main View Port */}
      <main className="flex-grow flex flex-col bg-black">
        {currentView === 'showcase' && (
          <LandingPage onLaunchConsole={() => handleViewChange('console')} />
        )}
        {currentView === 'console' && (
          <MissionControl />
        )}
        {currentView === 'defense' && (
          <ActiveDefense />
        )}
        {currentView === 'docs' && (
          <Documentation />
        )}
        {currentView === 'mcp' && (
          <McpUsageMonitor />
        )}
      </main>

      {/* Global Footer */}
      <Footer onViewChange={handleViewChange} />
    </div>
  );
}

export default App;

