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