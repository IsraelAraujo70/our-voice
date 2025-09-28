'use client';

import { MainLayout } from "@/components/layout/main-layout";
import { FeedScopeSwitcher } from "@/components/feed/feed-scope-switcher";
import { RealtimeFeed } from "@/components/feed/realtime-feed";
import { GlassCard } from "@/components/ui/glass-card";

export default function Home() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <section className="space-y-6">
            <FeedScopeSwitcher />
            <RealtimeFeed />
          </section>

          <aside className="hidden lg:flex">
            <GlassCard className="h-fit w-full p-6 space-y-4">
              <h3 className="text-lg font-semibold" style={{ color: 'var(--c-content)' }}>
                Descubra novas conexões
              </h3>
              <p className="text-sm" style={{ color: 'color-mix(in srgb, var(--c-content) 70%, transparent)' }}>
                Em breve você verá sugestões personalizadas de pessoas e debates para seguir.
              </p>
            </GlassCard>
          </aside>
        </div>
      </div>
    </MainLayout>
  );
}
