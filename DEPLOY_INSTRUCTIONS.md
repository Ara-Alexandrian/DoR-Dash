# DoR-Dash Unraid Deployment Instructions

## Step 1: Update Your Nginx Proxy Manager

**Edit your existing proxy host** (`dd.kronisto.net`):

1. **Details Tab:**
   - Domain Names: `dd.kronisto.net` ✅ (keep existing)
   - Scheme: `http` ✅ (keep existing)
   - Forward Hostname/IP: **Change to** `172.30.98.177`
   - Forward Port: **Change to** `1717`
   - Cache Assets: ✅ Enabled (keep existing)
   - Block Common Exploits: ✅ Enabled (keep existing)
   - Websockets Support: ✅ Enabled (keep existing)

2. **SSL Tab:**
   - SSL Certificate: `*.kronisto.net` ✅ (keep existing)
   - Force SSL: ✅ Enabled (keep existing)
   - HTTP/2 Support: ✅ Enabled (keep existing)

3. **Advanced Tab:**
   Copy and paste this configuration:
   ```nginx
   # Increase client body size for file uploads
   client_max_body_size 50M;

   # Backend API proxy
   location /api/ {
       proxy_pass http://172.30.98.177:1718/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-Host $host;
       proxy_set_header X-Forwarded-Port $server_port;
       
       # Handle preflight CORS requests
       if ($request_method = 'OPTIONS') {
           add_header 'Access-Control-Allow-Origin' '$http_origin' always;
           add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
           add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;
           add_header 'Access-Control-Allow-Credentials' 'true' always;
           add_header 'Access-Control-Max-Age' 86400 always;
           add_header 'Content-Length' 0;
           add_header 'Content-Type' 'text/plain';
           return 204;
       }
       
       # Timeout settings
       proxy_connect_timeout 60s;
       proxy_send_timeout 60s;
       proxy_read_timeout 60s;
   }

   # Health check endpoint
   location /health {
       proxy_pass http://172.30.98.177:1718/health;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       access_log off;
   }

   # Security headers
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-XSS-Protection "1; mode=block" always;
   add_header X-Content-Type-Options "nosniff" always;
   add_header Referrer-Policy "no-referrer-when-downgrade" always;
   ```

4. **Save** the configuration

## Step 2: Deploy on Unraid

**SSH into your Unraid server and run:**

```bash
# Navigate to appdata directory
cd /mnt/user/appdata/

# Clone the repository from Gitea mirror
git clone https://git.kronisto.net/aalexandrian/DoR-Dash.git
cd DoR-Dash

# Make the deploy script executable
chmod +x deploy.sh

# Deploy the application
./deploy.sh deploy
```

## Step 3: Verify Deployment

**Check these URLs:**
- Direct Frontend: `http://172.30.98.177:1717`
- Direct Backend: `http://172.30.98.177:1718/health`
- Through Nginx: `https://dd.kronisto.net`

**Login with:**
- Username: `cerebro`
- Password: `123`

## Step 4: Controlled Updates

The container will check for updates **only when restarted** (for stability). To update:

```bash
# Method 1: Restart container to check for updates
docker restart dor-dash

# Method 2: Rebuild with latest code
./deploy.sh rebuild

# View update logs
docker logs dor-dash | grep -E "(UPDATE|SUCCESS|ERROR)"
```

## Management Commands

```bash
# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Restart container
./deploy.sh restart

# Stop container
./deploy.sh stop

# Rebuild and redeploy
./deploy.sh rebuild
```

## Troubleshooting

**If the container fails to start:**
```bash
# Check Docker logs
docker logs dor-dash

# Verify network connectivity
ping 172.30.98.213  # PostgreSQL
ping 172.30.98.214  # Redis
ping 172.30.98.14   # Ollama
```

**If the website doesn't load:**
1. Test direct access first: `http://172.30.98.177:1717`
2. Check nginx proxy manager logs
3. Verify the advanced configuration was saved correctly

**For auto-update issues:**
```bash
# Disable auto-updates temporarily
docker run -d --name dor-dash-manual -p 1717:7117 -p 1718:8000 \
  -e AUTO_UPDATE=false [other environment variables...] dor-dash:latest
```

## Success Indicators

✅ Container shows "DoR-Dash is running" in logs  
✅ Health check returns: `{"status":"healthy","message":"DoR-Dash API is running"}`  
✅ Website loads at `https://dd.kronisto.net`  
✅ Login works with cerebro/123  
✅ Auto-update logs show periodic check activity  

---

**Need help?** Check the container logs first: `docker logs dor-dash`