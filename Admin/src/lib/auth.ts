import type { User, UserRole } from '../types';
import { ADMIN_ALLOWED_ROLES } from '../types';

export const TOKEN_KEY = 'cropshield_admin_token';
export const USER_KEY = 'cropshield_admin_user';

export function isAdminRole(role: string | undefined | null): role is UserRole {
  return !!role && (ADMIN_ALLOWED_ROLES as string[]).includes(role);
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function setAuthSession(token: string, user: User): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getApiBase(): string {
  const configured = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/$/, '');
  if (!configured) return '/api/v1';
  if (configured.endsWith('/api/v1')) return configured;
  return `${configured}/api/v1`;
}
