import { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle } from 'lucide-react';
import { uploadDataset } from '../services/api';
import clsx from 'clsx';

export default function Upload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const data = await uploadDataset(file);
      onUploadSuccess(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-8 max-w-2xl mx-auto mt-12 text-center">
      <div className="flex justify-center mb-6">
        <div className="p-4 bg-primary/20 rounded-full">
          <UploadCloud className="w-12 h-12 text-primary" />
        </div>
      </div>
      <h1 className="text-3xl font-bold mb-4">Audit AI Decisions for Hidden Discrimination</h1>
      <p className="text-slate-400 mb-8 max-w-lg mx-auto leading-relaxed">
        AI systems often make decisions that look fair overall but discriminate against specific groups. FairLens audits these decisions using statistical tests to detect hidden bias, proxy variables, and legal risk.
      </p>
      
      <form onSubmit={handleUpload} className="space-y-6">
        <div className="relative group cursor-pointer">
          <input 
            type="file" 
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className={clsx(
            "border-2 border-dashed rounded-xl p-8 transition-colors",
            file ? "border-primary bg-primary/5" : "border-slate-600 hover:border-primary/50 group-hover:bg-slate-800/50"
          )}>
            {file ? (
              <div className="flex items-center justify-center space-x-2 text-primary">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">{file.name}</span>
              </div>
            ) : (
              <span className="text-slate-400">Click or drag and drop to select a file</span>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-center space-x-2 text-danger bg-danger/10 p-3 rounded-lg text-left">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <button 
          type="submit" 
          disabled={!file || loading}
          className="w-full bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-lg transition-colors shadow-lg shadow-primary/20"
        >
          {loading ? 'Uploading & Profiling...' : 'Analyze Dataset'}
        </button>
      </form>

      <div className="mt-12 text-left bg-slate-800/30 p-6 rounded-xl border border-slate-700/50">
        <h3 className="text-lg font-bold mb-4 flex items-center"><span className="text-secondary mr-2">💼</span> Real-world Applications</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-800/80 rounded-lg text-sm text-slate-300 font-medium border border-slate-700/50">Hiring bias detection</div>
          <div className="p-4 bg-slate-800/80 rounded-lg text-sm text-slate-300 font-medium border border-slate-700/50">Loan approval fairness</div>
          <div className="p-4 bg-slate-800/80 rounded-lg text-sm text-slate-300 font-medium border border-slate-700/50">College admissions transparency</div>
        </div>
      </div>
    </div>
  );
}
