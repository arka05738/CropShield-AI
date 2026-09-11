import React, { useMemo, useRef, useState } from 'react';
import { Camera, ImagePlus, Loader2, X } from 'lucide-react';
import { SUPPORTED_CROPS } from '../../lib/crops';
import { friendlyApiError } from '../../lib/crops';

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
  const [crop, setCrop] = useState('Rice');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);

  const stepLabel = useMemo(() => STEPS[Math.min(progressStep, STEPS.length - 1)], [progressStep]);

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

      <section className="cs-surface p-4 sm:p-5 space-y-3">
        <label className="cs-label" htmlFor="crop-select">
          Select crop
        </label>
        <select
          id="crop-select"
          className="cs-input"
          value={crop}
          onChange={(e) => setCrop(e.target.value)}
          disabled={isLoading}
        >
          {SUPPORTED_CROPS.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
          {mode === 'disease'
            ? 'Crop hint routes the disease model. Choose the crop you photographed.'
            : 'Crop hint helps advisory matching. Pest detection uses the verified object detector.'}
        </p>
      </section>

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
              Honest status — not a fake percentage.
            </p>
          </div>
        </div>
      )}

      <button
        type="button"
        className="cs-btn cs-btn-primary w-full"
        disabled={!file || isLoading}
        onClick={async () => {
          if (!file) return;
          try {
            await onSubmit(file, crop);
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
