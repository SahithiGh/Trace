import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins:[react()],
  server:{
    port:5173,
    proxy:{
      '/api/v1':'http://localhost:8000',
      '/api/hindsight':'http://localhost:8787',
      '/api/health':'http://localhost:8787'
    }
  }
});
