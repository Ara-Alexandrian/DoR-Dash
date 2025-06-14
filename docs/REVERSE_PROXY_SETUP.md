# Reverse Proxy Setup Guide

This document provides instructions for setting up a reverse proxy to access the DoR-Dash application through a custom domain with SSL.

## Overview

The DoR-Dash application consists of two services:
- **Frontend**: SvelteKit application running on port 1717
- **Backend**: FastAPI application running on port 8000

To serve the application through a reverse proxy with SSL, you need to configure your proxy to forward both frontend and API requests.

## Nginx Proxy Manager Configuration

### Prerequisites
- Nginx Proxy Manager installed and running
- Domain name configured to point to your proxy server
- SSL certificate available (Let's Encrypt recommended)

### Setup Steps

1. **Create a new Proxy Host entry** in Nginx Proxy Manager

2. **Configure the main proxy settings:**
   - **Domain Names**: Your domain (e.g., `dd.kronisto.net`)
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `172.30.98.177` (or your server IP)
   - **Forward Port**: `1717`
   - **Cache Assets**: ✅ Enabled
   - **Block Common Exploits**: ✅ Enabled
   - **Websockets Support**: ✅ Enabled

3. **Configure SSL settings:**
   - **SSL Certificate**: Select your certificate
   - **Force SSL**: ✅ Enabled
   - **HTTP/2 Support**: ✅ Enabled

4. **🚨 CRITICAL: Add Advanced Configuration** to handle API requests:
   
   **IMPORTANT**: You currently only have the `/api/` proxy configured. You MUST add a frontend proxy configuration to nginx for the application to work through the reverse proxy.
   
   ```nginx
   # API proxy (add this to your existing configuration)
   location /api/ {
       proxy_pass http://172.30.98.177:8000/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       
       # Handle preflight requests
       if ($request_method = 'OPTIONS') {
           add_header 'Access-Control-Allow-Origin' '*';
           add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
           add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization';
           add_header 'Access-Control-Max-Age' 86400;
           add_header 'Content-Length' 0;
           add_header 'Content-Type' 'text/plain';
           return 204;
       }
   }
   ```

5. **🚨 REQUIRED: Update Main Proxy Configuration**
   
   **The root issue**: Your current nginx setup only proxies `/api/` requests but doesn't proxy the frontend application itself. Users are likely accessing the frontend directly at `http://172.30.98.177:1717` instead of through the reverse proxy.
   
   **Fix**: Update your main proxy host configuration in Nginx Proxy Manager:
   - **Forward Hostname/IP**: `172.30.98.177` 
   - **Forward Port**: `1717` (frontend port, not backend port)

## Application Configuration

### Frontend Configuration
The frontend must be configured to use relative API paths instead of absolute URLs to work with the reverse proxy.

**Environment Variables:**
```bash
VITE_API_URL=
```

**Key Points:**
- When `VITE_API_URL` is empty, the frontend uses relative paths (`/api/v1/...`)
- This allows the reverse proxy to handle API routing transparently
- Clear browser cache after configuration changes

### Backend Configuration
No special configuration required for the backend when using reverse proxy.

## Troubleshooting

### Common Issues

1. **Mixed Content Errors**
   - Ensure `VITE_API_URL` is empty in frontend configuration
   - Clear browser cache completely
   - Try incognito/private browsing mode

2. **API Requests Not Working**
   - Verify the advanced nginx configuration is saved
   - Test API endpoint directly: `https://yourdomain.com/api/v1/auth/login`
   - Should return "Method Not Allowed" for GET requests (this is correct)

3. **Browser Cache Issues**
   - Hard refresh with Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Clear all browser data for the domain
   - Try different browser or incognito mode

4. **File Upload Issues**
   - Ensure nginx proxy manager allows large file uploads
   - Configure `client_max_body_size` in nginx if needed

### Testing the Setup

1. **Test Frontend Access:**
   ```bash
   curl -I https://yourdomain.com/
   ```

2. **Test API Access:**
   ```bash
   curl -X POST https://yourdomain.com/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=cerebro&password=123&grant_type=password"
   ```

3. **Test in Browser:**
   - Navigate to `https://yourdomain.com/login`
   - Login with credentials: `cerebro` / `123`
   - Verify no mixed content errors in browser console

## Security Considerations

- SSL/TLS is enforced for all connections
- CORS headers are properly configured
- File upload size limits are enforced (50MB)
- Authentication tokens are transmitted securely

## Performance Optimization

- Gzip compression enabled via nginx
- Static asset caching configured
- WebSocket support for real-time features
- HTTP/2 enabled for better performance