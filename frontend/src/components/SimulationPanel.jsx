import { useState } from 'react';
import { Play } from 'lucide-react';
import { simulateScenario } from '../services/api';

export default function SimulationPanel({ datasetId, config, onSimulationComplete }) {
  const [featureToDrop, setFeatureToDrop] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    if (!featureToDrop) return;
    setLoading(true);
    try {
      const result = await simulateScenario(datasetId, config, featureToDrop);
      onSimulationComplete(result);
    } catch (err) {
      console.error(err);
      alert("Simulation failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 mt-8 border-l-4 border-l-secondary">
      <h3 className="text-xl font-bold mb-4">What-If Simulation Engine</h3>
      <p className="text-sm text-slate-400 mb-6">Test hypothetical interventions to see their impact on fairness metrics without altering raw data.</p>
      
      <div className="flex flex-col md:flex-row items-end space-y-4 md:space-y-0 md:space-x-4">
        <div className="flex-grow w-full">
          <label className="block text-sm font-medium text-slate-400 mb-1">Simulate Dropping a Feature</label>
          <input 
            type="text"
            placeholder="e.g. Zipcode, CreditScore"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-secondary outline-none"
            value={featureToDrop}
            onChange={(e) => setFeatureToDrop(e.target.value)}
          />
        </div>
        
        <button 
          onClick={handleSimulate}
          disabled={!featureToDrop || loading}
          className="w-full md:w-auto bg-secondary hover:bg-secondary/90 disabled:opacity-50 text-white font-medium py-2.5 px-6 rounded-lg transition-colors shadow-lg shadow-secondary/20 flex items-center justify-center space-x-2"
        >
          {loading ? <span>Simulating...</span> : <><Play className="w-4 h-4" /> <span>Run Simulation</span></>}
        </button>
      </div>
    </div>
  );
}
