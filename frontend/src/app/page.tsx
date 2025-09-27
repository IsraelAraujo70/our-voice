'use client';

import { MainLayout } from "@/components/layout/main-layout";
import { GlassCard } from "@/components/ui/glass-card";

export default function Home() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold" style={{ color: 'var(--c-content)' }}>Feed Principal</h2>

        <GlassCard>
          <p style={{ color: 'var(--c-content)' }} className="mb-4">
            Bem-vindo ao OUR Voice! Este é o layout principal da aplicação SPA com tema glassmorphism.
          </p>
        </GlassCard>

        <GlassCard>
          <h3 className="text-lg font-semibold mb-3" style={{ color: 'var(--c-content)' }}>Exemplo de Post</h3>
          <p style={{ color: 'color-mix(in srgb, var(--c-content) 80%, transparent)' }} className="mb-4">
            Este é um exemplo de como os posts aparecerão com o novo design glassmorphism.
            O efeito de vidro líquido cria uma sensação moderna e elegante.
          </p>
          <div className="flex gap-3">
            <button className="glass-button-primary">Like</button>
            <button className="glass-button-secondary">Reply</button>
            <button className="glass-button-ghost">Share</button>
          </div>
        </GlassCard>
      </div>
    </MainLayout>
  );
}
