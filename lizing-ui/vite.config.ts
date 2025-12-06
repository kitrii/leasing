import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Теперь можно писать import Home from '@/views/Home.vue'
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000', // Проксирование запросов к FastAPI
    },
  },
})
