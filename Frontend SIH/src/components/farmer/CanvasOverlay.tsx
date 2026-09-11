import React, { useRef, useEffect, useState } from 'react';
import { PestDetectionItem } from '../../types';
import { Eye, ShieldAlert, Bug } from 'lucide-react';

interface CanvasOverlayProps {
  imageUrl: string;
  pests: PestDetectionItem[];
  cropName: string;
  onSelectPest?: (pest: PestDetectionItem | null) => void;
}

export const CanvasOverlay: React.FC<CanvasOverlayProps> = ({
  imageUrl,
  pests,
  cropName,
  onSelectPest
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hoveredPest, setHoveredPest] = useState<PestDetectionItem | null>(null);
  const [imageLoaded, setImageLoaded] = useState<boolean>(false);
  const imageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageUrl;
    img.onload = () => {
      imageRef.current = img;
      setImageLoaded(true);
      drawCanvas(null);
    };
  }, [imageUrl, pests]);

  const drawCanvas = (activePest: PestDetectionItem | null) => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas dimensions to match image resolution
    canvas.width = img.naturalWidth || 800;
    canvas.height = img.naturalHeight || 600;

    // 1. Draw base image
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // 2. Draw bounding boxes
    pests.forEach((pest) => {
      const isHovered = activePest?.name === pest.name;
      const x = pest.bbox.x * canvas.width;
      const y = pest.bbox.y * canvas.height;
      const w = pest.bbox.width * canvas.width;
      const h = pest.bbox.height * canvas.height;

      // Color scheme based on pest severity
      let strokeColor = '#f59e0b'; // Amber
      let fillColor = 'rgba(245, 158, 11, 0.15)';
      if (pest.severity === 'Severe' || pest.severity === 'High') {
        strokeColor = '#ef4444'; // Red
        fillColor = 'rgba(239, 68, 68, 0.20)';
      } else if (pest.severity === 'Low') {
        strokeColor = '#10b981'; // Emerald
        fillColor = 'rgba(16, 185, 129, 0.15)';
      }

      if (isHovered) {
        strokeColor = '#38bdf8'; // Sky blue highlight
        fillColor = 'rgba(56, 189, 248, 0.35)';
      }

      // Box outline
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = isHovered ? 4 : 2.5;
      ctx.strokeRect(x, y, w, h);

      // Shaded fill
      ctx.fillStyle = fillColor;
      ctx.fillRect(x, y, w, h);

      // Corner accent brackets
      const cornerLen = Math.min(16, w / 4, h / 4);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 3;
      // Top-Left
      ctx.beginPath();
      ctx.moveTo(x, y + cornerLen);
      ctx.lineTo(x, y);
      ctx.lineTo(x + cornerLen, y);
      ctx.stroke();
      // Top-Right
      ctx.beginPath();
      ctx.moveTo(x + w - cornerLen, y);
      ctx.lineTo(x + w, y);
      ctx.lineTo(x + w, y + cornerLen);
      ctx.stroke();

      // Label background pill
      const labelText = `${pest.name} (${Math.round(pest.confidence * 100)}%)`;
      ctx.font = 'bold 14px Outfit, sans-serif';
      const textMetrics = ctx.measureText(labelText);
      const textWidth = textMetrics.width;
      const textHeight = 22;

      ctx.fillStyle = isHovered ? '#0284c7' : strokeColor;
      ctx.beginPath();
      ctx.roundRect(x, y - textHeight - 2 > 0 ? y - textHeight - 2 : y, textWidth + 16, textHeight, 4);
      ctx.fill();

      // Label text
      ctx.fillStyle = '#ffffff';
      ctx.fillText(labelText, x + 8, y - textHeight - 2 > 0 ? y - 6 : y + 16);
    });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || pests.length === 0) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    // Check if mouse hits any bounding box
    const found = pests.find((p) => {
      const x = p.bbox.x * canvas.width;
      const y = p.bbox.y * canvas.height;
      const w = p.bbox.width * canvas.width;
      const h = p.bbox.height * canvas.height;
      return mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
    });

    if (found !== hoveredPest) {
      setHoveredPest(found || null);
      if (onSelectPest) onSelectPest(found || null);
      drawCanvas(found || null);
    }
  };

  const handleMouseLeave = () => {
    setHoveredPest(null);
    if (onSelectPest) onSelectPest(null);
    drawCanvas(null);
  };

  return (
    <div ref={containerRef} className="relative rounded-2xl overflow-hidden glass-card border border-emerald-500/20 shadow-2xl">
      {/* Top Banner Tag */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-emerald-500/30 text-xs font-semibold text-emerald-400">
        <Bug className="w-4 h-4 text-emerald-400 animate-pulse" />
        <span>YOLOv8 Pest Visualizer</span>
        <span className="text-slate-400 font-normal">| {cropName}</span>
      </div>

      {pests.length > 0 && (
        <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-red-950/80 backdrop-blur-md px-3 py-1 rounded-lg border border-red-500/30 text-xs font-bold text-red-400">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>{pests.length} Cluster{pests.length > 1 ? 's' : ''} Detected</span>
        </div>
      )}

      {/* Responsive Canvas */}
      <div className="flex justify-center items-center bg-slate-950 min-h-[300px]">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="w-full h-auto max-h-[480px] object-contain cursor-crosshair transition-opacity duration-300"
          style={{ opacity: imageLoaded ? 1 : 0.4 }}
        />
      </div>

      {/* Bottom Interactive Pest Selector Chips */}
      <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-medium">Interactive Targets:</span>
          {pests.length === 0 ? (
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              ✓ No pest vectors detected on foliage
            </span>
          ) : (
            pests.map((pest, idx) => (
              <button
                key={idx}
                onMouseEnter={() => {
                  setHoveredPest(pest);
                  drawCanvas(pest);
                }}
                onMouseLeave={handleMouseLeave}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  hoveredPest?.name === pest.name
                    ? 'bg-sky-500 text-slate-950 font-bold scale-105'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {pest.name} ({Math.round(pest.confidence * 100)}%)
              </button>
            ))
          )}
        </div>
        <span className="text-[11px] text-slate-400 italic">
          Hover box to inspect normalized coordinates
        </span>
      </div>
    </div>
  );
};
