'use client';

import { MainLayout } from "@/components/layout/main-layout";

export default function Home() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold text-gray-900">Feed Principal</h2>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600">
            Bem-vindo ao OUR Voice! Este é o layout principal da aplicação SPA.
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
