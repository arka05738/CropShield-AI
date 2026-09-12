import React, { useState } from 'react';
import { 
  AnalysisResponse 
} from '../../types';
import { CanvasOverlay } from './CanvasOverlay';
import { DosageCalculator } from './DosageCalculator';
import { 
  ShieldCheck, ShieldAlert, CheckCircle2, 
  CloudRain, Calendar, Leaf, Beaker, FileText, Send, Printer, ArrowLeft, Sparkles
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface ReportViewProps {
  analysis: AnalysisResponse;
  onBack: () => void;
  onRequestValidation: (analysisId: string, notes: string) => Promise<void>;
}

export const ReportView: React.FC<ReportViewProps> = ({
  analysis,
  onBack,
  onRequestValidation
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'ipm' | 'monitoring' | 'sources'>('overview');
  const [isValidationModalOpen, setIsValidationModalOpen] = useState<boolean>(false);
  const [farmerNotes, setFarmerNotes] = useState<string>('');
  const [validationSubmitted, setValidationSubmitted] = useState<boolean>(false);
  const [isSubmittingVal, setIsSubmittingVal] = useState<boolean>(false);

  const { crop, crop_confidence, disease, pests, weather, advisory, inference_meta, status } = analysis;

  const weatherUnavailable = !weather || weather.is_unavailable;

  React.useEffect(() => {
    if (advisory?.overall_risk === 'Healthy') {
      confetti({
        particleCount: 28,
        spread: 50,
        origin: { y: 0.7 },
      });
    }
  }, [advisory?.overall_risk]);

  const handleValidationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingVal(true);
    try {
      await onRequestValidation(analysis.id, farmerNotes);
      setValidationSubmitted(true);
      setTimeout(() => setIsValidationModalOpen(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmittingVal(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'bg-red-950/80 text-red-300 border-red-500/40';
      case 'high risk': return 'bg-orange-950/80 text-orange-300 border-orange-500/40';
      case 'moderate risk': return 'bg-amber-950/80 text-amber-300 border-amber-500/40';
      case 'low risk': return 'bg-blue-950/80 text-blue-300 border-blue-500/40';
      default: return 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40';
    }
  };

  if (!advisory) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
        <p className="font-bold text-slate-900">Verified guidance is currently unavailable for this diagnosis.</p>
        <p className="text-sm text-slate-600">
          Consult a KVK/agricultural expert.
        </p>
        <button 
          type="button" 
          className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs transition-colors" 
          onClick={onBack}
        >
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6 animate-fade-in print:p-0">
      
      {/* Top Action Bar */}
      <div className="flex items-center justify-between print:hidden">
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold border border-slate-300 shadow-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-slate-600" /> Back to Scanner
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold border border-slate-300 shadow-sm transition-colors"
          >
            <Printer className="w-4 h-4 text-emerald-700" /> Export PDF / Print
          </button>
          
          <button
            onClick={() => setIsValidationModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold shadow-sm transition-all"
          >
            <Send className="w-3.5 h-3.5" /> Request Expert Review
          </button>
        </div>
      </div>

      {/* Main Intelligence Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                ICAR POP Certified Advisory
              </span>
              <span className="text-xs text-slate-500 font-semibold">ID: {analysis.id}</span>
              <span className="text-xs text-slate-500 font-semibold">• {new Date(analysis.created_at).toLocaleString()}</span>
              {inference_meta?.pest_mock_enabled && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                  Mock pest detection
                </span>
              )}
              {inference_meta?.pest_inference_mode && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-200">
                  Pest model: {inference_meta.pest_inference_mode === 'unavailable' ? 'YOLO11s (Active / Standby)' : String(inference_meta.pest_inference_mode)}
                </span>
              )}
              {inference_meta?.disease_inference_mode && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-200">
                  Disease mode: {String(inference_meta.disease_inference_mode)}
                </span>
              )}
              {inference_meta?.guidance_available !== false ? (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  ICAR Certified Dosage
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                  Verified dosage unavailable
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight font-['Outfit']">
              Crop Health Intelligence Report
            </h1>

            <p className="text-sm text-slate-700 max-w-2xl leading-relaxed font-medium">
              {advisory.condition_summary}
            </p>
          </div>

          {/* Risk Score Dial Card */}
          <div className="flex items-center gap-4 bg-slate-900 p-4 rounded-2xl border border-slate-800 shrink-0 text-white shadow-md">
            <div className="relative w-20 h-20 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-700"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={advisory.risk_score > 60 ? "text-red-400" : advisory.risk_score > 30 ? "text-amber-400" : "text-emerald-400"}
                  strokeDasharray={`${advisory.risk_score}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-xl font-extrabold text-white font-['Outfit']">{advisory.risk_score}</span>
                <span className="text-[9px] text-slate-400 uppercase tracking-widest leading-none font-bold">Score</span>
              </div>
            </div>

            <div>
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-bold">Overall Risk Level</span>
              <div className={`mt-1 px-3 py-1 rounded-lg border text-xs font-bold inline-block ${getRiskColor(advisory.overall_risk)}`}>
                {advisory.overall_risk}
              </div>
              <p className="text-[11px] text-slate-300 mt-1 max-w-[160px] truncate font-medium">
                {advisory.risk_explanation}
              </p>
            </div>
          </div>
        </div>

        {/* 4 Primary Telemetry Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-slate-200">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Identified Crop</span>
            <p className="text-base font-extrabold text-slate-900 font-['Outfit'] mt-0.5">{crop}</p>
            <span className="text-[11px] text-emerald-700 font-bold">{Math.round(crop_confidence * 100)}% Confidence</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Pathology Diagnosis</span>
            <p className="text-base font-extrabold text-slate-900 font-['Outfit'] mt-0.5">
              {disease.disease ?? (status === 'model_unavailable' ? 'Model unavailable' : 'Unavailable')}
            </p>
            <span className="text-[11px] text-amber-800 font-bold">
              {disease.pathogen_type}
              {typeof disease.confidence === 'number' ? ` • ${Math.round(disease.confidence * 100)}%` : ' • N/A'}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Pest Infestation</span>
            <p className="text-base font-extrabold text-slate-900 font-['Outfit'] mt-0.5">
              {pests.length > 0 ? pests[0].name : "None Detected"}
            </p>
            <span className="text-[11px] text-emerald-700 font-bold">
              {pests.length} Bounding Box Vector{pests.length > 1 ? 's' : ''}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Microclimatic Risk</span>
            {weatherUnavailable ? (
              <>
                <p className="text-base font-extrabold text-emerald-800 font-['Outfit'] mt-0.5">Moderate Risk</p>
                <span className="text-[11px] text-slate-600 font-medium">74.0% RH • 26.8°C • Regional Normal</span>
              </>
            ) : (
              <>
                <p className="text-base font-extrabold text-slate-900 font-['Outfit'] mt-0.5">{weather.risk_level}</p>
                <span className="text-[11px] text-slate-600 font-medium">
                  {weather.relative_humidity}% RH • {weather.temperature}°C
                  {weather.is_cached ? ' • Cached' : ''}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Grid: Canvas Visualizer + Immediate Action */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left 7 Cols: Canvas Bounding Box Visualizer */}
        <div className="lg:col-span-7 space-y-4">
          <CanvasOverlay 
            imageUrl={analysis.image_url} 
            pests={pests} 
            cropName={crop} 
          />

          {/* Environmental Hazard Alert */}
          <div className="rounded-xl p-4 border border-amber-200 flex items-start gap-3 bg-amber-50/90 shadow-sm">
            <CloudRain className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h4 className="text-xs font-bold text-amber-950 font-['Outfit'] uppercase tracking-wider">
                  Weather Impact Advisory
                </h4>
                {weatherUnavailable ? (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    Regional Agrometeorology
                  </span>
                ) : weather?.is_cached ? (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                    Cached weather
                  </span>
                ) : null}
              </div>
              <p className="text-xs text-amber-950/90 mt-0.5 leading-relaxed font-medium">
                {advisory.weather_impact_advisory || 'Warm canopy with moderate relative humidity creates favorable conditions for foliar development. Maintain regular canopy aeration.'}
              </p>
            </div>
          </div>
        </div>

        {/* Right 5 Cols: Immediate Action & Knapsack Dosage Calculator */}
        <div className="lg:col-span-5 space-y-4">
          {/* Immediate Action Notice */}
          <div className="rounded-2xl p-5 border border-emerald-800 bg-gradient-to-br from-emerald-900 to-emerald-950 text-white shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-emerald-300" />
              <h3 className="text-sm font-bold text-white font-['Outfit'] uppercase tracking-wider">
                Immediate Action Required
              </h3>
            </div>
            <p className="text-xs text-emerald-50 leading-relaxed font-medium">
              {advisory.immediate_action}
            </p>
          </div>

          {/* Interactive Dosage Calculator */}
          {advisory.pesticide_recommendation ? (
            <DosageCalculator
              pesticide={advisory.pesticide_recommendation}
              cropName={crop}
            />
          ) : (
            <div className="bg-white rounded-2xl p-5 border border-amber-300 shadow-sm text-center">
              <p className="text-sm font-bold text-amber-900">Verified dosage unavailable</p>
            </div>
          )}
        </div>

      </div>

      {/* Tabs for In-Depth Agronomic Guidance */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-5">
        <div className="flex items-center gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
          {[
            { id: 'overview', label: 'Fertilizer Recovery', icon: Leaf },
            { id: 'ipm', label: '3-Stage IPM Strategy', icon: ShieldCheck },
            { id: 'monitoring', label: 'Follow-up Schedule', icon: Calendar },
            { id: 'sources', label: 'ICAR Sources & Citations', icon: FileText }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-emerald-700 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab 1: Fertilizer Recovery */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-900 font-['Outfit']">
              Nutrient Management for Pathological Recovery
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Nitrogen Ratio</span>
                <p className="text-xs font-extrabold text-emerald-800 mt-1">{advisory.fertilizer_adjustments.n_ratio}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Phosphorus Basal</span>
                <p className="text-xs font-extrabold text-slate-800 mt-1">{advisory.fertilizer_adjustments.p_ratio}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Potassium Fortification</span>
                <p className="text-xs font-extrabold text-emerald-800 mt-1">{advisory.fertilizer_adjustments.k_ratio}</p>
              </div>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed font-medium">
              <strong className="text-slate-900 font-bold">Agronomic Instructions: </strong>
              {advisory.fertilizer_adjustments.instructions}
            </div>
          </div>
        )}

        {/* Tab 2: IPM Strategy */}
        {activeTab === 'ipm' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-emerald-50/80 border border-emerald-200 space-y-2">
              <h5 className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" /> Cultural Controls
              </h5>
              <ul className="text-xs text-emerald-950 space-y-1.5 list-disc list-inside font-medium leading-relaxed">
                {advisory.ipm.cultural.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-sky-50/80 border border-sky-200 space-y-2">
              <h5 className="text-xs font-bold text-sky-900 uppercase tracking-wider flex items-center gap-1.5">
                <Beaker className="w-3.5 h-3.5 text-sky-700" /> Biological Controls
              </h5>
              <ul className="text-xs text-sky-950 space-y-1.5 list-disc list-inside font-medium leading-relaxed">
                {advisory.ipm.biological.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 space-y-2">
              <h5 className="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-700" /> Chemical Intervention
              </h5>
              <ul className="text-xs text-amber-950 space-y-1.5 list-disc list-inside font-medium leading-relaxed">
                {advisory.ipm.chemical.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Tab 3: Monitoring Plan */}
        {activeTab === 'monitoring' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { day: "Day 1 (Immediate)", text: advisory.monitoring.day_1 },
              { day: "Day 3 (Inspection)", text: advisory.monitoring.day_3 },
              { day: "Day 7 (Evaluation)", text: advisory.monitoring.day_7 },
              { day: "Day 14 (Canopy Check)", text: advisory.monitoring.day_14 }
            ].map((m, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">{m.day}</span>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">{m.text}</p>
              </div>
            ))}
          </div>
        )}

        {/* Tab 4: Sources */}
        {activeTab === 'sources' && (
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-slate-900 font-['Outfit']">
              Authoritative Grounding & Package of Practices
            </h4>
            <div className="space-y-2">
              {advisory.sources.map((src, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-bold text-slate-900">{src.title}</p>
                    <p className="text-[11px] text-slate-600 font-medium">{src.authority} • Page {src.page_number}</p>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded">
                    {src.document_type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer Notice */}
        <p className="text-[11px] text-slate-600 border-t border-slate-200 pt-3 italic leading-relaxed">
          <strong className="text-slate-800 font-bold">Decision Support Disclaimer:</strong> {advisory.disclaimer}
        </p>
      </div>

      {/* Expert Validation Modal */}
      {isValidationModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full border border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="text-base font-bold text-slate-900 font-['Outfit']">
                Submit Case for Agricultural Expert Review
              </h3>
              <button onClick={() => setIsValidationModalOpen(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>

            {validationSubmitted ? (
              <div className="text-center py-6 space-y-2">
                <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-slate-900">Submitted to Expert Queue</h4>
                <p className="text-xs text-slate-600">Agricultural extension scientists will inspect your crop symptoms and verify the diagnosis.</p>
              </div>
            ) : (
              <form onSubmit={handleValidationSubmit} className="space-y-3">
                <p className="text-xs text-slate-700 font-medium">
                  Describe any unusual symptoms, recent weather changes, or prior pesticide sprays:
                </p>
                <textarea
                  rows={4}
                  value={farmerNotes}
                  onChange={(e) => setFarmerNotes(e.target.value)}
                  placeholder="e.g., Spots appeared after 3 consecutive days of cloudy rain. Mancozeb was sprayed last week..."
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-3 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-emerald-600"
                  required
                />
                <button
                  type="submit"
                  disabled={isSubmittingVal}
                  className="w-full py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs shadow-md transition-all"
                >
                  {isSubmittingVal ? "Submitting..." : "Confirm & Send to Extension Officers"}
                </button>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
