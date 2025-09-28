"use client";

import { MainHeader } from "@/components/layout/main-header";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="container mx-auto px-4 py-6">
        <MainHeader />

        {/* Main Content */}
        <main>
          {children}
        </main>
      </div>
    </div>
  );
}
