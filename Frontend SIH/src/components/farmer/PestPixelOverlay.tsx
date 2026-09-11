import React, { useEffect, useRef, useState } from 'react';
import { PestObjectDetectionItem } from '../../types';

type Props = {
  imageUrl: string;
  detections: PestObjectDetectionItem[];
  imageWidth: number;
  imageHeight: number;
};

/** Draws pixel-space backend boxes on the original image. */
export const PestPixelOverlay: React.FC<Props> = ({ imageUrl, detections, imageWidth, imageHeight }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageUrl;
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const w = imageWidth || img.naturalWidth;
      const h = imageHeight || img.naturalHeight;
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.drawImage(img, 0, 0, w, h);
      detections.forEach((d) => {
        const { x1, y1, x2, y2 } = d.bbox;
        const bw = Math.max(1, x2 - x1);
        const bh = Math.max(1, y2 - y1);
        ctx.strokeStyle = '#b42318';
        ctx.lineWidth = Math.max(2, Math.round(Math.min(w, h) / 200));
        ctx.strokeRect(x1, y1, bw, bh);
        const label = `${d.raw_label} (${Math.round(d.confidence * 100)}%)`;
        ctx.font = '600 14px Figtree, sans-serif';
        const tw = ctx.measureText(label).width + 12;
        const th = 22;
        const ly = y1 - th - 2 > 0 ? y1 - th - 2 : y1;
        ctx.fillStyle = '#b42318';
        ctx.fillRect(x1, ly, tw, th);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, x1 + 6, ly + 15);
      });
      setReady(true);
    };
  }, [imageUrl, detections, imageWidth, imageHeight]);

  return (
    <div className="rounded-[14px] overflow-hidden border bg-[var(--cs-bg-accent)]" style={{ borderColor: 'var(--cs-border)' }}>
      <canvas
        ref={canvasRef}
        className="w-full h-auto max-h-[520px] object-contain"
        style={{ opacity: ready ? 1 : 0.4 }}
        aria-label="Pest detections overlaid on original image"
      />
    </div>
  );
};
