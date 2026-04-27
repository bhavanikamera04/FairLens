import { useState } from 'react';
import Upload from './components/Upload';
import ConfigPanel from './components/ConfigPanel';
import ResultsDashboard from './components/ResultsDashboard';
import SimulationPanel from './components/SimulationPanel';

function App() {
  const [dataset, setDataset] = useState(null);
  const [auditResults, setAuditResults] = useState(null);

  const handleUploadSuccess = (data) => {
    setDataset(data);
    setAuditResults(null);
  };

  const handleAuditComplete = (results) => {
    setAuditResults(results);
  };

  const handleSimulationComplete = (simResults) => {
    // Merge new DI into audit results for demo simplicity
    setAuditResults(prev => ({
      ...prev,
      disparate_impact: simResults.new_disparate_impact,
      recommendations: [
        `Simulation Result: Dropping feature changed DI to ${simResults.new_disparate_impact.disparate_impact.toFixed(2)}`,
        ...(prev.recommendations || [])
      ]
    }));
  };

  return (
    <div className="min-h-screen text-slate-100 p-4 md:p-8">
      <header className="max-w-6xl mx-auto mb-12 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
            FairLens
          </h1>
          <p className="text-slate-400 mt-1">Statistical Bias Audit System (No ML Predictions)</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto">
        {!dataset && (
          <Upload onUploadSuccess={handleUploadSuccess} />
        )}

        {dataset && !auditResults && (
          <div className="space-y-6">
            <div className="glass-panel p-6">
              <h2 className="text-xl font-bold mb-2">Dataset Loaded: {dataset.dataset_id}</h2>
              <p className="text-slate-400">Rows: {dataset.rows} | Columns: {dataset.columns.length}</p>
            </div>
            <ConfigPanel dataset={dataset} onAuditComplete={handleAuditComplete} />
          </div>
        )}

        {auditResults && (
          <div className="space-y-8 transition-all duration-700 opacity-100">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Audit Results</h2>
              <button 
                onClick={() => setAuditResults(null)}
                className="text-sm text-primary hover:underline"
              >
                Reconfigure Audit
              </button>
            </div>
            
            <ResultsDashboard results={auditResults} />
            <SimulationPanel 
              datasetId={dataset.dataset_id} 
              config={auditResults.config} 
              onSimulationComplete={handleSimulationComplete} 
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
