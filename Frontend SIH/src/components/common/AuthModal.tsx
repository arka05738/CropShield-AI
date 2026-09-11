import React, { useState } from 'react';
import { ShieldCheck, Sprout, X } from 'lucide-react';
import { api } from '../../services/api';
import { User } from '../../types';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: User) => void;
  onRejectNonFarmer?: (message: string) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  onRejectNonFarmer
}) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const acceptFarmerOnly = (user: User): boolean => {
    if (user.role !== 'FARMER') {
      api.logout();
      const message =
        'This portal is for farmers only. Administrators and extension staff should use the Admin portal.';
      setError(message);
      onRejectNonFarmer?.(message);
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (isRegister) {
        const res = await api.register({
          email,
          password,
          full_name: fullName,
          role: 'FARMER'
        });
        if (!acceptFarmerOnly(res.user)) return;
        onSuccess(res.user);
      } else {
        const res = await api.login(email, password);
        if (!acceptFarmerOnly(res.user)) return;
        onSuccess(res.user);
      }
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemo = async () => {
    if (!import.meta.env.DEV) return;
    setError(null);
    setIsLoading(true);
    try {
      const res = await api.login('demo@cropshield.ai', 'cropshield123');
      if (!acceptFarmerOnly(res.user)) return;
      onSuccess(res.user);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Demo login error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-card rounded-3xl max-w-2xl w-full border border-emerald-500/30 overflow-hidden shadow-2xl flex flex-col md:flex-row">
        <div className="w-full md:w-5/12 bg-gradient-to-br from-emerald-950 via-slate-900 to-slate-950 p-6 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center text-slate-950 font-bold">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold text-white font-['Outfit']">
                Crop<span className="text-emerald-400">Shield</span>
              </span>
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Outfit']">Farmer Portal</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Farmer accounts only. Admin users should open the Admin portal instead.
              </p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-2">
            {import.meta.env.DEV ? (
              <button
                type="button"
                onClick={handleQuickDemo}
                className="w-full py-2 px-3 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 font-semibold text-xs border border-emerald-500/30 transition-all flex items-center gap-2"
              >
                <Sprout className="w-3.5 h-3.5 text-emerald-400" />
                <span>Login as Farmer (Demo)</span>
              </button>
            ) : null}
          </div>
        </div>

        <div className="w-full md:w-7/12 p-6 bg-slate-950 relative space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-['Outfit']">
              {isRegister ? 'Create Farmer Profile' : 'Account Authentication'}
            </h3>
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
              <X className="w-4 h-4" />
            </button>
          </div>

          {error && (
            <div className="p-3 bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs rounded-xl">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            {isRegister && (
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>
            )}

            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:outline-none focus:border-emerald-500"
                required
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:outline-none focus:border-emerald-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 transition-all"
            >
              {isLoading
                ? 'Authenticating...'
                : isRegister
                  ? 'Register & Enter Dashboard'
                  : 'Sign In to CropShield'}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => setIsRegister(!isRegister)}
                className="text-xs text-slate-400 hover:text-emerald-400 transition-colors"
              >
                {isRegister ? 'Already registered? Sign In' : 'New farmer? Create an account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
