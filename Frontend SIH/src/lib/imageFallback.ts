export const FALLBACK_LEAF_IMAGE = '/placeholder-leaf.svg';

export function handleImageError(e: React.SyntheticEvent<HTMLImageElement, Event>) {
  const target = e.currentTarget;
  if (target.src !== FALLBACK_LEAF_IMAGE && !target.src.endsWith('/placeholder-leaf.svg')) {
    target.onerror = null;
    target.src = FALLBACK_LEAF_IMAGE;
  }
}
