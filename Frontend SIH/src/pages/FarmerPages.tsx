import React, { useEffect, useState } from 'react';
import { useNavigate, useOutletContext, useParams, useLocation } from 'react-router-dom';
import { HomePage } from '../components/farmer/HomePage';
import { ScanWorkspace } from '../components/farmer/ScanWorkspace';
import { HistoryHub } from '../components/farmer/HistoryHub';
import { PestPixelOverlay } from '../components/farmer/PestPixelOverlay';
import { ReportView } from '../components/farmer/ReportView';
import { useFarmerApp } from '../context/FarmerAppContext';
import { api } from '../services/api';
import { AnalysisResponse, PestDetectResponse } from '../types';
import { confidenceBand, formatAiConfidence } from '../lib/crops';
import { LogOut, Languages } from 'lucide-react';
import type { FarmerOutletContext } from './FarmerLayout';
import { SupportedLanguage } from '../i18n/translations';

export const DashboardPage: React.FC = () => <HomePage />;

export const AnalyzePage: React.FC = () => {
  const { handleAnalyzeCrop, isScanning, scanProgressStep, scanError, userLocation } =
    useOutletContext<FarmerOutletContext>();

  return (
    <ScanWorkspace
      mode="disease"
      title="Scan disease"
      subtitle="Select your crop, upload a leaf photo, then analyze with the verified disease models."
      isLoading={isScanning}
      progressStep={scanProgressStep}
      error={scanError}
      onSubmit={async (file, crop) => {
        await handleAnalyzeCrop(file, userLocation.lat, userLocation.lon, crop);
      }}
    />
  );
};

export const PestDetectionPage: React.FC = () => {
  const { handleDetectPests, isPestScanning, pestProgressStep, pestError } =
    useOutletContext<FarmerOutletContext>();

  return (
    <ScanWorkspace
      mode="pest"
      title="Detect pests"
      subtitle="Upload a leaf or plant photo. The detector returns pest names with bounding boxes when found."
      isLoading={isPestScanning}
      progressStep={pestProgressStep}
      error={pestError}
      onSubmit={async (file, crop) => {
        await handleDetectPests(file, crop);
      }}
    />
  );
};

export const HistoryPage: React.FC = () => <HistoryHub />;

export const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { analyses } = useFarmerApp();
  const { handleRequestValidation } = useOutletContext<FarmerOutletContext>();
  const stateAnalysis = (location.state as { analysis?: AnalysisResponse } | null)?.analysis;

  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(
    stateAnalysis || analyses.find((a) => a.id === id) || null
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!analysis);

  useEffect(() => {
    if (analysis || !id) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await api.getAnalysisById(id);
        if (!cancelled) setAnalysis(data);
      } catch (err: unknown) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Report not found');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, analysis]);

  if (loading) {
    return (
      <div className="cs-surface p-8 animate-pulse space-y-3" aria-busy="true">
        <div className="h-6 w-1/3 rounded bg-[var(--cs-bg-accent)]" />
        <div className="h-40 rounded bg-[var(--cs-bg-accent)]" />
      </div>
    );
  }
  if (error || !analysis) {
    return (
      <div className="cs-surface p-8 text-center space-y-3">
        <p className="font-semibold">Report unavailable</p>
        <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
          {error || 'This diagnosis could not be loaded.'}
        </p>
        <button type="button" className="cs-btn cs-btn-secondary" onClick={() => navigate('/farmer/history')}>
          Back to history
        </button>
      </div>
    );
  }

  const band = confidenceBand(analysis.disease?.confidence);
  const guidance =
    analysis.inference_meta?.guidance_available ??
    analysis.advisory?.pesticide_recommendation?.guidance_available;

  return (
    <div className="space-y-5">
      <DiseaseResultHeader analysis={analysis} band={band} />
      {guidance === false && (
        <div className="rounded-[14px] p-4 border" style={{ background: 'var(--cs-warn-soft)', borderColor: '#f0d2a0' }}>
          <p className="font-bold text-sm" style={{ color: 'var(--cs-warn)' }}>
            Verified guidance is currently unavailable for this diagnosis.
          </p>
          <p className="text-sm mt-1" style={{ color: 'var(--cs-ink-soft)' }}>
            Consult a KVK/agricultural expert.
          </p>
        </div>
      )}
      <ReportView
        analysis={analysis}
        onBack={() => navigate('/farmer/history')}
        onRequestValidation={handleRequestValidation}
      />
    </div>
  );
};

function DiseaseResultHeader({
  analysis,
  band,
}: {
  analysis: AnalysisResponse;
  band: { label: string; tone: string };
}) {
  const toneStyle =
    band.tone === 'high'
      ? { background: 'var(--cs-success-soft)', color: 'var(--cs-success)' }
      : band.tone === 'moderate'
        ? { background: 'var(--cs-warn-soft)', color: 'var(--cs-warn)' }
        : band.tone === 'low'
          ? { background: 'var(--cs-danger-soft)', color: 'var(--cs-danger)' }
          : { background: 'var(--cs-bg-accent)', color: 'var(--cs-muted)' };

  return (
    <section className="cs-surface p-4 sm:p-5 space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        <img
          src={analysis.image_url}
          alt={`Scanned ${analysis.crop} leaf`}
          className="w-full sm:w-44 h-44 object-cover rounded-[12px] bg-[var(--cs-bg-accent)]"
        />
        <div className="space-y-2 flex-1">
          <p className="text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--cs-muted)' }}>
            Model-backed AI result
          </p>
          <h1 className="text-2xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
            {analysis.disease?.disease || analysis.disease?.display_label || 'Diagnosis'}
          </h1>
          <div className="flex flex-wrap gap-2">
            <span className="cs-chip" style={{ background: 'var(--cs-primary-soft)', color: 'var(--cs-primary)' }}>
              Crop: {analysis.crop}
            </span>
            <span className="cs-chip" style={toneStyle}>
              {band.label}
            </span>
          </div>
          <p className="text-sm">
            <span className="font-bold">AI confidence:</span> {formatAiConfidence(analysis.disease?.confidence)}
          </p>
          <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
            AI confidence is not field accuracy.
          </p>
        </div>
      </div>
    </section>
  );
}

export const PestReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { pestAnalyses } = useFarmerApp();
  const statePest = (location.state as { pest?: PestDetectResponse } | null)?.pest;
  const [pest, setPest] = useState<PestDetectResponse | null>(
    statePest || pestAnalyses.find((p) => p.id === id) || null
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!pest);

  useEffect(() => {
    if (pest || !id) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await api.getPestById(id);
        if (!cancelled) setPest(data);
      } catch (err: unknown) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Pest report not found');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, pest]);

  if (loading) {
    return <div className="cs-surface p-8 animate-pulse h-40" aria-busy="true" />;
  }
  if (error || !pest) {
    return (
      <div className="cs-surface p-8 text-center space-y-3">
        <p className="font-semibold">Pest report unavailable</p>
        <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
          {error}
        </p>
        <button type="button" className="cs-btn cs-btn-secondary" onClick={() => navigate('/farmer/history')}>
          Back to history
        </button>
      </div>
    );
  }

  const noPest = pest.status === 'no_pest_detected' || pest.count === 0;
  const guidance = pest.advisory?.guidance_available;

  return (
    <div className="space-y-5 max-w-3xl">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
          Pest detection result
        </h1>
        <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
          Crop hint: {pest.crop_hint || pest.crop || '—'}
        </p>
      </header>

      <PestPixelOverlay
        imageUrl={pest.image_url}
        detections={pest.detections || []}
        imageWidth={pest.image_width}
        imageHeight={pest.image_height}
      />

      {noPest ? (
        <div className="cs-surface p-5">
          <p className="font-bold">No verified pest detected in this image.</p>
          <p className="text-sm mt-1" style={{ color: 'var(--cs-muted)' }}>
            This does not prove the field is free of pests.
          </p>
        </div>
      ) : (
        <div className="cs-surface p-5 space-y-3">
          <p className="font-bold text-lg">Detected pests: {pest.count}</p>
          <ul className="space-y-2">
            {(pest.detections || []).map((d, i) => (
              <li key={`${d.raw_label}-${i}`} className="flex justify-between gap-3 text-sm border-b py-2" style={{ borderColor: 'var(--cs-border)' }}>
                <span className="font-semibold">{d.raw_label}</span>
                <span style={{ color: 'var(--cs-muted)' }}>AI confidence {formatAiConfidence(d.confidence)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="cs-surface p-5 space-y-2">
        <p className="text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--cs-muted)' }}>
          AI-estimated preliminary severity
        </p>
        <p className="text-xl font-bold capitalize">{pest.severity}</p>
        <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
          Preliminary AI estimate. Field conditions may differ.
        </p>
        {pest.severity_label && (
          <p className="text-sm" style={{ color: 'var(--cs-ink-soft)' }}>
            {pest.severity_label}
          </p>
        )}
      </div>

      <div className="cs-surface p-5 space-y-2">
        <h2 className="font-bold text-lg" style={{ fontFamily: 'var(--font-heading)' }}>
          Recommendations
        </h2>
        {guidance === false || guidance == null ? (
          <p className="text-sm" style={{ color: 'var(--cs-ink-soft)' }}>
            Verified pest-management guidance is unavailable for this result.
          </p>
        ) : (
          <>
            <p className="text-sm">{pest.advisory?.condition_summary}</p>
            {pest.advisory?.immediate_action && (
              <p className="text-sm">
                <span className="font-bold">Next step: </span>
                {pest.advisory.immediate_action}
              </p>
            )}
            {pest.advisory?.pesticide_recommendation?.guidance_available && (
              <div className="text-sm mt-2 p-3 rounded-[10px]" style={{ background: 'var(--cs-surface-2)' }}>
                <p className="font-bold">{pest.advisory.pesticide_recommendation.chemical_name}</p>
                <p>{pest.advisory.pesticide_recommendation.active_ingredient}</p>
                <p>{pest.advisory.pesticide_recommendation.exact_dose_per_liter}</p>
              </div>
            )}
          </>
        )}
      </div>

      <button type="button" className="cs-btn cs-btn-secondary" onClick={() => navigate('/farmer/history')}>
        Back to history
      </button>
    </div>
  );
};

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, language, setLanguage, logout } = useFarmerApp();
  if (!user) return null;

  const languages: { code: SupportedLanguage; label: string }[] = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'Hindi' },
    { code: 'mr', label: 'Marathi' },
  ];

  return (
    <div className="max-w-lg space-y-5">
      <header>
        <h1 className="text-2xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
          Profile
        </h1>
        <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
          Your farmer account details
        </p>
      </header>
      <div className="cs-surface p-5 space-y-3">
        <div>
          <p className="text-xs font-bold" style={{ color: 'var(--cs-muted)' }}>
            Name
          </p>
          <p className="font-semibold">{user.full_name}</p>
        </div>
        <div>
          <p className="text-xs font-bold" style={{ color: 'var(--cs-muted)' }}>
            Email
          </p>
          <p className="font-semibold">{user.email}</p>
        </div>
        {(user.district || user.state) && (
          <div>
            <p className="text-xs font-bold" style={{ color: 'var(--cs-muted)' }}>
              Region
            </p>
            <p className="font-semibold">{[user.district, user.state].filter(Boolean).join(', ')}</p>
          </div>
        )}
      </div>

      <div className="cs-surface p-5 space-y-3">
        <label className="cs-label flex items-center gap-2" htmlFor="lang">
          <Languages className="w-4 h-4" aria-hidden />
          Language
        </label>
        <select
          id="lang"
          className="cs-input"
          value={language}
          onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
        >
          {languages.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        className="cs-btn cs-btn-ghost w-full"
        onClick={() => {
          logout();
          navigate('/login', { replace: true });
        }}
      >
        <LogOut className="w-4 h-4" aria-hidden />
        Log out
      </button>
    </div>
  );
};

/* Keep secondary pages lightweight / reachable if linked */
export const AssistantPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="cs-surface p-6 space-y-3">
      <h1 className="text-xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
        Assistant
      </h1>
      <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
        Use Scan Disease or Detect Pest for model-backed results. Assistant chat remains available from older builds.
      </p>
      <button type="button" className="cs-btn cs-btn-primary" onClick={() => navigate('/farmer/analyze')}>
        Go to disease scan
      </button>
    </div>
  );
};

export const WeatherPage: React.FC = () => {
  const { weather, userLocation, refreshWeather } = useFarmerApp();
  return (
    <div className="cs-surface p-6 space-y-3 max-w-xl">
      <h1 className="text-xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
        Weather
      </h1>
      <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
        {userLocation.name}
      </p>
      {!weather || weather.is_unavailable ? (
        <p className="text-sm">Weather unavailable. No estimated values are shown.</p>
      ) : (
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt style={{ color: 'var(--cs-muted)' }}>Temperature</dt>
            <dd className="font-bold text-lg">{weather.temperature}°C</dd>
          </div>
          <div>
            <dt style={{ color: 'var(--cs-muted)' }}>Humidity</dt>
            <dd className="font-bold text-lg">{weather.relative_humidity}%</dd>
          </div>
        </dl>
      )}
      <button type="button" className="cs-btn cs-btn-secondary" onClick={() => refreshWeather()}>
        Refresh
      </button>
    </div>
  );
};

export const AlertsPage: React.FC = () => {
  const navigate = useNavigate();
  const { analyses } = useFarmerApp();
  const alerts = analyses.filter(
    (a) => a.advisory?.overall_risk === 'High Risk' || a.advisory?.overall_risk === 'Critical'
  );
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
        Alerts
      </h1>
      {alerts.length === 0 ? (
        <div className="cs-surface p-6 text-center text-sm" style={{ color: 'var(--cs-muted)' }}>
          No high-risk alerts from your diagnoses.
        </div>
      ) : (
        alerts.map((a) => (
          <button
            key={a.id}
            type="button"
            className="cs-surface w-full p-4 text-left"
            onClick={() => navigate(`/farmer/reports/${a.id}`)}
          >
            <p className="font-bold">
              {a.crop} · {a.disease?.disease}
            </p>
            <p className="text-sm" style={{ color: 'var(--cs-warn)' }}>
              {a.advisory?.overall_risk}
            </p>
          </button>
        ))
      )}
    </div>
  );
};
