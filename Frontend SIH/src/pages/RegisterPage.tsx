import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useFarmerApp } from '../context/FarmerAppContext';
import { friendlyApiError } from '../lib/crops';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { acceptFarmerUser } = useFarmerApp();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const res = await api.register({
        email,
        password,
        full_name: fullName,
        role: 'FARMER',
      });
      const result = acceptFarmerUser(res.user);
      if (!result.ok) {
        setError(result.message || 'Access denied');
        return;
      }
      navigate('/farmer/dashboard', { replace: true });
    } catch (err: unknown) {
      setError(friendlyApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="cs-surface w-full max-w-md p-6 sm:p-8 space-y-6">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--cs-muted)' }}>
            CropShield
          </p>
          <h1 className="text-2xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
            Create farmer account
          </h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="cs-label" htmlFor="name">
              Full name
            </label>
            <input id="name" className="cs-input" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div>
            <label className="cs-label" htmlFor="email">
              Email
            </label>
            <input id="email" className="cs-input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="cs-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              className="cs-input"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && (
            <div className="p-3 rounded-[10px] text-sm" style={{ background: 'var(--cs-danger-soft)', color: 'var(--cs-danger)' }} role="alert">
              {error}
            </div>
          )}
          <button type="submit" className="cs-btn cs-btn-primary w-full" disabled={isLoading}>
            {isLoading ? 'Creating…' : 'Register'}
          </button>
        </form>
        <p className="text-sm text-center" style={{ color: 'var(--cs-muted)' }}>
          Already registered?{' '}
          <Link to="/login" className="font-bold">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};
