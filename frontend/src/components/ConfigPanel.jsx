import { useState } from 'react';
import { runAudit } from '../services/api';
import clsx from 'clsx';
import { Activity, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function ConfigPanel({ dataset, onAuditComplete }) {
  const [config, setConfig] = useState({
    protected_col: '',
    target_col: '',
    priv_val: '',
    fav_outcome: '',
    qualification_cols: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const results = await runAudit(dataset.dataset_id, config);
      onAuditComplete({ ...results, config });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'Audit failed. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const isConfigComplete = config.protected_col && config.target_col && config.priv_val && config.fav_outcome;

  return (
    <div className="glass-panel p-6 mb-8">
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-8">
        <h4 className="font-bold text-sm text-slate-300 uppercase tracking-wide mb-3">Audit Pipeline</h4>
        <div className="flex flex-wrap gap-2 text-sm">
          <span className="bg-success/20 text-success border border-success/30 px-3 py-1 rounded-full">✓ Step 1: Upload dataset</span>
          <span className="bg-primary/20 text-primary border border-primary/30 px-3 py-1 rounded-full">Step 2: Select sensitive attribute & outcome</span>
          <span className="bg-slate-800 text-slate-400 border border-slate-700 px-3 py-1 rounded-full">Step 3: Run statistical bias audit</span>
          <span className="bg-slate-800 text-slate-400 border border-slate-700 px-3 py-1 rounded-full">Step 4: Analyze root causes</span>
        </div>
      </div>

      <div className="flex items-center space-x-2 mb-6">
        <Activity className="w-5 h-5 text-secondary" />
        <h3 className="text-xl font-bold">Audit Configuration</h3>
      </div>
      
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Protected Attribute (e.g. Race, Gender)</label>
            <select 
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              value={config.protected_col}
              onChange={(e) => setConfig({...config, protected_col: e.target.value})}
            >
              <option value="">Select Column...</option>
              {dataset.columns.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Privileged Value</label>
            <input 
              type="text"
              placeholder="e.g. White, Male"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-primary outline-none"
              value={config.priv_val}
              onChange={(e) => setConfig({...config, priv_val: e.target.value})}
            />
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Target Outcome Variable</label>
            <select 
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              value={config.target_col}
              onChange={(e) => setConfig({...config, target_col: e.target.value})}
            >
              <option value="">Select Column...</option>
              {dataset.columns.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Favorable Outcome Value</label>
            <input 
              type="text"
              placeholder="e.g. 1, Yes, Approved"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-primary outline-none"
              value={config.fav_outcome}
              onChange={(e) => setConfig({...config, fav_outcome: e.target.value})}
            />
          </div>
        </div>
        
        <div className="md:col-span-2 space-y-4 mt-4">
          {error && (
            <div className="flex items-center space-x-2 text-danger bg-danger/10 p-3 rounded-lg">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          <div className="flex justify-end">
            <button 
              type="submit" 
              disabled={!isConfigComplete || loading}
              className="bg-secondary hover:bg-secondary/90 disabled:opacity-50 text-white font-medium py-2.5 px-6 rounded-lg transition-colors shadow-lg shadow-secondary/20 flex items-center space-x-2"
            >
              {loading ? <span>Analyzing...</span> : <span>Run Full Audit</span>}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
