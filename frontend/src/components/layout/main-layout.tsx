"use client";

import { useAuth } from "@/hooks/use-auth";
import { AuthModal } from "@/components/auth/auth-modal";
import { Button } from "@/components/ui/button";
import { ClientOnly } from "@/components/ui/client-only";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { user, logout, isAuthenticated, getRole } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="container mx-auto px-4 py-6">
        <header className="glass-card px-4 py-3 mb-6">
          <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold" style={{ color: 'var(--c-content)' }}>OUR Voice</h1>
            <ClientOnly>
              {isAuthenticated() && (
                <span className="text-sm" style={{ color: 'color-mix(in srgb, var(--c-content) 70%, transparent)' }}>
                  Welcome, @{user?.handle}
                </span>
              )}
            </ClientOnly>
          </div>

          <div className="flex items-center space-x-4">
            <ClientOnly
              fallback={
                <Button variant="secondary" size="sm" disabled>
                  Loading...
                </Button>
              }
            >
              {isAuthenticated() ? (
                <>
                  <span className="text-xs px-3 py-1.5 glass-button-secondary rounded-full">
                    {getRole()}
                  </span>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    Logout
                  </Button>
                </>
              ) : (
                <AuthModal>
                  <Button variant="secondary" size="sm">
                    Login
                  </Button>
                </AuthModal>
              )}
            </ClientOnly>
          </div>
          </div>
        </header>

        {/* Main Content */}
        <main>
          {children}
        </main>
      </div>
    </div>
  );
}