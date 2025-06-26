import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		// Prefer TypeScript files over JavaScript files, but force auth store to .js
		extensions: ['.ts', '.js', '.svelte', '.json'],
		alias: {
			'$lib/stores/auth': './src/lib/stores/auth.js'
		}
	},
	define: {
		// Make build ID available in the frontend
		'import.meta.env.VITE_BUILD_ID': JSON.stringify(process.env.VITE_BUILD_ID || 'dev')
	},
	server: {
		host: '0.0.0.0',
		port: 3000,
		strictPort: true,
		allowedHosts: [
			'localhost',
			'172.30.98.177',
			'dd.kronisto.net',
			'.kronisto.net' // Allow all subdomains
		],
		// Proxy removed for reverse proxy compatibility
		// The reverse proxy will handle /api routing
	},
	build: {
		// Ensure relative paths in production build
		assetsDir: 'assets',
		rollupOptions: {
			output: {
				manualChunks: undefined,
				// Add timestamp for cache busting
				entryFileNames: `assets/[name].${Date.now()}.js`,
				chunkFileNames: `assets/[name].${Date.now()}.js`,
				assetFileNames: `assets/[name].${Date.now()}.[ext]`
			}
		}
	},
	preview: {
		host: '0.0.0.0',
		port: 1717,
		strictPort: true
	}
});