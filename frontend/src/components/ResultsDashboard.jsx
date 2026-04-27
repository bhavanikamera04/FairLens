import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { AlertCircle, ShieldAlert, CheckCircle, Search, TrendingDown } from 'lucide-react';
import clsx from 'clsx';

export default function ResultsDashboard({ results }) {
  if (!results) return null;

  const di = results.disparate_impact?.disparate_impact || 0;
  const isSignificant = results.disparate_impact?.significant;
  const isFair = di >= 0.8 && di <= 1.25;

  const rcaData = results.root_cause_analysis?.feature_shap_diff ? 
    Object.entries(results.root_cause_analysis.feature_shap_diff).slice(0, 5).map(([name, val]) => ({ name, value: val })) 
    : [];

  return (
    <div className="space-y-6">
      {/* Reliability Panel */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={clsx(
          "glass-panel p-4 border-l-4",
          results.dataset_info?.confidence === 'HIGH' ? "border-l-success" : 
          results.dataset_info?.confidence === 'CRITICAL_LOW' ? "border-l-danger" : "border-l-warning"
        )}>
          <h5 className="text-xs text-slate-400 uppercase font-bold mb-1">Audit Confidence</h5>
          <div className="text-xl font-bold text-white">{results.dataset_info?.confidence || 'UNKNOWN'}</div>
          <div className="text-[10px] text-slate-500 mt-1">{results.dataset_info?.confidence_reason}</div>
        </div>
        <div className={clsx(
          "glass-panel p-4 border-l-4",
          results.di_stability?.confidence === 'STABLE' ? "border-l-success" : 
          results.di_stability?.confidence === 'MODERATE' ? "border-l-warning" : "border-l-danger"
        )}>
          <h5 className="text-xs text-slate-400 uppercase font-bold mb-1">Signal Stability</h5>
          <div className="text-xl font-bold text-white">{results.di_stability?.confidence || 'UNKNOWN'}</div>
          <div className="text-[10px] text-slate-500 mt-1">{results.di_stability?.label}</div>
        </div>
        <div className="glass-panel p-4">
          <h5 className="text-xs text-slate-400 uppercase font-bold mb-1">Data Size</h5>
          <div className="text-xl font-bold text-white">{results.dataset_info?.rows || 0} rows</div>
          <div className="text-[10px] text-slate-500 mt-1">Samples analyzed</div>
        </div>
        <div className={clsx(
           "rounded-lg p-3 flex items-center space-x-3 border",
           results.dataset_info?.decision_allowed ? "bg-slate-900/50 border-slate-700/50" : "bg-danger/20 border-danger/40"
        )}>
          <AlertCircle className={clsx("w-5 h-5 shrink-0", results.dataset_info?.decision_allowed ? "text-warning" : "text-danger")} />
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">
            {results.dataset_info?.decision_allowed ? "Decision Gating: ACTIVE" : "Decision Gating: LOCKED"}
          </p>
        </div>
      </div>

      {!results.dataset_info?.decision_allowed && (
         <div className="glass-panel p-12 text-center border-2 border-dashed border-danger/40 bg-danger/5">
            <ShieldAlert className="w-16 h-16 text-danger mx-auto mb-4 opacity-50" />
            <h3 className="text-2xl font-bold text-white mb-2">Audit Gated: Insufficient Data</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              FairLens requires at least 30 samples to generate reliable insights. 
              Showing results now would be statistically irresponsible.
            </p>
            <div className="mt-8">
               <span className="text-xs font-mono bg-slate-900 px-3 py-1 rounded border border-slate-700 text-slate-500">
                  ERR_DATASET_MIN_SIZE_NOT_MET
               </span>
            </div>
         </div>
      )}

      {results.dataset_info?.decision_allowed && (
        <>
          <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 text-sm text-primary-light flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p><strong>Decision Intelligence Mode:</strong> All findings are presented as hypotheses. Use the <strong>Simulation Engine</strong> to validate causal impacts before acting.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* KPI Card 1: Disparate Impact */}
            <div className="glass-panel p-6">
              <h4 className="text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">Disparate Impact</h4>
              <div className="flex items-end space-x-3">
                <span className={clsx("text-4xl font-bold", isFair ? "text-success" : "text-danger")}>
                  {di.toFixed(2)}
                </span>
                <span className="text-sm text-slate-400 mb-1">(Target: 0.8 - 1.25)</span>
              </div>
              <div className="mt-4 flex items-center space-x-2">
                {isFair ? <CheckCircle className="text-success w-5 h-5" /> : <ShieldAlert className="text-danger w-5 h-5" />}
                <span className="text-sm font-medium">{isFair ? "Passes EEOC 4/5 Rule" : "Fails EEOC 4/5 Rule"}</span>
              </div>
            </div>

            {/* KPI Card 2: Statistical Significance */}
            <div className="glass-panel p-6">
              <h4 className="text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">Stat. Significance</h4>
              <div className="flex items-end space-x-3">
                <span className="text-4xl font-bold text-white">
                  {results.disparate_impact?.p_value?.toExponential(2) || "N/A"}
                </span>
              </div>
              <div className="mt-4 flex flex-col space-y-1">
                <div className="flex items-center space-x-2">
                  {isSignificant ? <AlertCircle className="text-warning w-5 h-5" /> : <CheckCircle className="text-success w-5 h-5" />}
                  <span className="text-sm font-medium">{isSignificant ? "Significant difference" : "Not significant"}</span>
                </div>
                {results.disparate_impact?.p_value_note && (
                  <span className="text-[10px] text-danger font-bold uppercase tracking-tighter">⚠️ {results.disparate_impact.p_value_note}</span>
                )}
              </div>
            </div>

            {/* KPI Card 3: Proxy Bias */}
            <div className="glass-panel p-6">
              <h4 className="text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">Top Proxy Risk</h4>
              <div className="flex flex-col space-y-2">
                <span className="text-2xl font-bold text-secondary truncate">
                   {results.proxy_risks && results.proxy_risks.length > 0 ? results.proxy_risks[0].feature : "No High Risks"}
                </span>
                {results.proxy_risks && results.proxy_risks.length > 0 && (
                  <span className="text-[10px] bg-danger/20 text-danger px-2 py-0.5 rounded w-fit font-bold uppercase">
                    Detection: {results.proxy_risks[0].risk}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* RCA Chart */}
            <div className="glass-panel p-6">
               <h3 className="text-lg font-bold mb-6 flex items-center space-x-2">
                <TrendingDown className="text-primary w-5 h-5" />
                <span>Model Reliance Pattern</span>
              </h3>
              <p className="text-sm text-slate-400 mb-4 italic">
                Features contributing to the model's disparate prediction behavior.
              </p>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rcaData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" />
                    <Tooltip 
                       contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                       itemStyle={{ color: '#3b82f6' }}
                    />
                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]}>
                      {rcaData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#ef4444' : '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 p-2 bg-slate-900/50 rounded text-[10px] text-slate-400 border border-slate-700/50">
                <strong>SHAP Note:</strong> This reflects model behavior, not causal effect.
              </div>
            </div>

            {/* Recommendations */}
            <div className="glass-panel p-6">
              <h3 className="text-lg font-bold mb-6">Decision Hypotheses</h3>
              <ul className="space-y-4">
                {results.recommendations?.map((rec, idx) => (
                  <li key={idx} className="flex items-start space-x-3 bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
                    <div className="mt-0.5"><CheckCircle className="text-secondary w-5 h-5" /></div>
                    <span className="text-slate-200 text-sm leading-relaxed">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
