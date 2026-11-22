import axios from 'axios';
import { create } from 'zustand';
import { getMeApi, loginApi } from '../api/auth';
import {
  registerUnauthorizedHandler,
  TOKEN_STORAGE_KEY,
  USER_STORAGE_KEY,
} from '../api/client';
import type { User } from '../types/auth';

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  refreshProfile: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

function readStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const firstMsg = detail[0]?.msg;
      if (typeof firstMsg === 'string') {
        return firstMsg;
      }
    }
    if (!err.response) {
      return 'Không thể kết nối đến máy chủ SmartSOP API. Vui lòng kiểm tra backend.';
    }
  }
  return 'Đăng nhập thất bại. Vui lòng thử lại.';
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem(TOKEN_STORAGE_KEY),
  user: readStoredUser(),
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await loginApi({ username: username.trim(), password });
      localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data.user));
      set({
        token: data.access_token,
        user: data.user,
        isLoading: false,
        error: null,
      });
      return true;
    } catch (err) {
      set({
        isLoading: false,
        error: extractErrorMessage(err),
      });
      return false;
    }
  },

  refreshProfile: async () => {
    const token = get().token;
    if (!token) return;
    try {
      const user = await getMeApi();
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
      set({ user });
    } catch {
      // 401 is handled by Axios interceptor; transient network errors keep session usable
    }
  },

  logout: () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    set({ token: null, user: null, isLoading: false, error: null });
  },

  clearError: () => set({ error: null }),
}));

registerUnauthorizedHandler(() => {
  useAuthStore.getState().logout();
});
