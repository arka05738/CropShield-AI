import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { ShieldCheck, MapPin, Globe, User as UserIcon, LogOut } from 'lucide-react';
import { LANGUAGES, SupportedLanguage, t } from '../../i18n/translations';
import { User } from '../../types';

interface HeaderProps {
  language: SupportedLanguage;
  onSelectLanguage: (lang: SupportedLanguage) => void;
  user: User | null;
  onLogout: () => void;
  locationName: string;
}

const navItems = [
  { to: '/farmer/dashboard', key: 'nav_dashboard' },
  { to: '/farmer/analyze', key: 'nav_analyze', emphasize: true },
  { to: '/farmer/history', key: 'nav_history' },
  { to: '/farmer/weather', key: 'nav_weather' },
  { to: '/farmer/assistant', key: 'nav_assistant' },
  { to: '/farmer/alerts', key: 'nav_alerts' },
  { to: '/farmer/profile', key: 'nav_profile' }
] as const;

export const Header: React.FC<HeaderProps> = ({
  language,
  onSelectLanguage,
  user,
  onLogout,
  locationName
}) => {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 glass-nav px-4 lg:px-8 py-3 transition-all duration-200">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center justify-between w-full md:w-auto gap-4">
          <button
            type="button"
            onClick={() => navigate('/farmer/dashboard')}
            className="flex items-center gap-2.5 cursor-pointer group text-left"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white font-['Outfit']">
                  Crop<span className="text-emerald-400">Shield</span>
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold tracking-wider bg-emerald-950/80 text-emerald-400 border border-emerald-500/30">
                  AI v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                {t(language, 'farmer_portal')}
              </p>
            </div>
          </button>
        </div>

        <div className="flex items-center gap-1 w-full md:w-auto justify-center overflow-x-auto pb-1 md:pb-0 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `px-3 py-1 text-xs rounded-lg transition-colors whitespace-nowrap ${
                  isActive
                    ? 'emphasize' in item && item.emphasize
                      ? 'bg-emerald-500 text-slate-950 font-bold'
                      : 'bg-emerald-500/20 text-emerald-300 font-medium'
                    : 'emphasize' in item && item.emphasize
                      ? 'text-emerald-400 hover:text-emerald-300'
                      : 'text-slate-400 hover:text-slate-200'
                }`
              }
            >
              {t(language, item.key)}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/60 border border-emerald-500/10 text-xs text-slate-300">
            <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="truncate max-w-[120px]">{locationName}</span>
          </div>

          <div className="relative flex items-center">
            <Globe className="w-3.5 h-3.5 text-slate-400 absolute left-2 pointer-events-none" />
            <select
              value={language}
              onChange={(e) => onSelectLanguage(e.target.value as SupportedLanguage)}
              className="bg-slate-900/80 border border-slate-700 text-xs text-slate-200 pl-7 pr-3 py-1.5 rounded-lg focus:outline-none focus:border-emerald-500 cursor-pointer"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code} className="bg-slate-900 text-slate-200">
                  {lang.nativeLabel} ({lang.label})
                </option>
              ))}
            </select>
          </div>

          {user ? (
            <div className="flex items-center gap-2 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800">
              <button
                type="button"
                onClick={() => navigate('/farmer/profile')}
                className="flex items-center gap-2 text-left"
              >
                <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">
                  {user.full_name.charAt(0)}
                </div>
                <div className="text-left hidden sm:block">
                  <p className="text-xs font-medium text-slate-200 truncate max-w-[90px]">{user.full_name}</p>
                  <p className="text-[10px] text-emerald-400 leading-none">{user.role}</p>
                </div>
              </button>
              <button
                onClick={onLogout}
                title={t(language, 'sign_out')}
                className="text-slate-400 hover:text-red-400 p-1 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="flex items-center gap-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-md shadow-emerald-500/20"
            >
              <UserIcon className="w-3.5 h-3.5" />
              {t(language, 'sign_in')}
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
