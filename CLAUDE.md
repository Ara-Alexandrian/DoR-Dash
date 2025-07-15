# 🤖 CLAUDE.md - AI Assistant Context & Project Guide

> **Context file for AI assistants working on DoR-Dash**
> 
> This document provides comprehensive project context, recent fixes, and development guidance for AI assistants (Claude, GPT, etc.) working on the DoR-Dash academic research management platform.

---

## 🎯 Project Overview

**DoR-Dash** (Dose of Reality Dashboard) is a production-ready academic research management platform serving the Mary Bird Perkins Cancer Center. Built with FastAPI + SvelteKit, it manages student research meetings, presentations, and progress tracking with AI-powered text refinement.

### 🏗️ System Architecture

```
Frontend (SvelteKit) → Backend (FastAPI) → PostgreSQL + Redis → Ollama AI
```

**Key Components:**
- **Authentication**: JWT-based with Redis session management
- **Database**: PostgreSQL with Alembic migrations
- **AI Integration**: Ollama + Gemma 3 4B for text refinement
- **Deployment**: Docker containerization with Unraid hosting
- **Themes**: 5 distinct themes (Light, Dark, Dracula, MBP, LSU)

---

## 🔧 Recent Major Fixes (January 2025)

### 1. **Authentication System Overhaul**
**Issue**: Infinite token refresh loops causing server flooding
**Fix**: Added rate limiting, proper error handling, and fixed `logout()` references
```javascript
// Fixed infinite loop with rate limiting
let refreshAttempts = 0;
const MAX_REFRESH_ATTEMPTS = 3;
const REFRESH_COOLDOWN = 60000; // 1 minute
```

### 2. **Navigation & Icon Enhancements**
**Issue**: Plain, low-contrast navigation icons
**Fix**: Replaced with vivid, high-contrast line-art icons with animations
- Enhanced all navigation icons with 2.5px stroke width
- Added drop shadows and visual accents
- Created animated easter egg eye icon (closed → opens on hover)

### 3. **Presentation Assignment System Fixes**
**Issue**: 500 errors on CREATE, UPDATE, DELETE operations
**Root Cause**: Missing `meeting_id` field in update schema + database table issues
**Fix**: 
- Added `meeting_id` to `PresentationAssignmentUpdate` model
- Fixed missing `presentation_assignment_files` table
- Added comprehensive error handling with rollback mechanisms

### 4. **Dashboard Statistics Navigation**
**Issue**: Broken stat cards and "Upcoming" button
**Fix**: Converted buttons to proper anchor links with correct routing
```javascript
// Before: <button on:click={() => window.location.href = '/agenda?filter=upcoming'}>
// After: <a href="/agenda?filter=upcoming">
```

---

## 📁 Project Structure

```
DoR-Dash/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/      # API route handlers
│   │   ├── db/models/         # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   └── core/              # Configuration & utilities
│   ├── alembic/               # Database migrations
│   └── requirements.txt       # Python dependencies
├── frontend/                   # SvelteKit frontend
│   ├── src/
│   │   ├── routes/            # Page components
│   │   ├── lib/               # Utilities & stores
│   │   └── components/        # Reusable UI components
│   └── package.json           # Node.js dependencies
├── scripts/                    # Automation scripts
│   ├── deploy.sh              # Docker deployment
│   ├── unraid-aliases.sh      # Server command aliases
│   └── local-aliases.sh       # Development aliases
├── docker/                     # Docker configuration
├── docs/                       # Documentation
└── .env                        # Environment variables
```

---

## 🚨 Critical Issues Fixed

### Database Schema Issues
**Problem**: Missing `presentation_assignment_files` table causing 500 errors
**Solution**: Table exists but migrations may need reapplication
```sql
-- Table structure verified:
presentation_assignment_files (
    id SERIAL PRIMARY KEY,
    presentation_assignment_id INTEGER REFERENCES presentation_assignments(id),
    uploaded_by_id INTEGER REFERENCES "user"(id),
    filename VARCHAR(255),
    -- ... other fields
);
```

### Authentication Race Conditions
**Problem**: Token refresh loops and session management issues
**Solution**: Implemented proper error handling and rate limiting
```javascript
// Key fix: Replaced all logout() calls with clearAuthState()
auth.clearAuthState();
if (browser) {
    goto('/login');
}
```

### Frontend Navigation
**Problem**: Icons were plain and buttons didn't navigate properly
**Solution**: Enhanced all icons and fixed navigation logic

---

## 🎨 Theme System

DoR-Dash supports 5 distinct themes:

1. **Light** - Default clean theme
2. **Dark** - Professional dark mode
3. **Dracula** - Purple/cyan accent theme
4. **MBP** - Mary Bird Perkins branded (red accents)
5. **LSU** - Louisiana State University (purple/gold)

**Implementation**: CSS classes applied to `<html>` element
```javascript
document.documentElement.classList.add(theme);
```

---

## 🔑 Key API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/auth/profile` - Get current user profile
- `POST /api/v1/auth/register` - New user registration (admin approval required)

### Presentation Assignments
- `GET /api/v1/presentation-assignments/` - List assignments
- `POST /api/v1/presentation-assignments/` - Create assignment
- `PUT /api/v1/presentation-assignments/{id}` - Update assignment (now includes meeting_id)
- `DELETE /api/v1/presentation-assignments/{id}` - Delete assignment

### File Management
- `POST /api/v1/presentation-assignments/{id}/files` - Upload file
- `GET /api/v1/presentation-assignments/{id}/files` - List files
- `DELETE /api/v1/presentation-assignments/{id}/files/{file_id}` - Delete file

---

## 🔧 Development Setup

### Quick Start
```bash
# Load development aliases
source scripts/local-aliases.sh

# For development environment
git pull origin master
./scripts/deploy.sh restart

# For production server
dorsmartrebuild  # Smart rebuild with cache
dorforcebuild    # Full rebuild (no cache)
dorupdate        # Quick restart
```

### Environment Variables (.env)
```bash
# Database
POSTGRES_SERVER=172.30.98.213
POSTGRES_USER=DoRadmin
POSTGRES_PASSWORD=1232
POSTGRES_DB=DoR

# Redis
REDIS_SERVER=172.30.98.214
REDIS_PORT=6379

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
OLLAMA_API_URL=http://172.30.98.14:11434/api/generate
```

---

## 🐛 Debugging Common Issues

### 1. **500 Errors on Presentation Assignments**
**Check**: Database table exists and API has proper error handling
```python
# Fixed with comprehensive error handling
try:
    db.commit()
    db.refresh(assignment)
except Exception as e:
    db.rollback()
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

### 2. **Authentication Loops**
**Check**: Token refresh logic and localStorage
```javascript
// Fixed: Proper rate limiting and error handling
if (refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
    clearAuthState();
    goto('/login');
}
```

### 3. **Navigation Issues**
**Check**: Use proper anchor tags instead of buttons for navigation
```svelte
<!-- Fixed: Use anchor instead of button -->
<a href="/agenda?filter=upcoming" class="card">
    <!-- content -->
</a>
```

---

## 📊 Database Models

### Key Tables
- **user** - User accounts with roles (admin, faculty, student)
- **meeting** - Research meetings with dates and agendas
- **presentation_assignments** - Faculty-assigned presentations
- **presentation_assignment_files** - File attachments for presentations
- **agenda_items** - Meeting agenda items and student updates

### Important Relationships
```sql
presentation_assignments.student_id → user.id
presentation_assignments.meeting_id → meeting.id
presentation_assignment_files.presentation_assignment_id → presentation_assignments.id
```

---

## 🚀 Deployment Commands

### Unraid Server Aliases
```bash
# Setup aliases (run once)
./scripts/unraid-aliases.sh
source ~/.bashrc

# Common commands
dorsmartrebuild  # Smart rebuild (recommended)
dorforcebuild    # Full rebuild with --no-cache
dorupdate        # Quick restart (fastest)
dorlogs          # View container logs
dorstatus        # Check container status
```

### Docker Commands
```bash
# Build and deploy
./scripts/deploy.sh rebuild

# Check status
docker ps | grep dor-dash
docker logs dor-dash

# Emergency restart
docker restart dor-dash
```

---

## 🔍 Testing & Quality Assurance

### Key Test Areas
1. **Authentication Flow** - Login, logout, token refresh
2. **Presentation Management** - Create, update, delete assignments
3. **File Uploads** - Attach files to presentations
4. **Navigation** - Dashboard stats, upcoming/completed buttons
5. **Theme Switching** - All 5 themes work correctly

### Manual Testing Checklist
- [ ] Login/logout works without infinite loops
- [ ] Presentation assignments can be created/edited/deleted
- [ ] Dashboard stat cards navigate correctly
- [ ] Icons display with high contrast
- [ ] Easter egg eye animation works
- [ ] File uploads work for presentations

---

## 📈 Performance Optimizations

### Recent Improvements
- **Caching**: Redis session management and API response caching
- **Database**: Proper indexing and foreign key constraints
- **Frontend**: Lazy loading and component optimization
- **Icons**: Optimized SVG icons with proper caching

### Monitoring
- Container health checks via Docker
- Database connection pooling
- Error logging with detailed stack traces
- Performance metrics in production

---

## 🎯 Future Development Guidelines

### Code Style
- **Backend**: Follow FastAPI best practices with proper error handling
- **Frontend**: Use SvelteKit conventions with Tailwind CSS
- **Database**: Always use migrations for schema changes
- **Icons**: Maintain 2.5px stroke width and high contrast

### Testing Strategy
- Unit tests for API endpoints
- Integration tests for authentication flow
- Manual testing for UI components
- Database migration testing

### Deployment Process
1. Develop and test in development environment
2. Commit changes with descriptive messages
3. Deploy using `dorsmartrebuild` on production server
4. Monitor logs for any issues
5. Test key functionality post-deployment

---

## 🤝 Working with AI Assistants

### Context Awareness
- **Current Status**: Production-ready with recent major fixes applied
- **Active Issues**: Generally stable, focus on new features or minor enhancements
- **Priority Areas**: User experience improvements, performance optimization

### Best Practices
- Always check existing code before implementing new features
- Use the established patterns for error handling and database operations
- Maintain consistency with the existing theme system
- Follow the project's naming conventions and file structure

### Common Commands for AI Assistants
```bash
# Check recent changes
git log --oneline -10

# View current branch status
git status

# Deploy updates
dorsmartrebuild

# View application logs
dorlogs

# Check running containers
docker ps
```

---

## 📞 Support & Resources

### Key Documentation
- [README.md](README.md) - Complete project overview
- [Technical Notes](docs/technical-notes.md) - Implementation details
- [API Documentation](docs/api/) - Endpoint reference
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production setup

### Quick References
- **Backend Port**: 8000
- **Frontend Port**: 1717
- **Database**: PostgreSQL on 172.30.98.213:5432
- **Redis**: 172.30.98.214:6379
- **AI Service**: Ollama on 172.30.98.14:11434

---

**Last Updated**: January 15, 2025  
**Version**: 2.1.0  
**Status**: Production Ready ✅

---

*This document serves as a comprehensive guide for AI assistants working on DoR-Dash. Keep it updated as the project evolves.*