"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { AuthService } from "@/lib/auth-service";
import type { UserRole } from "@/types/auth-types";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  redirectTo?: string;
  showLoginModal?: boolean;
}

export function ProtectedRoute({
  children,
  requiredRole = "user",
  redirectTo = "/",
  showLoginModal = false,
}: ProtectedRouteProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const { canAccess, token } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        await AuthService.initializeAuth();
      }
      setIsInitialized(true);
    };

    initAuth();
  }, [token]);

  useEffect(() => {
    if (!isInitialized) return;

    const hasAccess = canAccess(requiredRole);

    if (!hasAccess) {
      if (showLoginModal) {
        // TODO: Show login modal instead of redirecting
        console.log("Should show login modal");
      } else {
        // Store intended destination for after login
        sessionStorage.setItem("auth-redirect", pathname);
        router.push(redirectTo);
      }
    }
  }, [isInitialized, canAccess, requiredRole, showLoginModal, redirectTo, pathname, router]);

  // Show loading state while checking authentication
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900" />
      </div>
    );
  }

  // Check if user has required access level
  if (!canAccess(requiredRole)) {
    return null; // Will redirect or show modal via useEffect
  }

  return <>{children}</>;
}

// Convenience components for specific roles
export function UserRoute({ children, ...props }: Omit<ProtectedRouteProps, "requiredRole">) {
  return (
    <ProtectedRoute requiredRole="user" {...props}>
      {children}
    </ProtectedRoute>
  );
}

export function StaffRoute({ children, ...props }: Omit<ProtectedRouteProps, "requiredRole">) {
  return (
    <ProtectedRoute requiredRole="staff" {...props}>
      {children}
    </ProtectedRoute>
  );
}

export function AdminRoute({ children, ...props }: Omit<ProtectedRouteProps, "requiredRole">) {
  return (
    <ProtectedRoute requiredRole="admin" {...props}>
      {children}
    </ProtectedRoute>
  );
}