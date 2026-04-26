import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      '/api':          'http://localhost:8000',
      '/analyze':      'http://localhost:8000',
      '/session':      'http://localhost:8000',
      '/cover-letter': 'http://localhost:8000',
      '/alerts':       'http://localhost:8000',
      '/inbox':        'http://localhost:8000',
      '/health':       'http://localhost:8000',
      '/history':      'http://localhost:8000',
      '/db':           'http://localhost:8000',
    },
  },
})
