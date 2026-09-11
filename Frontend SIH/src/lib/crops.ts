/** Supported disease/pest crop routes — must match backend HF registry. */
export const SUPPORTED_CROPS = [
  'Grape',
  'Tomato',
  'Potato',
  'Maize',
  'Sugarcane',
  'Rice',
  'Wheat',
  'Cotton',
  'Sunflower',
] as const;

export type SupportedCrop = (typeof SUPPORTED_CROPS)[number];

export function confidenceBand(confidence: number | null | undefined): {
  label: string;
  tone: 'high' | 'moderate' | 'low' | 'unknown';
} {
  if (confidence == null || Number.isNaN(confidence)) {
    return { label: 'AI confidence unavailable', tone: 'unknown' };
  }
  if (confidence >= 0.75) return { label: 'High confidence', tone: 'high' };
  if (confidence >= 0.45) return { label: 'Moderate confidence', tone: 'moderate' };
  return { label: 'Low confidence', tone: 'low' };
}

export function formatAiConfidence(confidence: number | null | undefined): string {
  if (confidence == null || Number.isNaN(confidence)) return '—';
  return `${Math.round(confidence * 100)}%`;
}

export function friendlyApiError(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err || 'Something went wrong');
  const lower = msg.toLowerCase();
  if (lower.includes('401') || lower.includes('auth')) return 'Authentication failed. Please sign in again.';
  if (lower.includes('413') || lower.includes('too large') || lower.includes('maximum size')) {
    return 'Image is too large. Please upload a smaller photo (under 10 MB).';
  }
  if (lower.includes('unsupported') || lower.includes('format') || lower.includes('invalid image')) {
    return 'Invalid image. Please upload a JPG, PNG, or WebP leaf photo.';
  }
  if (lower.includes('503') || lower.includes('unavailable')) {
    return 'Service temporarily unavailable. Please try again shortly.';
  }
  if (lower.includes('model')) return 'Model unavailable for this request.';
  return msg;
}
