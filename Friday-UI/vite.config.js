import { defineConfig } from 'vite';


export default defineConfig({
  server: {
    port: 5173,
  },
  optimizeDeps: {
    exclude: ['onnxruntime-web', 'onnxruntime-web/wasm'],
    esbuildOptions: {
      sourcemap: false,
      external: ['onnxruntime-web', 'onnxruntime-web/wasm']
    }
  }
});
