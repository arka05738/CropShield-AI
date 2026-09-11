import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { AdminLayout } from './components/layout/AdminLayout';
import { getStoredToken, getStoredUser, isAdminRole } from './lib/auth';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage, DiseaseCasesPage, PestCasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { FarmersPage } from './pages/FarmersPage';
import { ModelsPage } from './pages/ModelsPage';
import { ProfilePage } from './pages/ProfilePage';
import { UnauthorizedState } from './components/ui/States';

function RequireAdmin() {
  const token = getStoredToken();
  const user = getStoredUser();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (!user || !isAdminRole(user.role)) {
    return <UnauthorizedState />;
  }
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      <Route element={<RequireAdmin />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="cases" element={<CasesPage />} />
          <Route path="cases/:kind/:id" element={<CaseDetailPage />} />
          <Route path="disease-cases" element={<DiseaseCasesPage />} />
          <Route path="pest-cases" element={<PestCasesPage />} />
          <Route path="farmers" element={<FarmersPage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          {/* Legacy redirects — pages removed from primary IA */}
          <Route path="users" element={<Navigate to="/admin/farmers" replace />} />
          <Route path="analyses" element={<Navigate to="/admin/cases" replace />} />
          <Route path="diseases" element={<Navigate to="/admin/disease-cases" replace />} />
          <Route path="pests" element={<Navigate to="/admin/pest-cases" replace />} />
          <Route path="analytics" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="settings" element={<Navigate to="/admin/profile" replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  );
}
