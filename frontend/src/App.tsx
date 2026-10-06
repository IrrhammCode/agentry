import React, { useState } from 'react';
import { Navbar } from './components/Navbar.tsx';
import { Footer } from './components/Footer.tsx';
import { LandingPage } from './views/LandingPage.tsx';
import { MissionControl } from './views/MissionControl.tsx';
import { ActiveDefense } from './views/ActiveDefense.tsx';
import { Documentation } from './views/Documentation.tsx';
import { McpUsageMonitor } from './views/McpUsageMonitor.tsx';
import { PresentationDeck } from './views/PresentationDeck.tsx';

export function App() {
  const getInitialView = (): 'showcase' | 'console' | 'defense' | 'docs' | 'mcp' | 'presentation' => {
    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (['showcase', 'console', 'defense', 'docs', 'mcp', 'presentation'].includes(hash)) {
      return hash as any;
    }
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view')?.toLowerCase();
    if (viewParam && ['showcase', 'console', 'defense', 'docs', 'mcp', 'presentation'].includes(viewParam)) {
      return viewParam as any;
    }
    return 'showcase';
  };

  const [currentView, setCurrentView] = useState<'showcase' | 'console' | 'defense' | 'docs' | 'mcp' | 'presentation'>(getInitialView);

  const handleViewChange = (view: 'showcase' | 'console' | 'defense' | 'docs' | 'mcp' | 'presentation') => {
    setCurrentView(view);
    window.location.hash = view;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col font-sans antialiased text-slate-100 bg-black">
      {/* Global Navbar */}
      <Navbar currentView={currentView} onViewChange={handleViewChange} />

      {/* Main View Port */}
      <main className="flex-grow flex flex-col bg-black">
        {currentView === 'showcase' && (
          <LandingPage 
            onLaunchConsole={() => handleViewChange('console')} 
            onLaunchPresentation={() => handleViewChange('presentation')}
          />
        )}
        {currentView === 'presentation' && (
          <PresentationDeck 
            onLaunchConsole={() => handleViewChange('console')}
            onExitDeck={() => handleViewChange('showcase')}
          />
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

