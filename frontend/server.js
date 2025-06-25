#!/usr/bin/env node
/**
 * Simple Node.js server for serving SvelteKit static build with SPA routing
 * Handles fallback to index.html for client-side routes
 */

import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
const PORT = process.env.PORT || 1717;
const HOST = process.env.HOST || '0.0.0.0';
const BUILD_DIR = path.join(__dirname, 'build');

// Check if build directory exists
if (!fs.existsSync(BUILD_DIR)) {
    console.error('❌ Build directory not found. Please run "npm run build" first.');
    process.exit(1);
}

// Serve static files from build directory
app.use(express.static(BUILD_DIR, {
    maxAge: '1h', // Cache static assets for 1 hour
    etag: true
}));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', message: 'Frontend server is running' });
});

// Proxy /uploads/ requests to backend for uploaded files
app.use('/uploads', createProxyMiddleware({
    target: 'http://172.30.98.177:8000',
    changeOrigin: true,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxying upload request: ${req.originalUrl} -> http://172.30.98.177:8000${req.originalUrl}`);
    },
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.status(500).send('Proxy error');
    }
}));

// SPA fallback - serve index.html for all other routes
app.get('*', (req, res) => {
    const indexPath = path.join(BUILD_DIR, 'index.html');
    
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(500).send('index.html not found in build directory');
    }
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).send('Internal server error');
});

// Start server
app.listen(PORT, HOST, () => {
    console.log(`🚀 Frontend server running at http://${HOST}:${PORT}`);
    console.log(`📁 Serving static files from: ${BUILD_DIR}`);
    console.log(`🔄 SPA routing enabled with fallback to index.html`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('🛑 SIGINT received, shutting down gracefully');
    process.exit(0);
});