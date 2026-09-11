import React, { useMemo, useRef, useState } from 'react';
import { Camera, ImagePlus, Loader2, Sparkles, X } from 'lucide-react';
import { SUPPORTED_CROPS } from '../../lib/crops';
import { friendlyApiError } from '../../lib/crops';
import { api } from '../../services/api';
import { CropCandidate } from '../../types';

const STEPS = ['Uploading image...', 'Analyzing crop...', 'Preparing recommendation...'] as const;

type Props = {
  mode: 'disease' | 'pest';
  title: string;
  subtitle: string;
  onSubmit: (file: File, crop: string) => Promise<void>;
  isLoading: boolean;
  progressStep: number;
  error?: string | null;
};

export const ScanWorkspace: React.FC<Props> = ({
  mode,
  title,
  subtitle,
  onSubmit,
  isLoading,
  progressStep,
  error,
}) => {
  const [crop, setCrop] = useState<string>('auto');
  const [detectedCrop, setDetectedCrop] = useState<string | null>(null);
  const [detectedConfidence, setDetectedConfidence] = useState<number | null>(null);
  const [topCandidates, setTopCandidates] = useState<CropCandidate[]>([]);
  const [isIdentifyingCrop, setIsIdentifyingCrop] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);

  const stepLabel = useMemo(() => STEPS[Math.min(progressStep, STEPS.length - 1)], [progressStep]);

  const runAutoCropDetection = async (f: File) => {
    setIsIdentifyingCrop(true);
    try {
      const res = await api.identifyCrop(f);
      if (res.status === 'success' && res.crop) {
        setDetectedCrop(res.crop);
        setDetectedConfidence(res.confidence ?? 0.9);
        setTopCandidates(res.top_candidates || []);
        // Automatically select the detected crop
        setCrop(res.crop);
      }
    } catch (err) {
      console.warn('Auto crop detection non-fatal error:', err);
    } finally {
      setIsIdentifyingCrop(false);
    }
  };

  const assignFile = (f: File | null) => {
    if (!f) return;
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(f.type) && !/\.(jpe?g|png|webp)$/i.test(f.name)) {
      setLocalError('Invalid image. Please upload a JPG, PNG, or WebP leaf photo.');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setLocalError('Image is too large. Please upload a smaller photo (under 10 MB).');
      return;
    }
    setLocalError(null);
    setFile(f);
    setPreview(URL.createObjectURL(f));
    // Trigger automatic crop identification from the uploaded picture
    runAutoCropDetection(f);
  };

  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    assignFile(f);
    e.target.value = '';
  };

  const clear = () => {
    setFile(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setDetectedCrop(null);
    setDetectedConfidence(null);
    setTopCandidates([]);
    setCrop('auto');
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <header className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
          {title}
        </h1>
        <p className="text-sm sm:text-base" style={{ color: 'var(--cs-muted)' }}>
          {subtitle}
        </p>
      </header>

      {/* Crop Selection with Automatic Hugging Face Detection */}
      <section className="cs-surface p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between">
          <label className="cs-label" htmlFor="crop-select">
            Crop Species
          </label>
          {isIdentifyingCrop && (
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              AI identifying crop...
            </span>
          )}
        </div>

        {/* AI Auto-Detection Feedback Banner */}
        {detectedCrop && !isIdentifyingCrop && (
          <div className="flex items-center justify-between gap-2 p-2.5 rounded-lg border bg-emerald-50/80 border-emerald-200 text-emerald-900 text-xs">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>
                Auto-identified from photo: <strong className="font-bold text-emerald-950">{detectedCrop}</strong>{' '}
                {detectedConfidence != null && (
                  <span className="text-emerald-700">({Math.round(detectedConfidence * 100)}% match)</span>
                )}
              </span>
            </div>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 bg-emerald-100/90 text-emerald-800 rounded border border-emerald-200">
              Hugging Face ViT
            </span>
          </div>
        )}

        {isIdentifyingCrop && (
          <div className="flex items-center gap-2 p-2.5 rounded-lg border bg-blue-50/80 border-blue-200 text-blue-900 text-xs animate-pulse">
            <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
            <span>Analyzing leaf morphology with Hugging Face Vision Transformers to select crop...</span>
          </div>
        )}

        <select
          id="crop-select"
          className="cs-input"
          value={crop}
          onChange={(e) => setCrop(e.target.value)}
          disabled={isLoading || isIdentifyingCrop}
        >
          <option value="auto">
            {detectedCrop ? `✨ Auto-detected: ${detectedCrop}` : '✨ Auto-detect from picture (AI)'}
          </option>
          {SUPPORTED_CROPS.map((c) => (
            <option key={c} value={c}>
              {c} {c === detectedCrop ? '✓ (Detected from picture)' : ''}
            </option>
          ))}
        </select>

        {topCandidates.length > 1 && detectedCrop && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px] text-gray-500">
            <span className="font-medium text-gray-600">Other possibilities:</span>
            {topCandidates.slice(1, 3).map((cand) => (
              <button
                key={cand.crop}
                type="button"
                className="underline text-emerald-700 hover:text-emerald-900 cursor-pointer"
                onClick={() => setCrop(cand.crop)}
              >
                {cand.crop} ({Math.round(cand.confidence * 100)}%)
              </button>
            ))}
          </div>
        )}

        <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
          {mode === 'disease'
            ? 'The crop is automatically identified from your photo using Hugging Face Vision models, or you can pick manually.'
            : 'Crop species guides precision agronomic advisories and pest management thresholds.'}
        </p>
      </section>

      {/* Image Upload / Camera Capture */}
      <section className="cs-surface p-4 sm:p-5 space-y-4">
        <p className="cs-label">Upload or capture leaf image</p>
        {!preview ? (
          <div
            className="border-2 border-dashed rounded-[14px] p-8 text-center space-y-4"
            style={{ borderColor: 'var(--cs-border-strong)', background: 'var(--cs-surface-2)' }}
          >
            <ImagePlus className="w-10 h-10 mx-auto" style={{ color: 'var(--cs-primary)' }} aria-hidden />
            <p className="text-sm font-medium">Clear close-up of the leaf works best</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button type="button" className="cs-btn cs-btn-primary" onClick={() => inputRef.current?.click()}>
                Choose photo
              </button>
              <button type="button" className="cs-btn cs-btn-secondary" onClick={() => cameraRef.current?.click()}>
                <Camera className="w-4 h-4" aria-hidden />
                Use camera
              </button>
            </div>
            <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={onPick} />
            <input
              ref={cameraRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={onPick}
            />
          </div>
        ) : (
          <div className="space-y-3">
            <div className="relative rounded-[14px] overflow-hidden border" style={{ borderColor: 'var(--cs-border)' }}>
              <img src={preview} alt="Selected leaf preview" className="w-full max-h-[420px] object-contain bg-[var(--cs-bg-accent)]" />
              <button
                type="button"
                className="absolute top-3 right-3 cs-btn cs-btn-ghost min-h-[40px] px-3 bg-white/95"
                onClick={clear}
                disabled={isLoading}
                aria-label="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs truncate" style={{ color: 'var(--cs-muted)' }}>
              {file?.name}
            </p>
          </div>
        )}
      </section>

      {(localError || error) && (
        <div className="rounded-[14px] p-4 border" style={{ background: 'var(--cs-danger-soft)', borderColor: '#f0b4ae', color: 'var(--cs-danger)' }} role="alert">
          <p className="font-bold text-sm">Something went wrong</p>
          <p className="text-sm mt-1">{localError || error}</p>
        </div>
      )}

      {isLoading && (
        <div className="cs-surface p-5 flex items-center gap-4" role="status" aria-live="polite">
          <Loader2 className="w-7 h-7 animate-spin shrink-0" style={{ color: 'var(--cs-primary)' }} />
          <div>
            <p className="font-bold">{stepLabel}</p>
            <p className="text-xs mt-1" style={{ color: 'var(--cs-muted)' }}>
              Honest status — running Hugging Face Vision Transformer models.
            </p>
          </div>
        </div>
      )}

      <button
        type="button"
        className="cs-btn cs-btn-primary w-full"
        disabled={!file || isLoading || isIdentifyingCrop}
        onClick={async () => {
          if (!file) return;
          try {
            // If crop is still 'auto', pass detectedCrop or empty (backend classifies directly)
            const effectiveCrop = crop === 'auto' ? (detectedCrop || '') : crop;
            await onSubmit(file, effectiveCrop);
          } catch (err) {
            setLocalError(friendlyApiError(err));
          }
        }}
      >
        {mode === 'disease' ? 'Analyze disease' : 'Detect pests'}
      </button>
    </div>
  );
};
