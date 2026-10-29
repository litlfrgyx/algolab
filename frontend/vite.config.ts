import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Pri vývoji presmeruje /api na backend, takže frontend aj API sú na jednej adrese
// rovnako ako po nasadení na Vercel.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: process.env.VITE_API_PROXY ?? 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 900,
  },
})
