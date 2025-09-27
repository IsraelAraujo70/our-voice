"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { AuthService } from "@/lib/auth-service";
import type { UserRole } from "@/types/auth-types";

export function useAuth() {
  const store = useAuthStore();

  useEffect(() => {
    // Initialize auth when the hook is first used
    AuthService.initializeAuth();
  }, []);

  return {
    ...store,
    login: AuthService.login,
    signup: AuthService.signup,
    logout: AuthService.logout,
  };
}

export function useRequireAuth(requiredRole: UserRole = "user") {
  const { canAccess, isAuthenticated } = useAuth();

  return {
    hasAccess: canAccess(requiredRole),
    isAuthenticated: isAuthenticated(),
    requiredRole,
  };
}