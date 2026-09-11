import React, { useState } from 'react';
import { History, Filter, ArrowRight } from 'lucide-react';
import { AnalysisResponse } from '../../types';
import { SupportedLanguage, t } from '../../i18n/translations';

interface FarmerHistoryProps {
  analyses: AnalysisResponse[];
  onSelectAnalysis: (analysis: AnalysisResponse) => void;
  language?: SupportedLanguage;
}

export const FarmerHistory: React.FC<FarmerHistoryProps> = ({
  analyses,
  onSelectAnalysis,
  language = 'en'
}) => {
  const [selectedCrop, setSelectedCrop] = useState<string>('all');
  const [selectedRisk, setSelectedRisk] = useState<string>('all');

  const filtered = analyses.filter((item) => {
    if (selectedCrop !== 'all' && item.crop.toLowerCase() !== selectedCrop.toLowerCase()) return false;
    if (
      selectedRisk !== 'all' &&
      item.advisory?.overall_risk?.toLowerCase() !== selectedRisk.toLowerCase()
    ) {
      return false;
    }
    return true;
  });

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      <div className="glass-card rounded-2xl p-6 border border-emerald-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <History className="w-4 h-4" />
            </span>
            <h2 className="text-xl font-bold text-white font-['Outfit']">
              {t(language, 'history_title')}
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Chronological log of your AI vision scans and field reports.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-700 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-slate-900">All Crops</option>
              <option value="tomato" className="bg-slate-900">Tomato</option>
              <option value="rice" className="bg-slate-900">Rice</option>
              <option value="cotton" className="bg-slate-900">Cotton</option>
              <option value="wheat" className="bg-slate-900">Wheat</option>
              <option value="potato" className="bg-slate-900">Potato</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-700 text-xs">
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-slate-900">All Risk Levels</option>
              <option value="healthy" className="bg-slate-900">Healthy</option>
              <option value="low risk" className="bg-slate-900">Low Risk</option>
              <option value="moderate risk" className="bg-slate-900">Moderate Risk</option>
              <option value="high risk" className="bg-slate-900">High Risk</option>
              <option value="critical" className="bg-slate-900">Critical</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 glass-card rounded-2xl border border-slate-800 space-y-2">
            <p className="text-sm text-slate-400">
              {analyses.length === 0
                ? 'No diagnostic records yet.'
                : 'No diagnostic records matching the selected filters.'}
            </p>
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectAnalysis(item)}
              className="glass-card rounded-2xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all cursor-pointer flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group hover:scale-[1.005]"
            >
              <div className="flex items-center gap-4">
                <img
                  src={item.image_url}
                  alt={item.crop}
                  className="w-16 h-16 rounded-xl object-cover border border-slate-800 group-hover:border-emerald-500/40 shrink-0"
                />

                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/30">
                      {item.crop}
                    </span>
                    <span className="text-xs text-slate-400">
                      • {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">({item.id})</span>
                  </div>

                  <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                    {item.disease?.disease ?? (item.status === 'model_unavailable' ? 'Model unavailable' : '—')}
                  </h4>

                  <p className="text-xs text-slate-400 line-clamp-1 max-w-lg">
                    {item.advisory?.condition_summary}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 self-end sm:self-center">
                <div className="text-right">
                  <span
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                      item.advisory?.overall_risk === 'Critical' ||
                      item.advisory?.overall_risk === 'High Risk'
                        ? 'bg-red-950/80 text-red-400 border-red-500/30'
                        : item.advisory?.overall_risk === 'Healthy'
                          ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/30'
                          : 'bg-amber-950/80 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    {item.advisory?.overall_risk || 'Unknown'}
                  </span>
                  {typeof item.advisory?.risk_score === 'number' && (
                    <span className="block text-[10px] text-slate-400 mt-1">
                      Score: {item.advisory.risk_score}/100
                    </span>
                  )}
                </div>

                <div className="p-2 rounded-xl bg-slate-900 text-slate-400 group-hover:text-emerald-400 group-hover:bg-emerald-500/10 transition-colors">
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
