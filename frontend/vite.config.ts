/// <reference types="vitest/config" />
import path from 'node:path'

import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Цель dev-прокси: backend API. Запросы фронта на /api/* проксируются сюда, поэтому
// в деве браузер видит ОДИН origin (Vite) → CORS не нужен вовсе.
const API_TARGET = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:3100'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
