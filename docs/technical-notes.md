# Technical Notes

This document contains detailed technical information about fixes, debugging sessions, and architectural decisions for the DoR-Dash application.

## Table of Contents

1. [MCP Server Configuration](#mcp-server-configuration)
2. [PostgreSQL Enum Case Mismatch Fix](#postgresql-enum-case-mismatch-fix)
3. [JSON Response Parsing Fix](#json-response-parsing-fix)
4. [Port Configuration Changes](#port-configuration-changes)
5. [Database Architecture](#database-architecture)
6. [Frontend SPA Routing Fix](#frontend-spa-routing-fix)
7. [Git Authentication Setup](#git-authentication-setup)
8. [Current Session Status](#current-session-status)

## MCP Server Configuration

### Problem Description

**Date:** January 6, 2025  
**Issue:** Multiple MCP (Model Context Protocol) servers failing to connect

### Root Cause Analysis

1. **PostgreSQL Server:** Using default credentials (`postgres:postgres`) instead of actual database credentials
2. **Git Server:** Missing repository path parameter
3. **Mermaid Server:** Incorrect package name (`mermaid-mcp-server` vs `@peng-shawn/mermaid-mcp-server`)
4. **SSH Server:** Not configured (needed for container debugging)

### Solution Implementation

**MCP Configuration File:** `.claude/mcp_settings.json`

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://DoRadmin:1232@172.30.98.213:5432/DoR"
      ]
    },
    "redis": {
      "command": "npx",
      "args": [
        "-y",
        "@redis/mcp-redis",
        "redis://172.30.98.214:6379"
      ]
    },
    "filesystem": {
      "command": "npx", 
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/config/workspace/gitea/DoR-Dash"
      ]
    },
    "mermaid": {
      "command": "npx",
      "args": [
        "-y",
        "@peng-shawn/mermaid-mcp-server"
      ]
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "/config/workspace/gitea/DoR-Dash"
      ]
    },
    "ssh": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-ssh"
      ]
    }
  }
}
```

### MCP Server Details

1. **PostgreSQL (`@modelcontextprotocol/server-postgres`)**
   - Credentials: `DoRadmin:1232`
   - Host: `172.30.98.213`
   - Database: `DoR`

2. **Redis (`@redis/mcp-redis`)**
   - Host: `172.30.98.214`
   - Port: `6379`

3. **Mermaid (`@peng-shawn/mermaid-mcp-server`)**
   - Correct package identified via npm search

4. **Git (`@modelcontextprotocol/server-git`)**
   - Added `--repository` parameter with path

5. **SSH (`mcp-ssh`)**
   - Added for direct container debugging capabilities

### Verification

Tested connections using Python scripts:
```python
# PostgreSQL
psycopg2.connect('postgresql://DoRadmin:1232@172.30.98.213:5432/DoR')

# Redis
redis.Redis(host='172.30.98.214', port=6379).ping()
```

Both connections successful.

---

## PostgreSQL Enum Case Mismatch Fix

### Problem Description

**Date:** June 9, 2025  
**Issue:** User role updates failing with PostgreSQL enum error

```
Failed to update user: (psycopg2.errors.InvalidTextRepresentation) 
invalid input value for enum userrole: "FACULTY"
LINE 1: UPDATE "user" SET role='FACULTY', updated_at=now() WHERE "us...
[parameters: {'role': 'FACULTY', 'user_id': 4}]
```

### Root Cause Analysis

The issue was caused by inconsistent enum values in the PostgreSQL database. Investigation revealed:

1. **Database Enum Values (Initial State):**
   ```sql
   SELECT enumlabel FROM pg_enum 
   JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
   WHERE pg_type.typname = 'userrole' 
   ORDER BY enumlabel;
   ```
   Result: `['ADMIN', 'STUDENT', 'faculty', 'secretary']`

2. **Python Enum Definition:** Used lowercase values (`student`, `faculty`, etc.)
3. **Frontend:** Sent lowercase values (`faculty`)
4. **Backend Logic:** Converted to uppercase (`FACULTY`) but `FACULTY` didn't exist in database

### Technical Investigation Steps

1. **Code Review:** Examined enum handling in:
   - `backend/app/db/models/user.py` - UserRole enum definition
   - `backend/app/api/endpoints/auth.py` - update_user function
   - `frontend/src/routes/admin/users/+page.svelte` - form values

2. **Database Migration Analysis:** Found incomplete migration in:
   - `5453acf55175_add_missing_role_enum_values.py` - Only added lowercase values

3. **SQLAlchemy Enum Handling:** Tested different approaches:
   - `values_callable` parameter
   - Direct string assignment
   - Enum object creation

### Solution Implementation

**Final Solution:** Added missing uppercase enum values to database

```python
# Added missing enum values to PostgreSQL
from sqlalchemy import text
db.execute(text("ALTER TYPE userrole ADD VALUE 'FACULTY'"))
db.execute(text("ALTER TYPE userrole ADD VALUE 'SECRETARY'"))
```

**Final Database State:**
```
['ADMIN', 'FACULTY', 'SECRETARY', 'STUDENT', 'faculty', 'secretary']
```

### Code Changes Made

1. **Updated `auth.py` role handling:**
   ```python
   # Convert to uppercase to match database enum
   role_value = value.upper() if isinstance(value, str) else value
   db_user.role = role_value
   ```

2. **Updated enum definition to match database:**
   ```python
   class UserRole(str, enum.Enum):
       STUDENT = "STUDENT"
       FACULTY = "FACULTY" 
       SECRETARY = "SECRETARY"
       ADMIN = "ADMIN"
   ```

3. **Added conversion for API responses:**
   ```python
   "role": user.role.lower() if isinstance(user.role, str) else user.role
   ```

### Lessons Learned

1. **Enum Consistency:** Database enums must be consistent across all values
2. **Migration Completeness:** Ensure all enum values are added in migrations
3. **Case Sensitivity:** PostgreSQL enums are case-sensitive
4. **Testing:** Always verify database state matches code expectations

### Files Modified

- `backend/app/db/models/user.py` - UserRole enum definition
- `backend/app/api/endpoints/auth.py` - Role handling logic
- Database schema - Added missing enum values

---

## JSON Response Parsing Fix

### Problem Description

**Date:** June 9, 2025  
**Issue:** User deletion failing with JSON parsing error

```
Failed to execute 'json' on 'Response': Unexpected end of JSON input
```

### Root Cause

Frontend API layer attempting to parse JSON from HTTP 204 No Content responses, which have empty bodies.

### Solution

Updated `frontend/src/lib/api/index.js` to handle empty responses:

```javascript
// Handle responses with no content first (like DELETE operations)
if (response.status === 204) {
  return { success: true };
}

// Get response text first
let responseText = '';
try {
  responseText = await response.text();
} catch (e) {
  console.warn('Failed to read response text:', e);
  responseText = '';
}

// Handle empty responses
if (!responseText || responseText.trim() === '') {
  if (response.ok) {
    return { success: true };
  } else {
    throw new Error(`Request failed with status ${response.status}`);
  }
}
```

---

## Port Configuration Changes

### Change Summary

**Date:** June 9, 2025  
**Change:** Updated frontend port from 7117 to 1717 per user preference

### Files Updated

1. `docker-entrypoint.sh` - Updated serve commands
2. `Dockerfile` - Updated EXPOSE directive  
3. `deploy.sh` - Updated display URLs
4. `docs/DEPLOY_INSTRUCTIONS.md` - Updated all documentation
5. `unraid-aliases.sh` - Updated convenience commands

### Technical Details

- **Old Port:** 7117
- **New Port:** 1717
- **Network:** br0 static IP (172.30.98.177)
- **Reverse Proxy:** Nginx proxy manager forwards requests
- **SSL:** Enforced through reverse proxy (dd.kronisto.net)

---

## Directory Reorganization

### Project Structure Improvements

**Date:** June 9, 2025  
**Change:** Reorganized root directory for better maintainability

### New Directory Structure
```
/
├── config/                 # Configuration files
│   ├── nginx.conf
│   ├── nginx-proxy-manager-config.txt
│   └── environment.yml
├── docker/                 # Docker-related files  
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   └── docker-entrypoint.sh
├── docs/                   # All documentation
│   ├── README.md
│   ├── DEPLOY_INSTRUCTIONS.md
│   ├── technical-notes.md
│   └── [other docs]
├── scripts/                # Shell scripts
│   ├── deploy.sh
│   ├── unraid-aliases.sh
│   ├── start.sh (symlink)
│   └── stop.sh (symlink)
├── temp/                   # Temporary files
│   └── token.txt
├── backend/                # Backend application
├── frontend/               # Frontend application
├── logs/                   # Application logs
├── uploads/                # File uploads
└── [other directories]
```

### Files Moved
- **Docker files:** `Dockerfile`, `docker-compose*.yml`, `docker-entrypoint.sh` → `/docker/`
- **Scripts:** `deploy.sh`, `unraid-aliases.sh` → `/scripts/`
- **Configuration:** `nginx.conf`, `environment.yml` → `/config/`
- **Documentation:** All `.md` files → `/docs/`
- **Temporary:** `token.txt` → `/temp/`

### References Updated
- `scripts/deploy.sh` - Updated docker build to use `-f docker/Dockerfile`
- `docker/Dockerfile` - Updated COPY command for docker-entrypoint.sh
- `scripts/unraid-aliases.sh` - Updated all deploy.sh references
- `docs/DEPLOY_INSTRUCTIONS.md` - Updated script paths
- Symbolic links maintained for `start.sh` and `stop.sh` in root

---

## Database Architecture

### Current Schema

#### User Management
- **Users Table:** PostgreSQL with full persistence
- **Authentication:** JWT tokens with bcrypt password hashing
- **Roles:** Enum type with both uppercase and lowercase values for compatibility
- **Registration:** Admin approval workflow for new users

#### Meeting System  
- **Storage:** PostgreSQL (persistent, not in-memory)
- **Calendar:** Full CRUD operations with drag-and-drop interface
- **Agendas:** Compiled from student and faculty updates
- **Files:** Persistent storage in `/uploads/` directory

#### Data Safety Status

✅ **PERSISTENT (Safe):**
- Meeting calendar (PostgreSQL)
- Uploaded files (`/uploads/` directory)
- Database schemas and migrations

⚠️ **IN-MEMORY (Data Loss Risk):**
- User accounts (USERS_DB dictionary)
- Student updates (STUDENT_UPDATES dictionary)  
- Faculty updates (FACULTY_UPDATES dictionary)
- Registration requests (REGISTRATION_REQUESTS dictionary)

### Migration History

1. `3250d522637a_add_persistent_user_storage.py` - Initial user storage
2. `5453acf55175_add_missing_role_enum_values.py` - Added role enum values
3. `65c2b80029f3_add_registration_request_table.py` - Registration system
4. Manual enum fixes - Added uppercase enum values via SQL

---

## Development Environment

### Container Configuration
- **Backend:** FastAPI with uvicorn auto-reload
- **Frontend:** SvelteKit with Vite HMR
- **Database:** PostgreSQL with persistent volumes
- **Network:** Unraid br0 bridge with static IP
- **Reverse Proxy:** Nginx Proxy Manager for SSL termination

### Cache Busting
Implemented timestamp-based asset naming in `vite.config.js`:
```javascript
entryFileNames: `assets/[name].${Date.now()}.js`,
chunkFileNames: `assets/[name].${Date.now()}.js`, 
assetFileNames: `assets/[name].${Date.now()}.[ext]`
```

### Convenience Tools
Created Unraid server management aliases in `unraid-aliases.sh`:
- `dorcd` - Navigate to project directory
- `dorbuild` - Build and restart containers
- `dorupdate` - Pull latest code and restart
- `dorlogs` - View application logs
- `dorstatus` - Check container status

---

## Frontend SPA Routing Fix

### Problem Description

**Date:** June 11, 2025  
**Issue:** Frontend routing completely broken - all client-side routes (dashboard, login, admin) returning HTTP 404 errors

### Root Cause Analysis

The application was using Python's SimpleHTTP server to serve the SvelteKit static build, which doesn't support Single Page Application (SPA) routing. Static servers return 404 for routes that don't exist as physical files, breaking client-side routing.

**Symptoms:**
- `curl http://172.30.98.177:1717/dashboard` → 404 "File not found"
- `curl http://172.30.98.177:1717/login` → 404 "File not found"  
- Server headers: `Server: SimpleHTTP/0.6 Python/3.11.13`

### Solution Implementation

**1. Created Custom Node.js Server (`frontend/server.js`):**
```javascript
// Express server with SPA fallback support
app.use(express.static(BUILD_DIR));
app.get('*', (req, res) => {
    res.sendFile(path.join(BUILD_DIR, 'index.html'));
});
```

**2. Updated Docker Configuration:**
- **Dockerfile:** Copy server.js and node_modules to production stage
- **docker-entrypoint.sh:** Prioritize custom server over fallbacks
- **package.json:** Added Express 4.x dependency and `serve` script

**3. Fixed ES Module Issues:**
- Converted server from CommonJS `require()` to ES modules `import`
- Downgraded Express from 5.x to 4.x for stability

### Test Results

✅ **Before Fix:**
```bash
curl http://172.30.98.177:1717/dashboard
# HTTP/1.0 404 File not found
```

✅ **After Fix:**
```bash
curl http://172.30.98.177:1717/dashboard  
# Returns: <!DOCTYPE html><html>... (SvelteKit app)

curl http://172.30.98.177:1717/health
# {"status":"healthy","message":"Frontend server is running"}
```

### Files Modified
- `frontend/server.js` - New custom Express server
- `frontend/package.json` - Added Express dependency  
- `docker/Dockerfile` - Copy server files
- `docker/docker-entrypoint.sh` - Use custom server

---

## Git Authentication Setup

### Problem Description

**Date:** June 11, 2025  
**Issue:** Unable to push commits to GitHub repository for automated deployments

### Solution Implementation

**1. GitHub Fine-Grained Token:**
- Created personal access token with DoR-Dash repository permissions
- Stored in `.github-token` file (gitignored for security)

**2. Git Remote Configuration:**
```bash
git remote set-url origin https://Ara-Alexandrian:TOKEN@github.com/Ara-Alexandrian/DoR-Dash.git
git config --global credential.helper store
```

**3. Security Measures:**
- Added `.github-token`, `*.token`, `credentials.txt` to `.gitignore`
- Token has repository-specific permissions only

### Current Status
✅ **Git Push Working:** Latest commits successfully pushed to GitHub
✅ **Authentication Configured:** Can commit and push on behalf of user

---

## Current Session Status

### Completed Tasks ✅

1. **MCP Server Installation:** 
   - Installed Svelte MCP docs server for reference
   - Added GitHub MCP server configuration
   - SSH server functioning for container debugging

2. **Frontend Routing Fix:**
   - Created custom Express server with SPA routing
   - Fixed SvelteKit routing issues (404 errors)
   - Updated Docker configuration
   - Local testing successful

3. **Git Authentication:**
   - Set up GitHub fine-grained token
   - Configured git for automated pushes
   - Commits successfully pushed to GitHub

### Current Issue 🚨

**Production Deployment Blocked:** `dorfullrebuild` command failing with git merge conflict in production directory `/mnt/user/appdata/DoR-Dash`

**Error Message:**
```
error: You have not concluded your merge (MERGE_HEAD exists).
hint: Please, commit your changes before merging.
fatal: Exiting because of unfinished merge.
```

### Resolution Commands (Run from production directory)

```bash
cd /mnt/user/appdata/DoR-Dash
git merge --abort 2>/dev/null || true
rm -f .git/MERGE_* .git/*.lock 2>/dev/null || true  
git reset --hard HEAD
git fetch origin master
git reset --hard origin/master
dorfullrebuild --no-cache
```

### Next Steps After Restart

1. **Resolve Production Git State:** Run the commands above to clean git merge conflict
2. **Deploy Frontend Fix:** Execute `dorfullrebuild --no-cache` to deploy SPA routing fix
3. **Test Website Functionality:** Comprehensive testing of all interactive elements
4. **Fix aalexandrian Login:** Investigate why faculty login fails (user exists, role correct)
5. **Clean Corrupted Data:** Remove Docker build logs from student update entries

### Key Files Modified This Session

- `frontend/server.js` (NEW) - Custom Express server
- `frontend/package.json` - Added Express dependency
- `docker/Dockerfile` - Updated to copy server files  
- `docker/docker-entrypoint.sh` - Use custom server
- `.claude/mcp_settings.json` - Added Svelte & GitHub MCP servers
- `.gitignore` - Added security token exclusions
- `docs/technical-notes.md` - This documentation

### Test Credentials for Resumption

- **Admin Login:** `cerebro/123` ✅ Working
- **Faculty Login:** `aalexandrian/12345678` ❌ "Incorrect username or password"
- **Backend API:** http://172.30.98.177:8000 ✅ Healthy  
- **Frontend:** http://172.30.98.177:1717 ❌ Still using Python server (needs rebuild)