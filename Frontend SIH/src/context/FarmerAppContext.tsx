import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import { AnalysisResponse, PestDetectResponse, User, WeatherMetrics } from '../types';
import { SupportedLanguage } from '../i18n/translations';

interface FarmerAppContextValue {
  user: User | null;
  setUser: (user: User | null) => void;
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  userLocation: { lat: number; lon: number; name: string };
  setUserLocation: (loc: { lat: number; lon: number; name: string }) => void;
  analyses: AnalysisResponse[];
  setAnalyses: React.Dispatch<React.SetStateAction<AnalysisResponse[]>>;
  pestAnalyses: PestDetectResponse[];
  setPestAnalyses: React.Dispatch<React.SetStateAction<PestDetectResponse[]>>;
  weather: WeatherMetrics | null;
  setWeather: React.Dispatch<React.SetStateAction<WeatherMetrics | null>>;
  refreshHistory: () => Promise<void>;
  refreshPestHistory: () => Promise<void>;
  refreshWeather: (lat?: number, lon?: number) => Promise<void>;
  logout: () => void;
  acceptFarmerUser: (user: User) => { ok: boolean; message?: string };
}

const FarmerAppContext = createContext<FarmerAppContextValue | null>(null);

export function useFarmerApp(): FarmerAppContextValue {
  const ctx = useContext(FarmerAppContext);
  if (!ctx) throw new Error('useFarmerApp must be used within FarmerAppProvider');
  return ctx;
}

function isFarmerRole(role: string): boolean {
  return role === 'FARMER';
}

export const FarmerAppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [language, setLanguage] = useState<SupportedLanguage>('en');
  const [userLocation, setUserLocation] = useState({
    lat: 19.9975,
    lon: 73.7898,
    name: 'Nashik, Maharashtra',
  });
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const [pestAnalyses, setPestAnalyses] = useState<PestDetectResponse[]>([]);
  const [weather, setWeather] = useState<WeatherMetrics | null>(null);

  const logout = useCallback(() => {
    api.logout();
    setUser(null);
    setAnalyses([]);
    setPestAnalyses([]);
    setWeather(null);
  }, []);

  const acceptFarmerUser = useCallback((u: User): { ok: boolean; message?: string } => {
    if (!isFarmerRole(u.role)) {
      api.logout();
      return {
        ok: false,
        message:
          'This portal is for farmers only. Administrators and extension staff should use the Admin portal.',
      };
    }
    setUser(u);
    return { ok: true };
  }, []);

  const refreshHistory = useCallback(async () => {
    const historyData = await api.getHistory().catch(() => []);
    setAnalyses(historyData);
  }, []);

  const refreshPestHistory = useCallback(async () => {
    const rows = await api.getPestHistory().catch(() => []);
    setPestAnalyses(rows);
  }, []);

  const refreshWeather = useCallback(
    async (lat?: number, lon?: number) => {
      const la = lat ?? userLocation.lat;
      const lo = lon ?? userLocation.lon;
      try {
        const w = await api.getWeather(la, lo);
        setWeather(w);
      } catch {
        setWeather(null);
      }
    },
    [userLocation.lat, userLocation.lon]
  );

  useEffect(() => {
    const savedUser = localStorage.getItem('cropshield_user');
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser) as User;
        if (isFarmerRole(parsed.role)) {
          setUser(parsed);
        } else {
          api.logout();
        }
      } catch {
        api.logout();
      }
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    refreshHistory();
    refreshPestHistory();
    refreshWeather();
  }, [user, refreshHistory, refreshPestHistory, refreshWeather]);

  const value = useMemo(
    () => ({
      user,
      setUser,
      language,
      setLanguage,
      userLocation,
      setUserLocation,
      analyses,
      setAnalyses,
      pestAnalyses,
      setPestAnalyses,
      weather,
      setWeather,
      refreshHistory,
      refreshPestHistory,
      refreshWeather,
      logout,
      acceptFarmerUser,
    }),
    [
      user,
      language,
      userLocation,
      analyses,
      pestAnalyses,
      weather,
      refreshHistory,
      refreshPestHistory,
      refreshWeather,
      logout,
      acceptFarmerUser,
    ]
  );

  return <FarmerAppContext.Provider value={value}>{children}</FarmerAppContext.Provider>;
};
