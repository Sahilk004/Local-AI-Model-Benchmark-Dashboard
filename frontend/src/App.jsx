import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Terminal, Settings2, Zap } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import PromptTester from './pages/PromptTester';
import Recommendation from './pages/Recommendation';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100">
      {/* Sidebar */}
      <div className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
          <Zap className="h-6 w-6 text-primary-500 mr-2" />
          <h1 className="text-lg font-bold">BenchAI</h1>
        </div>
        
        <nav className="flex-1 py-4 px-3 space-y-1">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'dashboard' ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400' : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'}`}
          >
            <LayoutDashboard className="mr-3 h-5 w-5" />
            Dashboard
          </button>
          
          <button 
            onClick={() => setActiveTab('tester')}
            className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'tester' ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400' : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'}`}
          >
            <Terminal className="mr-3 h-5 w-5" />
            Prompt Tester
          </button>
          
          <button 
            onClick={() => setActiveTab('recommendation')}
            className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'recommendation' ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400' : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'}`}
          >
            <Settings2 className="mr-3 h-5 w-5" />
            Recommendations
          </button>
        </nav>
        
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 w-full text-left"
          >
            Toggle {darkMode ? 'Light' : 'Dark'} Mode
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'tester' && <PromptTester />}
        {activeTab === 'recommendation' && <Recommendation />}
      </main>
    </div>
  );
}

export default App;
