# DoR-Dash Documentation

This directory contains all documentation for the DoR-Dash (Dose of Reality Dashboard) application.

## Quick Start

- **🚀 [Deployment Instructions](DEPLOY_INSTRUCTIONS.md)** - Complete Unraid deployment guide
- **🔧 [Technical Notes](technical-notes.md)** - Detailed bug fixes and technical solutions
- **🌐 [Reverse Proxy Setup](REVERSE_PROXY_SETUP.md)** - Nginx configuration for SSL termination

## Documentation Index

### Setup & Deployment
- **[DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)** - Step-by-step Unraid deployment
- **[REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md)** - Nginx Proxy Manager configuration
- **[UNRAID_DEPLOYMENT.md](UNRAID_DEPLOYMENT.md)** - Unraid-specific deployment details

### Development & Maintenance  
- **[technical-notes.md](technical-notes.md)** - Bug fixes, debugging sessions, and solutions
- **[pgadmin-setup-guide.md](pgadmin-setup-guide.md)** - Database administration setup
- **[GITHUB_GITEA_MIRROR_SETUP.md](GITHUB_GITEA_MIRROR_SETUP.md)** - Repository mirroring configuration

## Key Information

### Application URLs
- **Production:** https://dd.kronisto.net (through Nginx reverse proxy)
- **Direct Frontend:** http://172.30.98.177:1717
- **Direct Backend:** http://172.30.98.177:8000

### Default Credentials
- **Admin:** cerebro / 123
- **Test User:** aalexandrian / 12345678

### Recent Critical Fixes
1. **PostgreSQL Enum Case Mismatch** - Fixed user role update failures
2. **JSON Response Parsing** - Fixed user deletion errors
3. **Port Standardization** - Updated to port 1717
4. **Meeting Calendar Persistence** - Moved to PostgreSQL storage

## Architecture Overview

### Technology Stack
- **Backend:** FastAPI with PostgreSQL
- **Frontend:** SvelteKit with Vite
- **Deployment:** Docker on Unraid br0 network
- **Reverse Proxy:** Nginx Proxy Manager with SSL
- **File Storage:** Persistent `/uploads/` directory

### Data Safety Status
✅ **Persistent & Safe:**
- Meeting calendar (PostgreSQL)
- File uploads (`/uploads/` directory)
- Database schemas

⚠️ **In-Memory (Risk of Data Loss):**
- User accounts
- Student/faculty updates  
- Registration requests

## Support

For troubleshooting:
1. Check container logs: `docker logs dor-dash`
2. Review [technical-notes.md](technical-notes.md) for known issues
3. Verify deployment steps in [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)

---

**Last Updated:** June 9, 2025  
**Version:** Latest with PostgreSQL enum fixes