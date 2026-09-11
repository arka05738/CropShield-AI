import React, { useState, useRef } from 'react';
import { 
  UploadCloud, Camera, Image as ImageIcon, Sparkles, 
  MapPin, CheckCircle2, RefreshCw, AlertCircle 
} from 'lucide-react';

interface ImageUploaderProps {
  onAnalyze: (file: File, lat: number, lon: number, cropHint?: string) => void;
  isLoading: boolean;
  userLocation: { lat: number; lon: number; name: string };
  onRefreshLocation: () => void;
}

// Benchmark demo cases with verified crop imagery
const SAMPLE_CASES = [
  {
    label: "Tomato Early Blight + Aphids",
    crop: "Tomato",
    url: "https://images.unsplash.com/photo-1592878904946-b3cd8ae243d0?auto=format&fit=crop&w=800&q=80",
    desc: "Target-board foliar spots with vector clusters"
  },
  {
    label: "Rice Blast + Stem Borer",
    crop: "Rice",
    url: "https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=800&q=80",
    desc: "Spindle shaped lesions on paddy tillers"
  },
  {
    label: "Cotton Leaf Curl & Bollworm",
    crop: "Cotton",
    url: "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=800&q=80",
    desc: "Upward foliar cupping & square damage"
  },
  {
    label: "Healthy Wheat Canopy",
    crop: "Wheat",
    url: "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80",
    desc: "Vigorous green tillers with zero necrosis"
  }
];

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onAnalyze,
  isLoading,
  userLocation,
  onRefreshLocation
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [cropHint, setCropHint] = useState<string>('Tomato');
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // File Handling
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    stopCamera();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  // Camera Capture
  const startCamera = async () => {
    try {
      setIsCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera access error:", err);
      alert("Could not access camera. Please verify device permissions or upload a photo.");
      setIsCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    setIsCameraActive(false);
  };

  const snapPhoto = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
        processFile(file);
      }
    }, 'image/jpeg', 0.95);
  };

  // Sample Benchmark Selector
  const loadSampleCase = async (sample: typeof SAMPLE_CASES[0]) => {
    try {
      const response = await fetch(sample.url);
      const blob = await response.blob();
      const file = new File([blob], `${sample.crop.toLowerCase()}_sample.jpg`, { type: 'image/jpeg' });
      setCropHint(sample.crop);
      processFile(file);
    } catch (err) {
      console.error("Failed to load sample image:", err);
    }
  };

  const handleSubmit = () => {
    if (!selectedFile) return;
    onAnalyze(selectedFile, userLocation.lat, userLocation.lon, cropHint);
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      
      {/* SoilzePro Header Card */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden border border-emerald-500/20">
        <div className="absolute -right-16 -top-16 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                <Sparkles className="w-3.5 h-3.5" /> AI Diagnostic Lab
              </span>
              <span className="text-xs text-slate-400">Zero-Shot Gatekeeper & YOLOv8 Engine</span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight font-['Outfit']">
              Scan & Diagnose Crop Health
            </h2>
            <p className="text-sm text-slate-400 max-w-xl">
              Upload a clear photo of an infected crop leaf or stem. The gatekeeper verifies plant tissue before executing multi-pathogen vision inference and ICAR RAG synthesis.
            </p>
          </div>

          {/* Location Chip with Refresh */}
          <div className="flex items-center gap-2 bg-slate-950/70 px-3.5 py-2 rounded-xl border border-slate-800 text-xs text-slate-300">
            <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <p className="font-semibold text-white">{userLocation.name}</p>
              <p className="text-[10px] text-slate-400 font-mono">
                {userLocation.lat.toFixed(4)}° N, {userLocation.lon.toFixed(4)}° E
              </p>
            </div>
            <button 
              onClick={onRefreshLocation}
              title="Update GPS Location"
              className="ml-2 text-slate-400 hover:text-emerald-400 transition-colors p-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Upload Dropzone or Camera Stream */}
      <div 
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`glass-card rounded-2xl p-8 border-2 border-dashed transition-all text-center relative ${
          isDragging 
            ? 'border-emerald-400 bg-emerald-950/20 scale-[1.01]' 
            : 'border-emerald-500/25 hover:border-emerald-500/50'
        }`}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          accept="image/jpeg,image/png,image/webp" 
          onChange={handleFileChange} 
          className="hidden" 
        />

        {/* Live Video Camera Mode */}
        {isCameraActive ? (
          <div className="space-y-4 max-w-lg mx-auto">
            <div className="relative rounded-2xl overflow-hidden border border-emerald-500/30 bg-black aspect-video flex items-center justify-center">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-x-0 bottom-3 flex items-center justify-center gap-4">
                <button
                  onClick={snapPhoto}
                  className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow-xl shadow-emerald-500/30 transition-all flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" /> Capture Photo
                </button>
                <button
                  onClick={stopCamera}
                  className="px-4 py-2.5 rounded-xl bg-slate-900/90 text-slate-300 hover:text-white text-sm border border-slate-700 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
            <p className="text-xs text-slate-400">Position the infected leaf within center frame with steady focus</p>
          </div>
        ) : previewUrl ? (
          /* Image Preview Mode */
          <div className="space-y-5 max-w-md mx-auto">
            <div className="relative rounded-2xl overflow-hidden border border-emerald-500/30 group">
              <img 
                src={previewUrl} 
                alt="Selected crop preview" 
                className="w-full h-64 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent flex items-end justify-between p-4">
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 bg-slate-950/80 px-3 py-1 rounded-lg">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Photo Ready
                </span>
                <button
                  onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                  className="text-xs bg-slate-900/90 hover:bg-red-500/20 text-slate-300 hover:text-red-300 px-3 py-1 rounded-lg border border-slate-700 transition-colors"
                >
                  Change Photo
                </button>
              </div>
            </div>

            {/* Optional Crop Hint Picker */}
            <div className="flex items-center justify-center gap-3 text-xs text-slate-300">
              <span className="text-slate-400">Crop Type:</span>
              <select
                value={cropHint}
                onChange={(e) => setCropHint(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-emerald-400 font-semibold px-3 py-1.5 rounded-lg focus:outline-none focus:border-emerald-500"
              >
                {['Tomato', 'Rice', 'Wheat', 'Potato', 'Cotton', 'Maize', 'Sugarcane', 'Soybean', 'Chilli'].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Main CTA Button */}
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className={`w-full py-3.5 px-6 rounded-xl font-bold text-sm text-slate-950 shadow-xl transition-all flex items-center justify-center gap-2 ${
                isLoading 
                  ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-emerald-400 to-emerald-500 hover:from-emerald-300 hover:to-emerald-400 shadow-emerald-500/25 hover:scale-[1.02]'
              }`}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                  Running AI Vision & RAG Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Analyze Crop Health Now
                </>
              )}
            </button>
          </div>
        ) : (
          /* Empty State Dropzone */
          <div className="space-y-4 py-4">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto text-emerald-400 shadow-lg shadow-emerald-500/10">
              <UploadCloud className="w-8 h-8 stroke-[1.75]" />
            </div>

            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white font-['Outfit']">
                Drag and drop your crop photo here
              </h3>
              <p className="text-xs text-slate-400">
                Supports JPG, JPEG, PNG, or WebP (max 15MB)
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 transition-all flex items-center gap-2"
              >
                <ImageIcon className="w-4 h-4" /> Browse Gallery
              </button>
              <button
                type="button"
                onClick={startCamera}
                className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 font-semibold text-xs border border-slate-700 transition-all flex items-center gap-2"
              >
                <Camera className="w-4 h-4 text-emerald-400" /> Open Mobile Camera
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Benchmark Sample Case Selector */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-300 font-['Outfit']">
              Try Benchmark Test Scenarios
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
              1-Click Demo Scenarios
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {SAMPLE_CASES.map((sample, idx) => (
            <div
              key={idx}
              onClick={() => loadSampleCase(sample)}
              className="group cursor-pointer rounded-xl p-2.5 bg-slate-950/60 border border-slate-800/80 hover:border-emerald-500/40 transition-all hover:scale-[1.02] flex items-center gap-3"
            >
              <img 
                src={sample.url} 
                alt={sample.label} 
                className="w-12 h-12 rounded-lg object-cover border border-slate-800 group-hover:border-emerald-500/40"
              />
              <div className="text-left overflow-hidden">
                <p className="text-xs font-bold text-white group-hover:text-emerald-400 transition-colors truncate">
                  {sample.label}
                </p>
                <p className="text-[11px] text-slate-400 truncate">
                  {sample.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
