import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Leaf, Bug, ChevronRight, Clock } from 'lucide-react';
import { useFarmerApp } from '../../context/FarmerAppContext';
import { SUPPORTED_CROPS, formatAiConfidence } from '../../lib/crops';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, analyses, pestAnalyses } = useFarmerApp();

  const recent = [
    ...analyses.slice(0, 4).map((a) => ({
      id: a.id,
      kind: 'disease' as const,
      crop: a.crop,
      title: a.disease?.disease || a.disease?.display_label || 'Disease scan',
      confidence: a.disease?.confidence,
      date: a.created_at,
      image: a.image_url,
    })),
    ...pestAnalyses.slice(0, 4).map((p) => ({
      id: p.id,
      kind: 'pest' as const,
      crop: p.crop_hint || '—',
      title: p.pest || p.raw_label || (p.count ? `${p.count} detections` : 'Pest scan'),
      confidence: p.confidence ?? p.detections?.[0]?.confidence,
      date: p.created_at,
      image: p.image_url,
    })),
  ]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 5);

  return (
    <div className="space-y-8">
      <section className="cs-hero-panel p-6 sm:p-8 relative z-0">
        <div className="relative z-10 max-w-xl space-y-4">
          <p className="text-sm font-semibold text-emerald-100/90">Hello, {user?.full_name?.split(' ')[0] || 'Farmer'}</p>
          <h1 className="text-3xl sm:text-4xl font-bold leading-tight" style={{ fontFamily: 'var(--font-heading)' }}>
            Protect your crops with AI
          </h1>
          <p className="text-base sm:text-lg text-emerald-50/90">
            Scan a leaf to identify crop diseases and pests.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button type="button" className="cs-btn bg-white text-[var(--cs-primary)] hover:bg-emerald-50" onClick={() => navigate('/farmer/analyze')}>
              <Leaf className="w-5 h-5" aria-hidden />
              Scan Disease
            </button>
            <button
              type="button"
              className="cs-btn border border-white/40 text-white bg-white/10 hover:bg-white/20"
              onClick={() => navigate('/farmer/pest-detection')}
            >
              <Bug className="w-5 h-5" aria-hidden />
              Detect Pest
            </button>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
            Recent analyses
          </h2>
          <button type="button" className="text-sm font-bold" style={{ color: 'var(--cs-primary)' }} onClick={() => navigate('/farmer/history')}>
            View all
          </button>
        </div>
        {recent.length === 0 ? (
          <div className="cs-surface p-6 text-center">
            <p className="font-semibold">No analyses yet</p>
            <p className="text-sm mt-1" style={{ color: 'var(--cs-muted)' }}>
              Start with a disease scan or pest detection.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {recent.map((item) => (
              <li key={`${item.kind}-${item.id}`}>
                <button
                  type="button"
                  className="cs-surface w-full p-3 flex items-center gap-3 text-left hover:border-[var(--cs-primary-mid)] transition-colors"
                  onClick={() =>
                    navigate(
                      item.kind === 'disease' ? `/farmer/reports/${item.id}` : `/farmer/pest-reports/${item.id}`,
                      { state: item.kind === 'disease' ? { analysis: analyses.find((a) => a.id === item.id) } : { pest: pestAnalyses.find((p) => p.id === item.id) } }
                    )
                  }
                >
                  <div className="w-14 h-14 rounded-lg overflow-hidden shrink-0 bg-[var(--cs-bg-accent)]">
                    {item.image ? (
                      <img src={item.image} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-[var(--cs-muted)]">
                        <Clock className="w-5 h-5" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="cs-chip" style={{ background: 'var(--cs-primary-soft)', color: 'var(--cs-primary)' }}>
                        {item.crop}
                      </span>
                      <span className="cs-chip" style={{ background: item.kind === 'pest' ? 'var(--cs-warn-soft)' : 'var(--cs-info-soft)', color: item.kind === 'pest' ? 'var(--cs-warn)' : 'var(--cs-info)' }}>
                        {item.kind === 'pest' ? 'Pest' : 'Disease'}
                      </span>
                    </div>
                    <p className="font-bold truncate mt-1">{item.title}</p>
                    <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
                      AI confidence {formatAiConfidence(item.confidence)} · {new Date(item.date).toLocaleString()}
                    </p>
                  </div>
                  <ChevronRight className="w-5 h-5 shrink-0" style={{ color: 'var(--cs-muted)' }} aria-hidden />
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
          Supported crops
        </h2>
        <p className="text-sm" style={{ color: 'var(--cs-muted)' }}>
          Disease models are available for these crops. Others may return model unavailable.
        </p>
        <div className="flex flex-wrap gap-2">
          {SUPPORTED_CROPS.map((crop) => (
            <span key={crop} className="cs-chip" style={{ background: 'var(--cs-surface)', border: '1px solid var(--cs-border)', color: 'var(--cs-ink-soft)' }}>
              {crop}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
};
