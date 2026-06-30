import { create } from "zustand";
import { authApi } from "../services/authApi";
import type { User } from "../types";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  loading: boolean;

  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, inviteCode: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
  init: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("token"),
  isAuthenticated: false,
  isAdmin: false,
  loading: true,

  login: async (username, password) => {
    const res = await authApi.login({ username, password });
    const { access_token, user } = res.data;
    localStorage.setItem("token", access_token);
    set({
      token: access_token,
      user,
      isAuthenticated: true,
      isAdmin: user.role === "admin",
    });
  },

  register: async (username, password, inviteCode) => {
    const res = await authApi.register({ username, password, invite_code: inviteCode });
    const { access_token, user } = res.data;
    localStorage.setItem("token", access_token);
    set({
      token: access_token,
      user,
      isAuthenticated: true,
      isAdmin: user.role === "admin",
    });
  },

  logout: () => {
    localStorage.removeItem("token");
    set({
      token: null,
      user: null,
      isAuthenticated: false,
      isAdmin: false,
    });
  },

  fetchMe: async () => {
    try {
      const res = await authApi.me();
      set({
        user: res.data,
        isAuthenticated: true,
        isAdmin: res.data.role === "admin",
      });
    } catch {
      get().logout();
    }
  },

  init: async () => {
    const token = localStorage.getItem("token");
    if (token) {
      set({ token, loading: true });
      await get().fetchMe();
    }
    set({ loading: false });
  },
}));
