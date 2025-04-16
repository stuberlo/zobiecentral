import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:80',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
       }
    }
  }
});
