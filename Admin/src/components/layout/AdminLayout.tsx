import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ClipboardList,
  Leaf,
  Bug,
  Users,
  Cpu,
  UserCircle,
  LogOut,
  Shield,
  Menu,
  X,
} from 'lucide-react';
import { api } from '../../services/api';
import { getStoredUser } from '../../lib/auth';

const NAV = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/admin/cases', label: 'Cases', icon: ClipboardList },
  { to: '/admin/disease-cases', label: 'Disease Cases', icon: Leaf },
  { to: '/admin/pest-cases', label: 'Pest Cases', icon: Bug },
  { to: '/admin/farmers', label: 'Farmers', icon: Users },
  { to: '/admin/models', label: 'Models', icon: Cpu },
  { to: '/admin/profile', label: 'Profile', icon: UserCircle },
];

export function AdminLayout() {
  const navigate = useNavigate();
  const user = getStoredUser();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    api.logout();
    navigate('/login', { replace: true });
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex min-h-11 items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-colors ${
      isActive
        ? 'bg-green-700/40 font-semibold text-white'
        : 'text-stone-300 hover:bg-white/5 hover:text-white'
    }`;

  const sidebar = (
    <>
      <div className="border-b border-white/10 px-5 py-5">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-700/40 text-green-200" aria-hidden>
            <Shield className="h-5 w-5" />
          </span>
          <div>
            <p className="font-[family-name:var(--font-heading)] text-lg font-semibold tracking-tight text-white">
              CropShield
            </p>
            <p className="text-[11px] uppercase tracking-[0.14em] text-green-200/70">Admin Console</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4" aria-label="Primary">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={navLinkClass}
            onClick={() => setMobileOpen(false)}
          >
            <Icon className="h-4 w-4 shrink-0 opacity-80" aria-hidden />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-white/10 px-4 py-4">
        <p className="truncate text-sm font-medium text-white">{user?.full_name || 'Operator'}</p>
        <p className="truncate text-xs text-stone-400">{user?.role}</p>
        <button
          type="button"
          onClick={handleLogout}
          className="mt-3 flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-stone-200 hover:bg-white/10"
        >
          <LogOut className="h-3.5 w-3.5" aria-hidden />
          Sign out
        </button>
      </div>
    </>
  );

  return (
    <div className="flex min-h-screen">
      <aside
        className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-stone-200 bg-[var(--color-sidebar)] text-stone-100 lg:flex"
        aria-label="Admin navigation"
      >
        {sidebar}
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="Close menu"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative flex h-full w-[min(18rem,85vw)] flex-col bg-[var(--color-sidebar)] text-stone-100 shadow-xl">
            <button
              type="button"
              className="absolute right-3 top-3 rounded-lg p-2 text-stone-300 hover:bg-white/10"
              aria-label="Close navigation"
              onClick={() => setMobileOpen(false)}
            >
              <X className="h-5 w-5" />
            </button>
            {sidebar}
          </aside>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex min-h-14 items-center justify-between gap-3 border-b border-[var(--color-border)] bg-white/90 px-4 backdrop-blur lg:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-[var(--color-border)] bg-white text-stone-700 lg:hidden"
              aria-label="Open navigation"
              aria-expanded={mobileOpen}
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="lg:hidden">
              <p className="text-sm font-semibold text-stone-900">CropShield Admin</p>
            </div>
            <p className="hidden text-sm text-stone-500 lg:block">
              Agricultural AI monitoring — live backend data only
            </p>
          </div>
          <div className="text-right text-xs text-stone-500">
            <span className="hidden sm:inline">{user?.email}</span>
            <span className="ml-2 rounded border border-stone-200 bg-stone-50 px-2 py-0.5 font-semibold text-stone-700">
              {user?.role}
            </span>
          </div>
        </header>

        <main className="min-w-0 flex-1 overflow-x-hidden p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
