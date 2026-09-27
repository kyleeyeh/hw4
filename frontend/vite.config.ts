import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API + image requests to the FastAPI backend on :8000 during dev,
// so the frontend can use same-origin relative paths (/api, /media).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
    },
  },
})
