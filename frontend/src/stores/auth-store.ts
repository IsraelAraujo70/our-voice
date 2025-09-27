import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, UserRole } from "../types/auth-types";
import { getUserRole } from "../types/auth-types";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  fieldErrors: Record<string, string>;
}

interface AuthActions {
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setFieldErrors: (errors: Record<string, string>) => void;
  clearError: () => void;
  clearFieldError: (field: string) => void;
  clearAllErrors: () => void;
  logout: () => void;
  getRole: () => UserRole;
  isAuthenticated: () => boolean;
  canAccess: (requiredRole: UserRole) => boolean;
}

type AuthStore = AuthState & AuthActions;

const roleHierarchy: Record<UserRole, number> = {
  guest: 0,
  user: 1,
  staff: 2,
  admin: 3,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isLoading: false,
      error: null,
      fieldErrors: {},

      // Actions
      setUser: (user: User) => set({ user }),
      setToken: (token: string) => set({ token }),
      setLoading: (isLoading: boolean) => set({ isLoading }),
      setError: (error: string | null) => set({ error }),
      setFieldErrors: (errors: Record<string, string>) => set({ fieldErrors: errors }),
      clearError: () => set({ error: null }),
      clearFieldError: (field: string) => set((state) => ({
        fieldErrors: Object.fromEntries(
          Object.entries(state.fieldErrors).filter(([key]) => key !== field)
        ),
      })),
      clearAllErrors: () => set({ error: null, fieldErrors: {} }),

      logout: () => set({ user: null, token: null, error: null, fieldErrors: {} }),

      getRole: () => {
        const { user } = get();
        return getUserRole(user);
      },

      isAuthenticated: () => {
        const { user, token } = get();
        return !!(user && token);
      },

      canAccess: (requiredRole: UserRole) => {
        const currentRole = get().getRole();
        return roleHierarchy[currentRole] >= roleHierarchy[requiredRole];
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
);