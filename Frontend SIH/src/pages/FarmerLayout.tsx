import React, { useRef, useState } from 'react';
import { Navigate, Outlet, useNavigate } from 'react-router-dom';
import { FarmerShell } from '../components/farmer/FarmerShell';
import { useFarmerApp } from '../context/FarmerAppContext';
import { api } from '../services/api';
import { AnalysisResponse, PestDetectResponse } from '../types';
import { friendlyApiError } from '../lib/crops';

export type FarmerOutletContext = {
  handleAnalyzeCrop: (file: File, lat: number, lon: number, cropHint?: string) => Promise<void>;
  handleDetectPests: (file: File, cropHint?: string) => Promise<void>;
  handleRequestValidation: (analysisId: string, notes: string) => Promise<void>;
  handleRefreshLocation: () => void;
  isScanning: boolean;
  isPestScanning: boolean;
  scanProgressStep: number;
  pestProgressStep: number;
  scanError: string | null;
  pestError: string | null;
  userLocation: { lat: number; lon: number; name: string };
};

export const FarmerLayout: React.FC = () => {
  const navigate = useNavigate();
  const {
    user,
    logout,
    userLocation,
    setUserLocation,
    setAnalyses,
    setPestAnalyses,
    refreshWeather,
  } = useFarmerApp();

  const [isScanning, setIsScanning] = useState(false);
  const [isPestScanning, setIsPestScanning] = useState(false);
  const [scanProgressStep, setScanProgressStep] = useState(0);
  const [pestProgressStep, setPestProgressStep] = useState(0);
  const [scanError, setScanError] = useState<string | null>(null);
  const [pestError, setPestError] = useState<string | null>(null);
  const timers = useRef<number[]>([]);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const clearTimers = () => {
    timers.current.forEach((id) => window.clearTimeout(id));
    timers.current = [];
  };

  const startHonestProgress = (setter: (n: number) => void) => {
    clearTimers();
    setter(0);
    timers.current.push(window.setTimeout(() => setter(1), 1200));
    timers.current.push(window.setTimeout(() => setter(2), 2800));
  };

  const handleRefreshLocation = () => {
    if (!('geolocation' in navigator)) return;
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        setUserLocation({ lat, lon, name: 'Current field location' });
        await refreshWeather(lat, lon);
      },
      () => undefined
    );
  };

  const handleAnalyzeCrop = async (file: File, lat: number, lon: number, cropHint?: string) => {
    setIsScanning(true);
    setScanError(null);
    startHonestProgress(setScanProgressStep);
    try {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('latitude', lat.toString());
      fd.append('longitude', lon.toString());
      if (cropHint) fd.append('crop_hint', cropHint);
      const result = await api.runDiagnosis(fd);
      clearTimers();
      if (result.status === 'rejected') {
        const rej = result as { status: 'rejected'; message: string; suggestions?: string[] };
        setScanError(rej.message || 'Image was rejected. Please use a clear crop leaf photo.');
        return;
      }
      const fullReport = result as AnalysisResponse;
      setAnalyses((prev) => [fullReport, ...prev]);
      navigate(`/farmer/reports/${fullReport.id}`, { state: { analysis: fullReport } });
    } catch (err) {
      clearTimers();
      setScanError(friendlyApiError(err));
      throw err;
    } finally {
      setIsScanning(false);
    }
  };

  const handleDetectPests = async (file: File, cropHint?: string) => {
    setIsPestScanning(true);
    setPestError(null);
    startHonestProgress(setPestProgressStep);
    try {
      const fd = new FormData();
      fd.append('file', file);
      if (cropHint) fd.append('crop_hint', cropHint);
      const result: PestDetectResponse = await api.detectPests(fd);
      clearTimers();
      setPestAnalyses((prev) => [result, ...prev]);
      navigate(`/farmer/pest-reports/${result.id}`, { state: { pest: result } });
    } catch (err) {
      clearTimers();
      setPestError(friendlyApiError(err));
      throw err;
    } finally {
      setIsPestScanning(false);
    }
  };

  const handleRequestValidation = async (analysisId: string, notes: string) => {
    await api.requestValidation(analysisId, notes);
  };

  // silence unused logout lint in layout — logout is in shell
  void logout;

  return (
    <FarmerShell>
      <Outlet
        context={
          {
            handleAnalyzeCrop,
            handleDetectPests,
            handleRequestValidation,
            handleRefreshLocation,
            isScanning,
            isPestScanning,
            scanProgressStep,
            pestProgressStep,
            scanError,
            pestError,
            userLocation,
          } satisfies FarmerOutletContext
        }
      />
    </FarmerShell>
  );
};
