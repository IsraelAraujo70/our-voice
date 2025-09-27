"use client";

import { useAuth } from "@/hooks/use-auth";
import { AuthModal } from "@/components/auth/auth-modal";
import { Button } from "@/components/ui/button";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { user, logout, isAuthenticated, getRole } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  const userRole = getRole();
  const isAuth = isAuthenticated();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">OUR Voice</h1>
            {isAuth && (
              <span className="text-sm text-gray-500">
                Welcome, @{user?.handle}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuth ? (
              <>
                <span className="text-xs px-2 py-1 bg-gray-100 rounded-full">
                  {userRole}
                </span>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <AuthModal>
                <Button variant="outline" size="sm">
                  Login
                </Button>
              </AuthModal>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  );
}