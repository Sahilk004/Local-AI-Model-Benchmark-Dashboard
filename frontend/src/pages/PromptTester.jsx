import React, { useState } from 'react';
import { Send, Cpu, Zap, Clock } from 'lucide-react';
import api from '../api';

function PromptTester() {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState(['llama3']);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const availableModels = ['llama3', 'mistral', 'phi3'];

  const toggleModel = (model) => {
    if (selectedModels.includes(model)) {
      setSelectedModels(selectedModels.filter(m => m !== model));
    } else {
      setSelectedModels([...selectedModels, model]);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim() || selectedModels.length === 0) return;

    setLoading(true);
    setResults([]);

    try {
      const res = await api.post('/generate', {
        prompt: prompt,
        models: selectedModels,
        quantization: "default"
      });

      setResults(res.data);

      // ✅ SAVE DATA TO BACKEND (IMPORTANT FIX)
      await Promise.all(
        res.data.map(r =>
          api.post('/history', {
            model_name: r.model_name,
            quantization: "default",
            tokens_per_sec: r.tokens_per_sec,
            latency_ms: r.latency_ms,
            ram_usage_mb: r.ram_usage_mb
          })
        )
      );

    } catch (error) {
      console.error("Generation error:", error);
      alert("Error generating response. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 h-full flex flex-col">
      <h2 className="text-2xl font-bold mb-6">Prompt Tester</h2>

      {/* Input Section */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Select Models to Compare</label>
          <div className="flex flex-wrap gap-2">
            {availableModels.map(model => (
              <button
                key={model}
                onClick={() => toggleModel(model)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  selectedModels.includes(model)
                    ? 'bg-primary-500 text-white'
                    : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                {model}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Prompt</label>
          <div className="relative">
            <textarea
              className="w-full h-32 p-4 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none resize-none"
              placeholder="Enter your prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim() || selectedModels.length === 0}
              className="absolute bottom-4 right-4 bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center h-64 text-slate-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
            Running parallel inference...
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {results.map((res, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col"
              >
                <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex justify-between items-center">
                  <h3 className="font-semibold text-lg">{res.model_name}</h3>
                  {res.cached && (
                    <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded-full">
                      Cached
                    </span>
                  )}
                </div>

                <div className="p-6 flex-1 overflow-y-auto whitespace-pre-wrap font-mono text-sm">
                  {res.response || "No response generated."}
                </div>

                <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" /> {Math.round(res.latency_ms)}ms
                  </div>
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 mr-1" /> {res.tokens_per_sec.toFixed(1)} t/s
                  </div>
                  <div className="flex items-center">
                    <Cpu className="h-4 w-4 mr-1" /> +{Math.round(res.ram_usage_mb)} MB
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default PromptTester;