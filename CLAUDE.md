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
   - Connection: `postgresql://postgres:postgres@localhost:5432/postgres`

2. **Redis Server** (`redis`)
   - Cache management and key-value operations
   - Memory usage analysis and monitoring
   - Session data inspection and cleanup
   - Connection: `redis://localhost:6379`

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

5. **Git Server** (`git`)
   - Advanced version control operations
   - Repository analysis and health checks
   - Commit history and branch management
   - Security scanning for exposed credentials

### Using MCP Tools

These servers provide additional capabilities beyond standard Claude Code tools:
- **Database Operations**: Query live PostgreSQL data directly
- **Cache Analysis**: Inspect Redis keys and performance metrics
- **File Management**: Advanced operations on project files and uploads
- **Documentation**: Generate visual diagrams for architecture documentation
- **Repository Management**: Enhanced git operations and security analysis

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

### CRITICAL DATA PERSISTENCE FIX (LATEST CRITICAL)
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