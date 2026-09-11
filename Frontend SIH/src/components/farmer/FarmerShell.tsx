import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Home, Leaf, Bug, History, UserRound, LogOut } from 'lucide-react';
import { useFarmerApp } from '../../context/FarmerAppContext';

const navItems = [
  { to: '/farmer/dashboard', label: 'Home', icon: Home, end: true },
  { to: '/farmer/analyze', label: 'Scan', icon: Leaf, end: false, prominent: true },
  { to: '/farmer/pest-detection', label: 'Pest', icon: Bug, end: false },
  { to: '/farmer/history', label: 'History', icon: History, end: false },
  { to: '/farmer/profile', label: 'Profile', icon: UserRound, end: false },
];

export const FarmerShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useFarmerApp();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col lg:flex-row" style={{ color: 'var(--cs-ink)' }}>
      {/* Desktop sidebar */}
      <aside
        className="hidden lg:flex lg:w-64 xl:w-72 flex-col shrink-0 border-r sticky top-0 h-screen"
        style={{ background: 'var(--cs-surface)', borderColor: 'var(--cs-border)' }}
        aria-label="Main navigation"
      >
        <div className="px-6 py-7 border-b" style={{ borderColor: 'var(--cs-border)' }}>
          <p className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--cs-muted)' }}>
            CropShield
          </p>
          <h1 className="text-2xl font-bold mt-1" style={{ fontFamily: 'var(--font-heading)' }}>
            Farmer
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--cs-muted)' }}>
            {user?.full_name}
          </p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 min-h-[48px] px-4 rounded-[10px] font-semibold text-sm transition-colors ${
                    isActive ? 'text-white' : ''
                  }`
                }
                style={({ isActive }) =>
                  isActive
                    ? { background: 'var(--cs-primary)', color: '#fff' }
                    : { color: 'var(--cs-ink-soft)' }
                }
              >
                <Icon className="w-5 h-5" aria-hidden />
                {item.label}
                {item.prominent && (
                  <span
                    className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full"
                    style={{ background: 'var(--cs-primary-soft)', color: 'var(--cs-primary)' }}
                  >
                    AI
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
        <div className="p-4 border-t" style={{ borderColor: 'var(--cs-border)' }}>
          <button
            type="button"
            className="cs-btn cs-btn-ghost w-full"
            onClick={() => {
              logout();
              navigate('/login', { replace: true });
            }}
          >
            <LogOut className="w-4 h-4" aria-hidden />
            Log out
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header
          className="lg:hidden sticky top-0 z-30 px-4 py-3 border-b flex items-center justify-between"
          style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(8px)', borderColor: 'var(--cs-border)' }}
        >
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider" style={{ color: 'var(--cs-muted)' }}>
              CropShield
            </p>
            <p className="text-sm font-bold">{user?.full_name}</p>
          </div>
          <button
            type="button"
            className="cs-btn cs-btn-ghost min-h-[40px] px-3 text-xs"
            onClick={() => navigate('/farmer/analyze')}
          >
            Scan
          </button>
        </header>

        <main className="flex-1 w-full max-w-5xl mx-auto px-4 py-5 sm:px-6 lg:px-8 pb-28 lg:pb-10">
          {children}
        </main>

        {/* Mobile bottom nav */}
        <nav
          className="lg:hidden fixed bottom-0 inset-x-0 z-40 border-t grid grid-cols-5"
          style={{ background: 'var(--cs-surface)', borderColor: 'var(--cs-border)' }}
          aria-label="Mobile navigation"
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className="flex flex-col items-center justify-center gap-0.5 py-2 min-h-[64px] text-[11px] font-semibold"
                style={({ isActive }) => ({
                  color: isActive ? 'var(--cs-primary)' : 'var(--cs-muted)',
                })}
              >
                <span
                  className={`flex items-center justify-center w-10 h-10 rounded-full ${
                    item.prominent ? 'shadow-sm' : ''
                  }`}
                  style={
                    item.prominent
                      ? { background: 'var(--cs-primary)', color: '#fff', marginTop: '-18px' }
                      : undefined
                  }
                >
                  <Icon className="w-5 h-5" aria-hidden />
                </span>
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </div>
    </div>
  );
};
