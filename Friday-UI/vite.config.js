import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
  },
  optimizeDeps: {
    // This tells Vite's esbuild not to generate source maps for pre-bundled dependencies like Three.js
    esbuildOptions: {
      sourcemap: false,
    }
  }
});
