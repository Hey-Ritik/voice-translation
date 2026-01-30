import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Use 127.0.0.1 (IPv4) so proxy works when localhost resolves to ::1 (IPv6)
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true },
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/languages': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/health': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
});
