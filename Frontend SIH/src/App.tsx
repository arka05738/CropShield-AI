import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { FarmerAppProvider, useFarmerApp } from './context/FarmerAppContext';
import { FarmerLayout } from './pages/FarmerLayout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import {
  AnalyzePage,
  AlertsPage,
  AssistantPage,
  DashboardPage,
  HistoryPage,
  PestDetectionPage,
  PestReportPage,
  ProfilePage,
  ReportPage,
  WeatherPage,
} from './pages/FarmerPages';

function RootRedirect() {
  const { user } = useFarmerApp();
  return <Navigate to={user ? '/farmer/dashboard' : '/login'} replace />;
}

function AuthRedirect({ children }: { children: React.ReactNode }) {
  const { user } = useFarmerApp();
  if (user) return <Navigate to="/farmer/dashboard" replace />;
  return <>{children}</>;
}

export function App() {
  return (
    <BrowserRouter>
      <FarmerAppProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route
            path="/login"
            element={
              <AuthRedirect>
                <LoginPage />
              </AuthRedirect>
            }
          />
          <Route
            path="/register"
            element={
              <AuthRedirect>
                <RegisterPage />
              </AuthRedirect>
            }
          />
          <Route path="/farmer" element={<FarmerLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="analyze" element={<AnalyzePage />} />
            <Route path="pest-detection" element={<PestDetectionPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="reports/:id" element={<ReportPage />} />
            <Route path="pest-reports/:id" element={<PestReportPage />} />
            <Route path="weather" element={<WeatherPage />} />
            <Route path="assistant" element={<AssistantPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </FarmerAppProvider>
    </BrowserRouter>
  );
}

export default App;
