import React from 'react';
import {
  ArrowRight, CloudRain, Droplets, Thermometer,
  Wind, Sparkles, MapPin
} from 'lucide-react';
import { AnalysisResponse, WeatherMetrics, User } from '../../types';
import { SupportedLanguage, t } from '../../i18n/translations';
import { handleImageError } from '../../lib/imageFallback';

interface FarmerDashboardProps {
  user: User | null;
  analyses: AnalysisResponse[];
  weather: WeatherMetrics | null;
  language: SupportedLanguage;
  onNavigateToAnalyze: () => void;
  onSelectAnalysis: (analysis: AnalysisResponse) => void;
  locationName: string;
}

export const FarmerDashboard: React.FC<FarmerDashboardProps> = ({
  user,
  analyses,
  weather,
  language,
  onNavigateToAnalyze,
  onSelectAnalysis,
  locationName
}) => {
  const totalAnalyses = analyses.length;
  const healthyCrops = analyses.filter((a) => a.advisory?.overall_risk === 'Healthy').length;
  const diseaseCases = analyses.filter((a) => a.disease?.pathogen_type !== 'Healthy').length;
  const pestCases = analyses.filter((a) => a.pests?.length > 0).length;
  const highRiskCases = analyses.filter(
    (a) =>
      a.advisory?.overall_risk === 'High Risk' || a.advisory?.overall_risk === 'Critical'
  ).length;

  const farmVigorScore =
    totalAnalyses > 0
      ? Math.round(((totalAnalyses - highRiskCases) / totalAnalyses) * 100)
      : null;

  const weatherUnavailable = !weather || weather.is_unavailable;
  const displayName = user?.full_name?.trim() || 'Farmer';

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="glass-card rounded-3xl p-6 lg:p-8 relative overflow-hidden border border-emerald-500/20 shadow-2xl">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-emerald-500/10 via-transparent to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/20 inline-flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> {t(language, 'farmer_portal')}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <MapPin className="w-3 h-3 text-emerald-400" /> {locationName}
              </span>
            </div>

            <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight font-['Outfit']">
              Good day, {displayName}
            </h1>

            <p className="text-sm text-slate-300 max-w-xl leading-relaxed">
              Review your diagnostic history and run a new crop scan when you need verified field guidance.
            </p>
          </div>

          <button
            onClick={onNavigateToAnalyze}
            className="group px-8 py-5 rounded-2xl bg-gradient-to-r from-emerald-400 to-emerald-500 hover:from-emerald-300 hover:to-emerald-400 text-slate-950 font-extrabold text-base shadow-xl shadow-emerald-500/30 transition-all hover:scale-105 flex items-center gap-3 shrink-0"
          >
            <span className="w-3 h-3 rounded-full bg-slate-950 animate-ping" />
            <span>{t(language, 'analyze_crop_btn')}</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-8 pt-6 border-t border-slate-800/80">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[11px] text-slate-400 font-medium">Total Scans</span>
            <p className="text-2xl font-bold text-white font-['Outfit'] mt-1">{totalAnalyses}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[11px] text-slate-400 font-medium">Healthy</span>
            <p className="text-2xl font-bold text-emerald-400 font-['Outfit'] mt-1">{healthyCrops}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[11px] text-slate-400 font-medium">Disease Cases</span>
            <p className="text-2xl font-bold text-amber-400 font-['Outfit'] mt-1">{diseaseCases}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[11px] text-slate-400 font-medium">Pest Cases</span>
            <p className="text-2xl font-bold text-sky-400 font-['Outfit'] mt-1">{pestCases}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[11px] text-slate-400 font-medium">High Risk</span>
            <p className="text-2xl font-bold text-red-400 font-['Outfit'] mt-1">{highRiskCases}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 glass-card rounded-2xl p-6 border border-emerald-500/20 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white font-['Outfit']">Scan Health Summary</h3>
              {farmVigorScore !== null ? (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">
                  From your scans
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">
                  Unavailable
                </span>
              )}
            </div>

            {farmVigorScore === null ? (
              <div className="py-10 text-center space-y-2">
                <p className="text-sm text-slate-300 font-medium">No scans yet</p>
                <p className="text-xs text-slate-500">
                  A health summary will appear after you complete at least one diagnostic scan.
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center my-6">
                <div className="relative w-36 h-36 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-slate-800"
                      strokeWidth="3.2"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-emerald-400"
                      strokeDasharray={`${farmVigorScore}, 100`}
                      strokeWidth="3.2"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-black text-white font-['Outfit']">{farmVigorScore}%</span>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Non-critical</span>
                  </div>
                </div>
                <p className="text-xs text-center text-slate-400 mt-2 max-w-xs">
                  Share of your scans that are not High Risk or Critical. Based only on your history.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-8 glass-card rounded-2xl p-6 border border-emerald-500/20 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
                <CloudRain className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-['Outfit']">
                  {t(language, 'weather_title')}
                </h3>
                <p className="text-xs text-slate-400">{locationName}</p>
              </div>
            </div>

            {!weatherUnavailable && (
              <div className="flex items-center gap-2">
                {weather.is_cached && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Cached
                  </span>
                )}
                <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold">
                  Risk: {weather.risk_level}
                </span>
              </div>
            )}
          </div>

          {weatherUnavailable ? (
            <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-1">
              <p className="text-sm text-slate-300 font-medium">Weather unavailable</p>
              <p className="text-xs text-slate-500">
                Live telemetry is not available right now. No placeholder values are shown.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span>Temperature</span>
                  <Thermometer className="w-4 h-4 text-orange-400" />
                </div>
                <p className="text-2xl font-extrabold text-white font-['Outfit'] mt-1">
                  {weather.temperature}°C
                </p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span>Humidity</span>
                  <Droplets className="w-4 h-4 text-sky-400" />
                </div>
                <p className="text-2xl font-extrabold text-white font-['Outfit'] mt-1">
                  {weather.relative_humidity}%
                </p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span>Precipitation</span>
                  <CloudRain className="w-4 h-4 text-emerald-400" />
                </div>
                <p className="text-2xl font-extrabold text-white font-['Outfit'] mt-1">
                  {weather.precipitation} mm
                </p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span>Wind</span>
                  <Wind className="w-4 h-4 text-teal-400" />
                </div>
                <p className="text-2xl font-extrabold text-white font-['Outfit'] mt-1">
                  {weather.wind_speed} km/h
                </p>
              </div>
            </div>
          )}

          {!weatherUnavailable && weather.risk_factor && (
            <p className="text-xs text-slate-300 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              {weather.risk_factor}
            </p>
          )}
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white font-['Outfit']">Recent Diagnoses</h3>
            <span className="text-xs text-slate-400">({analyses.length})</span>
          </div>
          <button
            onClick={onNavigateToAnalyze}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
          >
            New Scan <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {analyses.length === 0 ? (
          <div className="py-10 text-center rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <p className="text-sm text-slate-300">No diagnostic history yet</p>
            <p className="text-xs text-slate-500">Run your first crop scan to see reports here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analyses.slice(0, 3).map((an) => (
              <div
                key={an.id}
                onClick={() => onSelectAnalysis(an)}
                className="group cursor-pointer rounded-2xl p-4 bg-slate-950/70 border border-slate-800 hover:border-emerald-500/40 transition-all hover:scale-[1.01] flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="relative rounded-xl overflow-hidden aspect-video">
                    <img
                      src={an.image_url}
                      alt={an.crop}
                      onError={handleImageError}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-slate-950/80 text-[10px] font-bold text-white">
                      {an.crop}
                    </div>
                    <div
                      className={`absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-bold ${
                        an.advisory?.overall_risk === 'Critical' ||
                        an.advisory?.overall_risk === 'High Risk'
                          ? 'bg-red-950/90 text-red-400 border border-red-500/30'
                          : an.advisory?.overall_risk === 'Healthy'
                            ? 'bg-emerald-950/90 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-950/90 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {an.advisory?.overall_risk || 'Unknown'}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">
                      {an.disease?.disease ?? (an.status === 'model_unavailable' ? 'Model unavailable' : '—')}
                    </h4>
                    <p className="text-xs text-slate-400 line-clamp-2 mt-0.5">
                      {an.advisory?.condition_summary}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                  <span>{new Date(an.created_at).toLocaleDateString()}</span>
                  <span className="text-emerald-400 font-semibold group-hover:underline flex items-center gap-1">
                    View Report <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
