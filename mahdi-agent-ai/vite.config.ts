import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: '.',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
    chunkSizeWarningLimit: 1200,
  },
  server: {
    allowedHosts: true,
    host: '0.0.0.0',
    watch: {
      // Agent-generated project files and stored data must never trigger a page reload.
      ignored: ['**/data/**', '**/dist/**', '**/node_modules/**', '**/server/**', '**/templates/**'],
    },
  },
});
