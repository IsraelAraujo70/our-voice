/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts,tsx}'],
    exclude: [
      'node_modules/',
      'src/test/e2e/**',
      '*.config.ts',
      '**/*.d.ts',
      '.next/',
      'public/',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/e2e/**',
        'src/test/setup.ts',
        '*.config.ts',
        '**/*.d.ts',
        '.next/',
        'public/',
      ],
      thresholds: {
        branches: 0,
        functions: 0,
        lines: 0,
        statements: 0
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})