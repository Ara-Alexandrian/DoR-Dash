# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Project State (June 2025)

DoR-Dash is a mature research dashboard application for Mary Bird Perkins Cancer Center with the following production-ready systems:

### Core Architecture
- **Frontend**: SvelteKit with TypeScript, TailwindCSS, responsive design
- **Backend**: FastAPI with Python, SQLAlchemy, PostgreSQL
- **Deployment**: Docker containers on Unraid with reverse proxy (Nginx)
- **Authentication**: JWT-based with role-based access control (Student, Faculty, Secretary, Admin)
- **Infrastructure**: MCP (Model Context Protocol) servers for debugging and development

### Production Features (2025)
- **Authentication System**: Robust JWT authentication with session recovery and token refresh
- **Presentation Assignment System**: Full grillometer feedback system with file uploads
- **Meeting Management**: Agenda creation with integrated presentation assignments
- **Update Submission**: Student progress updates with LLM text refinement (Ollama/Gemma)
- **User Management**: Admin user CRUD with avatar support and role management
- **Quality Assurance**: Comprehensive QA testing suite with automated reports
- **Theme System**: Multiple themes (Light, Dark, Dracula, MBP, LSU) with contrast optimization
- **File Management**: Secure file uploads with presentation assignment integration
- **Dashboard**: Real-time statistics and presentation assignment management

### Recent Major Updates (June 2025)
- **Authentication Overhaul**: Resolved JWT token storage race conditions and parameter mismatches
- **Sidebar Race Condition Fix**: Fixed sidebar visibility issues after login
- **Repository Cleanup**: Comprehensive cleanup removing 47 debug files and 10,489 lines of clutter
- **Documentation Organization**: All .md files moved to /docs directory for better structure
- **Deployment Automation**: Smart rebuild scripts with cache busting and health checks
- **MCP Integration**: SSH servers configured for container debugging and development
- **Presentation Files**: File upload system integrated with presentation assignments

## Quality Assurance (QA) Structure

The project now has a comprehensive QA system:

### QA Directory Structure
```
qa/
├── LLM-QA/               # LLM text refinement QA reports
├── Validation/           # General system validation reports  
├── database/             # Database testing scripts
├── integration/          # API integration tests
└── utils/                # Testing utilities
```

### LLM Testing Suite
- **Endpoint**: `/api/v1/text-testing/run-tests` (admin only)
- **Purpose**: Validate conservative LLM behavior
- **Output**: Automatic report generation in `qa/LLM-QA/`
- **Model**: Gemma 3 4B on Ollama server (172.30.98.14:11434)

### Test Cases Cover:
- Basic grammar fixes
- Announcement formatting (no emojis/dramatic headers)
- Challenge descriptions
- Technical content preservation
- Length expansion limits (max 30%)

### When to Run LLM Tests:
- After changing LLM prompts
- After model updates
- Before production deployments
- When text refinement issues are reported

See `qa/README.md` for detailed usage instructions.

## Presentation Assignment System

The project now features a comprehensive presentation assignment system that integrates faculty assignment capabilities with meeting agenda management.

### Core Features
- **Faculty/Admin Assignment Interface**: Located at `/presentation-assignments`
- **Meeting Integration**: Assignments automatically appear in meeting agendas
- **Grillometer System**: Faculty can set feedback intensity using 🧊 (Relaxed), 🔥 (Moderate), ☢️ (Intense)
- **Requirement Tracking**: Checkbox-based requirements (slides, presentation, data/results, aims, time management, other)
- **Completion Tracking**: Assignment status and completion date management

### Database Structure
```sql
presentation_assignments table:
- id, student_id, assigned_by_id, meeting_id
- title (tentative title), description, presentation_type
- duration_minutes, requirements, due_date
- grillometer_novelty, grillometer_methodology, grillometer_delivery (1-3 scale)
- is_completed, completion_date, notes
```

### API Endpoints
- `GET/POST /api/v1/presentation-assignments/` - List/create assignments
- `GET/PUT/DELETE /api/v1/presentation-assignments/{id}` - Manage specific assignments
- `GET /api/v1/meetings/{id}/agenda` - Now includes presentation assignments

### Frontend Integration
- **Assignment Page**: `/presentation-assignments` with inline editing and grillometer controls
- **Meeting Agendas**: Assignments displayed in "Assigned Presentations" section
- **Timeline Integration**: Assignments appear in meeting schedule with calculated time slots
- **Role-based UI**: Faculty-only visibility for grillometer settings and notes

### Grillometer System
The grillometer provides faculty with a way to guide feedback intensity across three dimensions:
- **Novelty Assessment**: How critically to assess originality and innovation
- **Methodology Review**: How rigorously to examine research methods  
- **Presentation Delivery**: How critically to evaluate presentation skills

### Recent Fixes
- **JSON Serialization**: Fixed FastAPI serialization of SQLAlchemy objects in meeting agenda API
- **Database Enum**: Corrected presentation_type field from String to Enum for proper validation
- **UI Improvements**: Updated icons, alphabetical sorting, and "Student" → "Presenter" labeling

## MCP SSH Server Configuration

MCP (Model Context Protocol) SSH servers are configured to provide secure access to containers on the same subnet:

### Available MCP Servers
- **ssh-dor-dash**: Main DoR-Dash application container (172.30.98.177)
- **ssh-postgres**: PostgreSQL database container (172.30.98.213)
- **ssh-redis**: Redis cache container (172.30.98.214)
- **ssh-ollama**: Ollama AI server container (172.30.98.14)
- **puppeteer**: Visual testing and UI validation server (NEW)
- **postgres**: Direct PostgreSQL database connection
- **redis**: Direct Redis cache connection
- **mermaid**: Diagram generation server
- **github**: GitHub repository integration

### Configuration Files
- `mcp-servers.json`: Main MCP server definitions
- `ssh-config.json`: DoR-Dash container SSH credentials
- `ssh-postgres-config.json`: PostgreSQL container configuration
- `ssh-redis-config.json`: Redis container configuration
- `ssh-ollama-config.json`: Ollama container configuration

### Setup Instructions
1. Run the setup script: `./setup-mcp-ssh.sh`
2. Test connectivity: `ssh root@172.30.98.177`
3. See `docs/MCP_SSH_SETUP.md` for detailed configuration

### Security Notes
- Change default passwords immediately in production
- Use SSH keys instead of passwords when possible
- Restrict SSH access to specific IP addresses
- Regular security audits recommended

[... Rest of the previous content remains unchanged ...]