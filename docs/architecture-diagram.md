# DoR-Dash Architecture Diagram

**Last Updated:** June 27, 2025  
**System Status:** Production-Ready with Comprehensive Authentication & Repository Cleanup

## System Architecture Overview

```mermaid
graph TB
    subgraph "External Access"
        User[👤 User Browser]
        SSL[🔒 SSL/HTTPS]
    end

    subgraph "Reverse Proxy Layer"
        NPM[📡 Nginx Proxy Manager<br/>dd.kronisto.net]
    end

    subgraph "Docker Network (br0: 172.30.98.177)"
        subgraph "Frontend Container"
            Frontend[🎨 SvelteKit Frontend<br/>Port: 1717<br/>Custom Express Server + SPA Routing]
        end

        subgraph "Backend Container"
            Backend[⚡ FastAPI Backend<br/>Port: 8000<br/>Python/Uvicorn + SQLAlchemy ORM]
        end

        subgraph "Database Container"
            PostgreSQL[(🗄️ PostgreSQL<br/>Port: 5432<br/>Complete Data Persistence<br/>Users, AgendaItems, Meetings)]
        end

        subgraph "Cache Container"
            Redis[(🚀 Redis Cache<br/>Port: 6379<br/>Session & Performance Cache Only)]
        end

        subgraph "AI Container"
            Ollama[🤖 Ollama API<br/>Port: 11434<br/>Gemma 3 4B (CPU/RAM)<br/>Text Refinement]  
        end

        subgraph "QA System"
            QA[📊 Quality Assurance Agent<br/>Automated Testing & Validation<br/>Health Monitoring]
        end
    end

    subgraph "File Storage"
        Uploads[📁 File Storage<br/>/uploads/<br/>Persistent Disk + DB Metadata]
    end

    User --> SSL
    SSL --> NPM
    NPM --> Frontend
    NPM --> Backend
    Frontend --> Backend
    Backend --> PostgreSQL
    Backend --> Redis
    Backend --> Ollama
    Backend --> Uploads
    QA --> Frontend
    QA --> Backend
    QA --> PostgreSQL
    QA --> Redis
```

## Data Flow Architecture (Updated June 2025)

```mermaid
flowchart TD
    subgraph "Authentication Flow"
        A1[User Login] --> A2[JWT Token Generation]
        A2 --> A3[Token Storage in Redis]
        A3 --> A4[Role-based Access Control]
    end

    subgraph "Student Update Flow"
        S1[Student Submits Update] --> S2[AI Text Refinement via Ollama]
        S2 --> S3[Store in PostgreSQL AgendaItem]
        S3 --> S4[Associate Files in Database]
        S4 --> S5[Display in Meeting Agenda]
    end

    subgraph "Faculty Update Flow"
        F1[Faculty Submits Update] --> F2[Store in PostgreSQL AgendaItem]
        F2 --> F3[Associate Files in Database]
        F3 --> F4[Display in Meeting Agenda]
    end

    subgraph "Meeting Management Flow"
        M1[Create Meeting] --> M2[Store in PostgreSQL]
        M2 --> M3[Generate Agenda from AgendaItems]
        M3 --> M4[Calendar Display]
    end

    subgraph "File Upload Flow"
        U1[File Upload Request] --> U2[Validate File Type/Size]
        U2 --> U3[Store in /uploads/ Directory]
        U3 --> U4[Save Metadata to PostgreSQL]
        U4 --> U5[Associate with AgendaItem]
    end

    subgraph "QA Validation Flow"
        Q1[Automated Health Check] --> Q2[Test All System Components]
        Q2 --> Q3[Generate Timestamped Report]
        Q3 --> Q4[Traffic Light Status Update]
    end

    A4 --> S1
    A4 --> F1
    A4 --> M1
    A4 --> U1
    Q1 --> Q4
```

## Database Schema (Unified AgendaItem Model)

```mermaid
erDiagram
    USERS ||--o{ AGENDA_ITEMS : creates
    USERS ||--o{ MEETINGS : creates
    USERS ||--o{ REGISTRATION_REQUESTS : submits
    MEETINGS ||--o{ AGENDA_ITEMS : contains
    AGENDA_ITEMS ||--o{ FILE_UPLOADS : has

    USERS {
        int id PK
        string username
        string email
        string password_hash
        enum role "ADMIN, FACULTY, STUDENT, SECRETARY"
        string full_name
        datetime created_at
        boolean is_active
    }

    AGENDA_ITEMS {
        int id PK
        int meeting_id FK
        int user_id FK
        string item_type "student_update, faculty_update, announcement"
        string title
        jsonb content "Polymorphic content storage"
        boolean is_presenting
        datetime created_at
        datetime updated_at
    }

    MEETINGS {
        int id PK
        string title
        datetime date
        string description
        string meeting_type
        int created_by FK
        datetime created_at
    }

    FILE_UPLOADS {
        int id PK
        string filename
        string original_filename
        string content_type
        integer file_size
        string file_path
        int user_id FK
        int agenda_item_id FK
        datetime uploaded_at
    }

    REGISTRATION_REQUESTS {
        int id PK
        string username
        string email
        string full_name
        string password_hash
        enum status "pending, approved, rejected"
        datetime created_at
        int processed_by FK
        datetime processed_at
    }

    LEGACY_STUDENT_UPDATES {
        string note "DEPRECATED - Migrated to AGENDA_ITEMS"
    }

    LEGACY_FACULTY_UPDATES {
        string note "DEPRECATED - Migrated to AGENDA_ITEMS"
    }
```

## API Endpoints Structure (Current)

```mermaid
graph LR
    subgraph "Authentication API (/auth)"
        Auth1[POST /login]
        Auth2[POST /logout]
        Auth3[GET /profile]
        Auth4[POST /refresh]
    end

    subgraph "User Management API (/users)"
        User1[GET /users]
        User2[POST /users]
        User3[PUT /users/{id}]
        User4[DELETE /users/{id}]
        User5[PUT /users/{id}/role]
    end

    subgraph "Unified Agenda API (/agenda-items)"
        Agenda1[GET /agenda-items]
        Agenda2[POST /agenda-items]
        Agenda3[PUT /agenda-items/{id}]
        Agenda4[DELETE /agenda-items/{id}]
    end

    subgraph "Legacy Updates API (/updates, /faculty-updates)"
        Update1[GET /updates - Student]
        Update2[POST /updates - Student]
        Update3[GET /faculty-updates]
        Update4[POST /faculty-updates]
        Update5[POST /text/refine-text]
    end

    subgraph "Meetings API (/meetings)"
        Meet1[GET /meetings]
        Meet2[POST /meetings]
        Meet3[PUT /meetings/{id}]
        Meet4[DELETE /meetings/{id}]
        Meet5[GET /meetings/{id}/agenda]
    end

    subgraph "Files API (/files)"
        File1[POST /upload]
        File2[GET /{file_id}]
        File3[DELETE /{file_id}]
    end

    subgraph "Registration API (/registration)"
        Reg1[POST /register]
        Reg2[GET /requests]
        Reg3[POST /requests/{id}/approve]
        Reg4[POST /requests/{id}/reject]
    end

    subgraph "QA API (/qa)"
        QA1[GET /health]
        QA2[POST /validate]
        QA3[GET /reports]
    end
```

## Component Architecture (Enhanced)

```mermaid
graph TB
    subgraph "Frontend Components"
        subgraph "Pages"
            P1[Dashboard]
            P2[Calendar]
            P3[Submit Updates]
            P4[Admin Panel]
            P5[Login/Register]
        end

        subgraph "Stores (Svelte)"
            S1[Auth Store]
            S2[Theme Store]
            S3[User Data Store]
            S4[Meeting Store]
        end

        subgraph "API Layer"
            API1[Auth API]
            API2[Users API]
            API3[Meetings API]
            API4[AgendaItems API]
            API5[Files API]
        end

        subgraph "Express Server"
            EXP1[SPA Routing]
            EXP2[Static File Serving]
            EXP3[Health Endpoints]
        end
    end

    subgraph "Backend Services"
        subgraph "Core Services"
            C1[Authentication Service]
            C2[Permission Service]
            C3[Session Management]
            C4[Security Service]
        end

        subgraph "Business Logic"
            B1[User Management]
            B2[AgendaItem Processing]
            B3[Meeting Management]
            B4[File Handling]
            B5[AI Integration]
            B6[QA Validation]
        end

        subgraph "Data Layer"
            D1[SQLAlchemy ORM]
            D2[PostgreSQL Database]
            D3[File System]
            D4[Redis Cache Layer]
        end
    end

    P1 --> S1
    P2 --> S4
    P3 --> S1
    P4 --> S1
    P5 --> S1

    S1 --> API1
    S3 --> API2
    S4 --> API3
    P2 --> API4
    P3 --> API5

    API1 --> C1
    API2 --> B1
    API3 --> B3
    API4 --> B2
    API5 --> B4

    C1 --> D2
    B1 --> D1
    B2 --> D1
    B3 --> D1
    B4 --> D3
    B5 --> Ollama
    B6 --> D2

    C2 --> C1
    C3 --> D4
    D1 --> D2

    EXP1 --> P1
    EXP1 --> P2
    EXP1 --> P3
    EXP1 --> P4
    EXP1 --> P5
```

## Security & Authentication Flow (Updated)

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (Express)
    participant B as Backend (FastAPI)
    participant R as Redis Cache
    participant DB as PostgreSQL
    participant QA as QA Agent

    U->>F: Login Request
    F->>B: POST /auth/login
    B->>DB: Validate Credentials (PostgreSQL)
    DB-->>B: User Data
    B->>B: Generate JWT Token
    B->>R: Store Session
    B-->>F: JWT Token + User Info
    F->>F: Store Token in Memory
    F-->>U: Redirect to Dashboard

    Note over U,DB: Subsequent Requests

    U->>F: Access Protected Resource
    F->>B: API Request + JWT Header
    B->>B: Validate JWT
    B->>R: Check Session
    R-->>B: Session Valid
    B->>B: Check Permissions
    B->>DB: Query Data (AgendaItems/Users)
    DB-->>B: Data Response
    B-->>F: Resource Data
    F-->>U: Display Resource

    Note over QA: Continuous Monitoring

    QA->>F: Health Check
    QA->>B: API Validation
    QA->>DB: Database Health
    QA->>R: Cache Performance
```

## Deployment Architecture (Docker Compose)

```mermaid
graph TB
    subgraph "Host Environment (Unraid)"
        subgraph "Docker Compose Stack"
            DC[docker-compose.yml]
            ENV[.env Configuration]
        end

        subgraph "Network Configuration"
            BR0[br0 Bridge Network<br/>172.30.98.177]
            PORTS[Port Mapping<br/>1717:1717, 8000:8000]
        end

        subgraph "Volume Mounts"
            V1[./uploads:/app/uploads]
            V2[./logs:/app/logs]
            V3[postgres_data:/var/lib/postgresql/data]
            V4[redis_data:/data]
        end

        subgraph "Scripts & Tools"
            START[start.sh]
            STOP[stop.sh]
            DEPLOY[deploy.sh]
            QA_SCRIPT[qa-validation.sh]
        end
    end

    subgraph "External Services"
        DNS[dd.kronisto.net]
        SSL_CERT[SSL Certificate]
        POSTGRES_EXT[External PostgreSQL<br/>172.30.98.213:5432]
        REDIS_EXT[External Redis<br/>172.30.98.214:6379]
        OLLAMA_EXT[External Ollama<br/>172.30.98.14:11434]
    end

    DC --> BR0
    DC --> V1
    DC --> V2
    DC --> V3
    DC --> V4
    
    START --> DC
    DEPLOY --> DC
    QA_SCRIPT --> DC
    
    DNS --> SSL_CERT
    SSL_CERT --> NPM
    
    DC --> POSTGRES_EXT
    DC --> REDIS_EXT
    DC --> OLLAMA_EXT
```

## Current Architecture Status (June 2025)

### ✅ PRODUCTION-READY FEATURES
1. **Robust Authentication System** - JWT with session recovery and token refresh
2. **Presentation Assignment System** - Complete grillometer feedback with file uploads
3. **Meeting Integration** - Seamless presentation assignment display in agendas
4. **Advanced Theme System** - Five themes with accessibility compliance
5. **Repository Organization** - Clean structure with documentation in /docs
6. **MCP Infrastructure** - SSH servers for debugging and container access
7. **Quality Assurance** - Automated testing suite with health monitoring
8. **Deployment Automation** - Smart rebuild scripts with cache busting

### 🎯 CURRENT STATE (June 2025)
- **Authentication:** Comprehensive JWT system with race condition fixes
- **Presentation Management:** Full grillometer system with faculty assignment interface
- **File Management:** Integrated file uploads with presentation assignments
- **Themes:** Five distinct themes with contrast optimization
- **Documentation:** All .md files organized in /docs directory
- **Container Access:** MCP SSH servers for development and debugging
- **Repository:** Clean organization with 47 debug files removed

### 🔧 RECENT MAJOR FIXES (June 2025)
1. **Authentication Overhaul:** Resolved JWT token storage race conditions
2. **Sidebar Visibility Fix:** Fixed missing sidebar after successful login
3. **Repository Cleanup:** Removed 10,489 lines of development clutter
4. **Documentation Organization:** Proper structure with docs in /docs
5. **Deployment Streamlining:** Enhanced Docker deployment with health checks

### 🎉 SYSTEM HIGHLIGHTS
- **Zero Data Loss:** Complete database persistence with proper relationships
- **Secure Authentication:** Token refresh mechanisms with session recovery
- **Faculty Tools:** Grillometer feedback system for presentation guidance
- **User Experience:** Responsive design with accessibility-compliant themes
- **Developer Experience:** MCP infrastructure for efficient debugging
- **Quality Assurance:** Comprehensive testing with automated validation

---

**Architecture Evolution:**
- **V1.0 (2024):** Basic functionality with in-memory storage
- **V2.0 (Early 2025):** Database persistence and unified models
- **V2.1 (June 2025):** Advanced theming and presentation management
- **V2.2 (June 2025):** Complete grillometer system implementation
- **V2.3 (June 2025):** Authentication fixes and repository organization

This architecture provides a production-ready research dashboard with robust authentication, advanced presentation management, and comprehensive quality assurance.