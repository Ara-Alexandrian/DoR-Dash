# GitHub to Gitea Mirror Setup Guide

This guide sets up automatic mirroring from GitHub to Gitea, allowing you to develop on GitHub while deploying from your local Gitea instance.

## 🔄 Mirror Configuration

### Step 1: Create Mirror Repository in Gitea

1. **Login to your Gitea instance**: `https://git.kronisto.net`

2. **Create New Repository**:
   - Click **"+"** → **"New Migration"**
   - Select **"GitHub"** as source
   - **Clone Address**: `https://github.com/Ara-Alexandrian/DoR-Dash.git`
   - **Repository Name**: `DoR-Dash`
   - **Visibility**: Private (recommended)
   - ✅ **Enable "This repository will be a mirror"**
   - **Migration Type**: Select **"Pull mirror"**
   - **Sync Interval**: `10m` (sync every 10 minutes)

3. **Click "Migrate Repository"**

### Step 2: Configure GitHub Webhook (Optional - for instant sync)

For faster syncing, set up a webhook in GitHub:

1. **In GitHub** (`https://github.com/Ara-Alexandrian/DoR-Dash`):
   - Go to **Settings** → **Webhooks**
   - Click **"Add webhook"**
   - **Payload URL**: `https://git.kronisto.net/api/v1/repos/[your-username]/DoR-Dash/mirror-sync`
   - **Content type**: `application/json`
   - **Secret**: (optional, but recommended)
   - **Events**: Select **"Just the push event"**
   - ✅ **Active**

2. **Click "Add webhook"**

## 🚀 Updated Deployment Configuration

Since you'll be using GitHub as the primary repository, we need to update the Docker auto-update configuration.

### Option A: Use GitHub Repository (Recommended)

Update the Docker environment to pull from GitHub:

```bash
# In your deploy.sh or docker run command, use:
-e REPO_URL="https://github.com/Ara-Alexandrian/DoR-Dash.git"
```

**Pros**: Direct from source, faster updates
**Cons**: Requires internet access from Unraid

### Option B: Use Gitea Mirror (Local Network)

Keep using Gitea as configured:

```bash
# Keep existing configuration:
-e REPO_URL="https://git.kronisto.net/[your-username]/DoR-Dash.git"
```

**Pros**: Local network only, faster cloning
**Cons**: 10-minute delay for auto-sync

## 🔧 Development Workflow

### Your New Workflow:

1. **Develop on GitHub**:
   ```bash
   git clone https://github.com/Ara-Alexandrian/DoR-Dash.git
   cd DoR-Dash
   # Make changes
   git add .
   git commit -m "Your changes"
   git push origin master
   ```

2. **Automatic Mirroring**:
   - GitHub webhook triggers instant sync (if configured)
   - OR Gitea pulls changes every 10 minutes

3. **Automatic Deployment**:
   - Docker container checks for updates every 5 minutes
   - Automatically deploys new changes from your chosen repository

### Testing the Setup:

1. **Push a small change to GitHub**
2. **Check Gitea mirror** updates within 10 minutes (or instantly with webhook)
3. **Watch Docker logs** for auto-update activity:
   ```bash
   docker logs -f dor-dash | grep -E "(UPDATE|PULL|DEPLOY)"
   ```

## 📝 Repository URLs

- **GitHub (Primary)**: `https://github.com/Ara-Alexandrian/DoR-Dash.git`
- **Gitea (Mirror)**: `https://git.kronisto.net/[your-username]/DoR-Dash.git`

## ⚙️ Update Docker Configuration

Choose your preferred approach and update the deployment:

### Using GitHub (Direct):
```bash
./deploy.sh stop
# Edit docker-compose.prod.yml or deploy.sh
# Change REPO_URL to: https://github.com/Ara-Alexandrian/DoR-Dash.git
./deploy.sh deploy
```

### Using Gitea (Mirror):
```bash
# No changes needed - current configuration works
# Just ensure the mirror is set up correctly
```

## 🔍 Monitoring

Monitor the mirroring and deployment:

```bash
# Check Gitea mirror status
curl -s https://git.kronisto.net/api/v1/repos/[username]/DoR-Dash

# Check Docker auto-update logs
docker logs -f dor-dash | grep UPDATE

# Check last commit in container
docker exec dor-dash cat /app/.current-commit
```

## 🐛 Troubleshooting

### Mirror Not Syncing:
1. Check Gitea logs
2. Verify GitHub repository is public or credentials are correct
3. Test webhook delivery in GitHub

### Auto-Update Not Working:
1. Check repository URL is accessible from Docker container
2. Verify network connectivity
3. Check Docker container logs for errors

---

**Recommended Setup**: Use GitHub as primary repository with Gitea mirror for redundancy and local network benefits.