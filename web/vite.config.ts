import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const backendTarget = 'http://127.0.0.1:5000'

const createProxyOptions = () => ({
  target: backendTarget,
  changeOrigin: true,
  configure: (proxy: any) => {
    proxy.on('error', (_err: any, _req: any, res: any) => {
      if (res && !res.headersSent && typeof res.writeHead === 'function') {
        res.writeHead(503, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ status: 'offline', message: 'Backend MetalSense offline (inicie com: python api.py)' }))
      }
    })
  },
})

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': createProxyOptions(),
      '/health': createProxyOptions(),
      '/ready': createProxyOptions(),
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
