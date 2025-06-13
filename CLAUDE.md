# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DoR-Dash (Dose of Reality Dash) is a web application for managing student research meetings. It enables users to log in, submit bi-monthly updates with AI-assisted refinement, request support, schedule mock exams, and share presentation files.

## Technical Stack

- **Backend**: Python with FastAPI
- **Frontend**: SvelteKit or Vue.js with Vite
- **Database**: PostgreSQL
- **Caching**: Redis
- **AI Integration**: Ollama API with Mistral (CPU/RAM based, not GPU)
- **Deployment**: Docker and Docker Compose

## Core Development Commands

### Setup and Installation

```bash
# Build and start all services
docker-compose up -d

# Build specific services
docker-compose build backend
docker-compose build frontend

# View logs
docker-compose logs -f
```

### Backend Development (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend service locally (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Frontend Development (SvelteKit/Vue.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## Architecture Notes

### Directory Structure (Planned)

```
/
├── backend/
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database models and connections
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── lib/            # Reusable components/utilities
│   │   ├── routes/         # Page components
│   │   ├── stores/         # State management
│   │   └── app.svelte      # Application entry point
│   ├── static/             # Static assets
│   └── package.json        # Node dependencies
├── docker-compose.yml      # Container orchestration
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

### Data Models

- **User**: Authentication and role management
- **StudentUpdate**: Bi-monthly update submissions
- **SupportRequest**: Requests for support
- **MockExamRequest**: Mock exam scheduling
- **FileUpload**: Attachment metadata
- **AssignedPresentation**: Presentation scheduling

### API Endpoints Structure

- `/auth`: Authentication endpoints
- `/users`: User management (admin)
- `/updates`: Student updates submission and retrieval
- `/requests`: Support and mock exam requests
- `/files`: File upload and download
- `/roster`: Student roster management
- `/presentations`: Presentation assignment

## Performance Considerations

1. Use Redis aggressively for caching:
   - Session data
   - Query results (especially roster, meeting agendas)
   - UI components where possible

2. Optimize database queries:
   - Use appropriate indexes
   - Limit fetched fields
   - Implement pagination for large data sets

3. Frontend optimization:
   - Minimize JavaScript bundle sizes
   - Implement code splitting
   - Use SSR/SSG where appropriate

## Ollama Integration Guidelines

- Ollama runs Mistral AI on CPU/RAM only (not GPU)
- Backend makes HTTP requests to Ollama API
- Default endpoint: http://localhost:11434
- Implement proper error handling, timeouts and retries
- Use for text refinement in student updates

## MCP Server Tools

Claude Code is configured with Model Context Protocol (MCP) servers that provide enhanced development capabilities:

### Available MCP Servers

1. **PostgreSQL Server** (`postgres`)
   - Direct database queries and schema inspection
   - Data integrity checking and analysis
   - Performance monitoring and optimization
   - Connection: `postgresql://DoRadmin:1232@172.30.98.213:5432/DoR`

2. **Redis Server** (`redis`)
   - Cache management and key-value operations
   - Memory usage analysis and monitoring
   - Session data inspection and cleanup
   - Connection: `redis://172.30.98.214:6379`
   - Package: `redis-mcp`

3. **File System Server** (`filesystem`)
   - Enhanced file operations within project directory
   - Upload directory management and analysis
   - File structure verification and cleanup
   - Scope: `/config/workspace/gitea/DoR-Dash`

4. **Mermaid Server** (`mermaid`)
   - Create architecture diagrams and flowcharts
   - Generate documentation visuals
   - Validate and render Mermaid syntax
   - Export diagrams in SVG format
   - Package: `@peng-shawn/mermaid-mcp-server`

5. **Git Server** (`git`)
   - Advanced version control operations
   - Repository analysis and health checks
   - Commit history and branch management
   - Security scanning for exposed credentials
   - Repository path: `/config/workspace/gitea/DoR-Dash`
   - Package: `mcp-git`

6. **SSH Server** (`ssh`)
   - Direct SSH access to containers and servers
   - Real-time debugging of running containers
   - Execute commands on remote hosts
   - Container console access
   - Package: `mcp-ssh`

### Using MCP Tools

These servers provide additional capabilities beyond standard Claude Code tools:

#### PostgreSQL Server Usage
```sql
-- Example: Query user data
mcp__postgres__query(sql="SELECT * FROM users WHERE role='student'")

-- Example: Check database schema
mcp__postgres__query(sql="SELECT table_name FROM information_schema.tables WHERE table_schema='public'")

-- Example: Analyze meeting data
mcp__postgres__query(sql="SELECT COUNT(*) as total_meetings, COUNT(DISTINCT user_id) as unique_attendees FROM meetings")
```

#### Redis Server Usage
```python
# Example: Check cached sessions
mcp__redis__list(pattern="session:*")

# Example: Get specific cache value
mcp__redis__get(key="user:123:preferences")

# Example: Set cache with expiration
mcp__redis__set(key="temp:data", value="{'status':'processing'}", expireSeconds=300)

# Example: Clear specific cache keys
mcp__redis__delete(key=["session:old1", "session:old2"])
```

#### File System Server Usage
```python
# Example: List upload directory
mcp__filesystem__list_directory(path="/config/workspace/gitea/DoR-Dash/uploads")

# Example: Search for specific files
mcp__filesystem__search_files(path="/config/workspace/gitea/DoR-Dash", pattern="*.py", excludePatterns=["venv/*", "__pycache__/*"])

# Example: Get file metadata
mcp__filesystem__get_file_info(path="/config/workspace/gitea/DoR-Dash/uploads/update_1_file_1.pdf")

# Example: Read multiple configuration files
mcp__filesystem__read_multiple_files(paths=["backend/.env", "frontend/.env.example"])
```

#### Mermaid Server Usage
```mermaid
# Example: Create architecture diagram
graph TD
    A[Frontend SvelteKit] -->|API Calls| B[Backend FastAPI]
    B --> C[PostgreSQL]
    B --> D[Redis Cache]
    B --> E[Ollama AI]
```

#### Git Server Usage
```bash
# Example: Check repository status
mcp__git__status()

# Example: View recent commits
mcp__git__log(limit=10)

# Example: Search for security issues
mcp__git__search(pattern="password|secret|key", excludePaths=["*.md", "docs/*"])
```

#### SSH Server Usage
```bash
# Example: Connect to backend container
mcp__ssh__connect(host="172.30.98.177", user="root", command="docker exec -it dor-dash-backend-1 bash")

# Example: Check container logs
mcp__ssh__execute(command="docker logs dor-dash-frontend-1 --tail 50")

# Example: Debug running processes
mcp__ssh__execute(command="docker exec dor-dash-backend-1 ps aux | grep python")
```

### Practical MCP Usage Examples

#### Debugging Database Issues
```python
# Check if users are properly stored
mcp__postgres__query(sql="SELECT id, username, role, created_at FROM users ORDER BY created_at DESC LIMIT 10")

# Verify meeting-update relationships
mcp__postgres__query(sql="SELECT m.id, m.title, COUNT(su.id) as student_updates FROM meetings m LEFT JOIN student_updates su ON m.id = su.meeting_id GROUP BY m.id, m.title")
```

#### Monitoring Redis Cache
```python
# Check active sessions
mcp__redis__list(pattern="session:*")

# Monitor cache memory usage
mcp__redis__info()
```

#### File Upload Verification
```python
# List all uploaded files
mcp__filesystem__list_directory(path="/config/workspace/gitea/DoR-Dash/uploads")

# Check file sizes and dates
mcp__filesystem__directory_tree(path="/config/workspace/gitea/DoR-Dash/uploads")
```

### Managing MCP Servers

```bash
# List configured servers
claude mcp list

# View server details
claude mcp get <server-name>

# Add new server
claude mcp add <name> <command> [args...]

# Remove server
claude mcp remove <server-name>
```

### MCP Server Troubleshooting

#### Common Issues and Solutions

1. **PostgreSQL Connection Failed**
   - Verify credentials: `DoRadmin:1232@172.30.98.213:5432/DoR`
   - Check if PostgreSQL container is running: `docker ps | grep postgres`
   - Test connection: `psycopg2.connect('postgresql://DoRadmin:1232@172.30.98.213:5432/DoR')`

2. **Redis Connection Failed**
   - Verify host: `172.30.98.214:6379`
   - Check if Redis container is running: `docker ps | grep redis`
   - Test connection: `redis.Redis(host='172.30.98.214', port=6379).ping()`

3. **Git Server Not Working**
   - Ensure repository path is correct: `/config/workspace/gitea/DoR-Dash`
   - Check git status manually: `git status`
   - Verify package name: `mcp-git` (not `@modelcontextprotocol/server-git`)

4. **Mermaid Server Issues**
   - Correct package: `@peng-shawn/mermaid-mcp-server`
   - May need to clear npm cache: `npm cache clean --force`

5. **SSH Server Not Connecting**
   - Verify SSH keys are configured
   - Check host accessibility: `ssh user@host`

### MCP Configuration File Location
- **Settings**: `.claude/mcp_settings.json`
- **Permissions**: `.claude/settings.local.json`

### Restarting MCP Servers
After configuration changes, restart Claude Code or use:
```bash
# Restart specific server
claude mcp restart <server-name>

# Restart all servers
claude mcp restart --all
```

## Security Practices

- Implement JWT-based authentication
- Use password hashing (bcrypt)
- Apply role-based access control
- Validate all user inputs
- Secure file upload handling
- Protect API endpoints

## Reverse Proxy Configuration

The application is designed to work behind a reverse proxy with SSL termination. See `docs/REVERSE_PROXY_SETUP.md` for detailed configuration instructions.

**Key Configuration Points:**
- Frontend must use relative API paths (`VITE_API_URL=""`)
- Nginx proxy manager forwards `/api/*` requests to backend port 8000
- Frontend served from port 1717
- SSL/HTTPS enforced for security

## Current User Accounts

**Admin User:**
- Username: `cerebro`
- Password: `123`
- Role: `admin`

**Test User:**
- Username: `aalexandrian`
- Password: `12345678`
- Role: `student`

## Recent Updates

### MCP Server Configuration Updates (Latest)
- **CRITICAL FIX**: Updated MCP server configurations with correct package names and credentials
- **PostgreSQL**: Using `@modelcontextprotocol/server-postgres` with credentials `DoRadmin:1232@172.30.98.213:5432/DoR`
- **Redis**: Fixed package from `@redis/mcp-redis` to `redis-mcp` with connection `redis://172.30.98.214:6379`
- **Git Server**: Fixed package from `@modelcontextprotocol/server-git` to `mcp-git` with repository path
- **Mermaid Server**: Using `@peng-shawn/mermaid-mcp-server`
- **SSH Server**: Using `mcp-ssh` for direct container debugging
- **Filesystem Server**: Using `@modelcontextprotocol/server-filesystem`
- **Debug Output**: Faculty updates contain debug print statements (lines 101-102, 514)

### CRITICAL DATA PERSISTENCE FIX
- **CRITICAL BUG FIX**: Migrated student and faculty updates from in-memory storage to PostgreSQL database
- **Root Cause**: Agenda items were lost on container restart because they were stored in-memory only
- **Solution**: Updated all CRUD operations for student/faculty updates to use PostgreSQL database
- **Files Modified**: 
  - `backend/app/api/endpoints/updates.py` - Student updates now use database
  - `backend/app/api/endpoints/faculty_updates.py` - Faculty updates now use database
- **Result**: All agenda items (student updates, faculty announcements) now persist through restarts
- **Impact**: No more data loss on deployment or container restart!
- **Technical Details**: Converted in-memory `STUDENT_UPDATES_DB` and `FACULTY_UPDATES_DB` to use SQLAlchemy ORM with PostgreSQL

### PostgreSQL Enum Case Mismatch Fix
- **CRITICAL BUG FIX**: Fixed user role update failures caused by PostgreSQL enum case mismatch
- **Root Cause**: Database had inconsistent mix of uppercase (`ADMIN`, `STUDENT`) and lowercase (`faculty`, `secretary`) enum values
- **Solution**: Added missing uppercase enum values (`FACULTY`, `SECRETARY`) to database for full compatibility
- **Files Modified**: `backend/app/api/endpoints/auth.py`, `backend/app/db/models/user.py`
- **Result**: User role changes (admin ↔ faculty ↔ student) now work correctly
- **Technical Details**: See `docs/technical-notes.md` for complete investigation and solution

### JSON Response Parsing Fix
- **BUG FIX**: Fixed user deletion failing with "Failed to execute 'json' on 'Response': Unexpected end of JSON input"
- **Root Cause**: Frontend trying to parse JSON from HTTP 204 No Content responses (empty body)
- **Solution**: Updated `frontend/src/lib/api/index.js` to handle empty responses and 204 status codes
- **Cache Busting**: Added timestamp-based asset naming in Vite config to prevent cached JavaScript issues

### Port Configuration Standardization  
- **CONFIGURATION CHANGE**: Updated frontend port from 7117 to 1717 per user preference
- **Files Updated**: `docker-entrypoint.sh`, `Dockerfile`, `deploy.sh`, all documentation
- **Network**: Uses br0 static IP (172.30.98.177) with Nginx reverse proxy
- **URLs**: Frontend at port 1717, backend at port 8000, SSL via dd.kronisto.net

### Meeting Calendar Database Fix
- **CRITICAL DATABASE FIX**: Moved meeting calendar from in-memory storage to PostgreSQL persistence
- **Data Recovery**: Your calendar meetings are now permanently saved to database and won't be lost on restart
- **Calendar Safety**: All future meeting data will persist through server restarts and deployments
- **Database CRUD**: All meeting operations (create, read, update, delete) now use PostgreSQL
- **Agenda Persistence**: Meeting agendas will now be maintained permanently

### File Upload/Download System Fix 
- **CRITICAL FIX**: Replaced mock file storage with real file persistence to `/config/workspace/gitea/DoR-Dash/uploads/`
- **Binary File Support**: Fixed corrupted downloads for PPT/PPTX and other binary files 
- **Proper Media Types**: Added correct MIME types for PowerPoint, PDF, Word, Excel files
- **Unique File Names**: Prevents conflicts with timestamp-based naming `update_{id}_file_{id}_{timestamp}.ext`
- **Error Handling**: Clear messages for missing files vs. old uploads before file storage

### Student Self-Registration System 
- **Student Registration Portal** (`/register`): Students can self-register without admin assistance
- **Admin Approval Workflow** (`/admin/registration`): Admins can review, approve, or reject registration requests
- **Authentication Integration**: Approved registrations automatically create user accounts with "student" role
- **Navigation Enhancement**: Added registration link to login page and admin panel
- **Security**: Registration page bypasses authentication, follows same styling as login page

### Meeting Management System
- Enhanced calendar functionality with drag-and-drop meeting management
- Meeting creation popup with predefined meeting types
- Agenda system that compiles student and faculty updates by meeting
- File upload/download support for updates (50MB limit)
- Expandable/collapsible agenda sections for better readability

### Architecture Changes
- Removed mock exam functionality
- Increased file upload limits from 10MB to 50MB
- Fixed reverse proxy compatibility with relative API paths
- Improved meeting-based workflow over presentation-based system
- Eliminated all mock/demo authentication behavior

### File Upload Features
- Multiple file support for student updates
- File download with mock content generation
- Integration with meeting agenda display
- Proper permission controls for file access

## 🚨 LIVE DATA WARNING 🚨

**CRITICAL: This application now contains live user data and is actively being used.**

### Live Data Locations:
1. **User Accounts** (`backend/app/api/endpoints/auth.py` - `USERS_DB`) ⚠️ *IN-MEMORY*
2. **📚 STUDENT UPDATES** (`PostgreSQL` - **PERSISTENT DATABASE**) ✅ *SAFE*
3. **👨‍🏫 FACULTY UPDATES** (`PostgreSQL` - **PERSISTENT DATABASE**) ✅ *SAFE*
4. **📅 MEETING CALENDAR** (`PostgreSQL` - **PERSISTENT DATABASE**) ✅ *SAFE*
5. **Registration Requests** (`backend/app/api/endpoints/registration.py` - `REGISTRATION_REQUESTS`) ⚠️ *IN-MEMORY*
6. **🗂️ UPLOADED FILES** (`/config/workspace/gitea/DoR-Dash/uploads/` - **PERSISTENT ON DISK**) ✅ *SAFE*

### Development Safety Rules:
- **NEVER** reset or clear in-memory data stores during development (User Accounts, Registration Requests)
- **NEVER** change initialization logic that would overwrite existing users
- **NEVER** delete or modify files in `/uploads/` directory
- **ALWAYS** preserve existing data when modifying data structures
- **TEST CAREFULLY** before pushing changes that modify user data handling
- **DATABASE SAFETY**: Student/Faculty updates and meetings are now persistent in PostgreSQL and safe from restarts!

### Safe Modification Practices:
- Add new users by appending to existing `USERS_DB`
- Extend data models by adding optional fields with defaults
- Test data modifications on a copy before applying to live data
- When debugging, read data rather than modifying it
- Use conditional logic to avoid overwriting existing entries

## 🤖 Specialized Agent System

DoR-Dash uses a specialized agent architecture for efficient task management. Each agent has domain expertise while sharing project context.

### Available Specialized Agents

1. **Website Testing Agent** (`agents/WEBSITE_TESTING_AGENT.md`)
   - End-to-end testing, API validation, performance testing
   - Authentication testing and error scenario validation
   - Comprehensive test reporting and regression testing

2. **Database Management Agent** (`agents/DATABASE_AGENT.md`)
   - PostgreSQL schema management and migrations
   - Data integrity checks and performance optimization
   - Backup/recovery and database health monitoring

3. **UI Management Agent** (`agents/UI_AGENT.md`)
   - SvelteKit frontend development and component architecture
   - Responsive design, accessibility, and user experience
   - Performance optimization and build management

4. **LLM Integration Agent** (`agents/LLM_AGENT.md`)
   - Ollama API integration and AI-assisted features
   - Text refinement, summarization, and academic writing assistance
   - Natural language processing and intelligent automation

5. **Repository Management Agent** (`agents/REPOSITORY_AGENT.md`)
   - Git operations, branch management, and version control
   - Code refactoring, project structure optimization
   - Documentation management and code quality standards

### Quick Agent Deployment Subroutines

See `agents/SUBROUTINES.md` for comprehensive quick-access commands. Here are the most common patterns:

#### Single-Letter Ultra-Fast Access
```bash
# W = Website Testing Agent - Quick health check
Task(description="W", prompt="Website Testing Agent: Quick health check - frontend/backend status, basic auth test, API connectivity.")

# D = Database Agent - Quick database check  
Task(description="D", prompt="Database Agent: Quick database check - connection, schema integrity, user accounts status.")

# U = UI Agent - Quick frontend check
Task(description="U", prompt="UI Agent: Quick frontend check - build status, component integrity, basic UX validation.")

# L = LLM Agent - Quick Ollama check
Task(description="L", prompt="LLM Agent: Quick Ollama check - service status, model availability, basic text generation test.")

# R = Repository Agent - Quick repo check
Task(description="R", prompt="Repository Agent: Quick repo check - git health, project structure, code quality, documentation status.")
```

#### Full Deployment Commands
```bash
# Comprehensive website testing
Task(description="Test Web", prompt="Deploy Website Testing Agent. Run comprehensive test suite: status check, auth testing, API validation, error handling. Provide executive summary with pass/fail status.")

# Database management and health check
Task(description="DB Admin", prompt="Deploy Database Management Agent. Check database health, verify schema integrity, ensure all tables exist with proper data.")

# UI development and optimization
Task(description="UI Dev", prompt="Deploy UI Management Agent. Review frontend architecture, check component structure, validate user experience, report UI issues.")

# LLM integration and AI features
Task(description="LLM Setup", prompt="Deploy LLM Integration Agent. Check Ollama connectivity, test AI features, validate text refinement capabilities.")

# Repository management and code quality
Task(description="Repo Admin", prompt="Deploy Repository Management Agent. Analyze repository structure, check code quality, validate documentation, assess git health.")
```

#### Emergency and Coordination Commands
```bash
# Full system health check
Task(description="System Check", prompt="Deploy all agents in sequence: 1) Repository Agent - check git health, 2) Database Agent - verify schema, 3) Website Testing Agent - test functionality, 4) UI Agent - check frontend, 5) LLM Agent - verify AI features. Provide unified status report.")

# Emergency database recovery
Task(description="Emergency Fix", prompt="Deploy Database Agent for emergency recovery: fix critical database issues, restore user accounts, ensure application functionality. Then deploy Website Testing Agent to verify recovery.")
```

### Agent Integration Best Practices

1. **Hierarchical Knowledge**: Each agent inherits from main CLAUDE.md then applies domain-specific expertise
2. **Cross-Agent Coordination**: Agents can collaborate on complex tasks (e.g., DB Agent fixes schema, then Testing Agent validates)
3. **Efficient Task Distribution**: Use specialized agents for their expertise areas rather than general-purpose commands
4. **Quick Access Patterns**: Use single-letter shortcuts for frequent operations, full commands for comprehensive tasks

For the complete list of agent subroutines and shortcuts, reference `agents/SUBROUTINES.md`.