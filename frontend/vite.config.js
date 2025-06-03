import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 3000,
		strictPort: true,
		proxy: {
			'/api': {
				target: 'http://172.30.98.21:8000',
				changeOrigin: true,
				secure: false
			}
		}
	}
});