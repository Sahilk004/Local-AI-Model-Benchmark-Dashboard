import React, { useState } from 'react';
import { Settings2, Cpu, Zap, Sparkles } from 'lucide-react';
import api from '../api';

function Recommendation() {
  const [ram, setRam] = useState(8);
  const [preference, setPreference] = useState('balanced');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRecommend = async () => {
    setLoading(true);
    try {
      const res = await api.post('/recommend', {
        ram_available_gb: parseFloat(ram),
        preference: preference
      });
      setRecommendation(res.data);
    } catch (error) {
      console.error(error);
      alert("Error getting recommendation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Model Recommendation Engine</h2>
      
      <div className="bg-white dark:bg-slate-900 p-8 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm mb-8">
        <h3 className="text-lg font-semibold mb-6 flex items-center">
          <Settings2 className="mr-2 text-primary-500" /> Configure Constraints
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label className="block text-sm font-medium mb-4 flex items-center">
              <Cpu className="mr-2 h-4 w-4" /> Available RAM (GB)
            </label>
            <input 
              type="range" 
              min="4" 
              max="64" 
              step="4"
              value={ram}
              onChange={(e) => setRam(e.target.value)}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer dark:bg-slate-700"
            />
            <div className="mt-4 text-center font-bold text-2xl text-primary-600">{ram} GB</div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-4 flex items-center">
              <Sparkles className="mr-2 h-4 w-4" /> Optimization Preference
            </label>
            <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
              {['speed', 'balanced', 'quality'].map(pref => (
                <button
                  key={pref}
                  onClick={() => setPreference(pref)}
                  className={`flex-1 py-2 text-sm font-medium rounded-md capitalize transition-all ${preference === pref ? 'bg-white dark:bg-slate-700 shadow-sm text-primary-600 dark:text-primary-400' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
                >
                  {pref}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <div className="mt-8 flex justify-end">
          <button 
            onClick={handleRecommend}
            disabled={loading}
            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Get Recommendation'}
          </button>
        </div>
      </div>
      
      {recommendation && (
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-8 text-white shadow-lg animate-in fade-in slide-in-from-bottom-4">
          <h3 className="text-xl font-bold mb-2 flex items-center">
            <Zap className="mr-2 text-yellow-300" /> Recommended For You
          </h3>
          
          <div className="mt-6 bg-white/10 rounded-lg p-6 backdrop-blur-sm border border-white/20">
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-indigo-200 text-sm mb-1">Model</p>
                <p className="text-3xl font-bold">{recommendation.recommended_model}</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm mb-1">Quantization</p>
                <p className="text-3xl font-bold uppercase">{recommendation.recommended_quantization}</p>
              </div>
            </div>
            
            <div className="border-t border-white/20 pt-4">
              <p className="text-sm text-indigo-100 leading-relaxed">
                {recommendation.explanation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Recommendation;
