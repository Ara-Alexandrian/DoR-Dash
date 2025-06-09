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

## Security Practices

- Implement JWT-based authentication
- Use password hashing (bcrypt)
- Apply role-based access control
- Validate all user inputs
- Secure file upload handling
- Protect API endpoints

## Reverse Proxy Configuration

The application is designed to work behind a reverse proxy with SSL termination. See `REVERSE_PROXY_SETUP.md` for detailed configuration instructions.

**Key Configuration Points:**
- Frontend must use relative API paths (`VITE_API_URL=""`)
- Nginx proxy manager forwards `/api/*` requests to backend port 8000
- Frontend served from port 7117
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

### Meeting Calendar Database Fix (LATEST URGENT)
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
2. **Student Updates** (`backend/app/api/endpoints/updates.py` - `STUDENT_UPDATES`) ⚠️ *IN-MEMORY*
3. **Faculty Updates** (`backend/app/api/endpoints/faculty_updates.py` - `FACULTY_UPDATES`) ⚠️ *IN-MEMORY*
4. **📅 MEETING CALENDAR** (`PostgreSQL` - **PERSISTENT DATABASE**) ✅ *SAFE*
5. **Registration Requests** (`backend/app/api/endpoints/registration.py` - `REGISTRATION_REQUESTS`) ⚠️ *IN-MEMORY*
6. **🗂️ UPLOADED FILES** (`/config/workspace/gitea/DoR-Dash/uploads/` - **PERSISTENT ON DISK**) ✅ *SAFE*

### Development Safety Rules:
- **NEVER** reset or clear in-memory data stores during development
- **NEVER** change initialization logic that would overwrite existing users
- **NEVER** delete or modify files in `/uploads/` directory
- **ALWAYS** preserve existing data when modifying data structures
- **TEST CAREFULLY** before pushing changes that modify user data handling
- **BACKUP AWARENESS**: Metadata is in-memory and will be lost on server restart, but uploaded files are persistent on disk

### Safe Modification Practices:
- Add new users by appending to existing `USERS_DB`
- Extend data models by adding optional fields with defaults
- Test data modifications on a copy before applying to live data
- When debugging, read data rather than modifying it
- Use conditional logic to avoid overwriting existing entries