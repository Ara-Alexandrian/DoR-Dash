# DoR-Dash Architecture Diagram

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
            Frontend[🎨 SvelteKit Frontend<br/>Port: 1717<br/>Vite Dev Server]
        end

        subgraph "Backend Container"
            Backend[⚡ FastAPI Backend<br/>Port: 8000<br/>Python/Uvicorn]
        end

        subgraph "Database Container"
            PostgreSQL[(🗄️ PostgreSQL<br/>Port: 5432<br/>Persistent Storage)]
        end

        subgraph "Cache Container"
            Redis[(🚀 Redis Cache<br/>Port: 6379<br/>Session & Query Cache)]
        end

        subgraph "AI Container"
            Ollama[🤖 Ollama API<br/>Port: 11434<br/>Mistral AI (CPU/RAM)]
        end
    end

    subgraph "File Storage"
        Uploads[📁 File Storage<br/>/uploads/<br/>Persistent Disk]
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
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Authentication Flow"
        A1[User Login] --> A2[JWT Token Generation]
        A2 --> A3[Token Storage in Redis]
        A3 --> A4[Role-based Access Control]
    end

    subgraph "Student Update Flow"
        S1[Student Submits Update] --> S2[AI Text Refinement via Ollama]
        S2 --> S3[Store in Memory + Files]
        S3 --> S4[Display in Meeting Agenda]
    end

    subgraph "Faculty Update Flow"
        F1[Faculty Submits Update] --> F2[Store in Memory]
        F2 --> F3[Display in Meeting Agenda]
    end

    subgraph "Meeting Management Flow"
        M1[Create Meeting] --> M2[Store in PostgreSQL]
        M2 --> M3[Generate Agenda from Updates]
        M3 --> M4[Calendar Display]
    end

    subgraph "File Upload Flow"
        U1[File Upload Request] --> U2[Validate File Type/Size]
        U2 --> U3[Store in /uploads/ Directory]
        U3 --> U4[Save Metadata to Memory]
        U4 --> U5[Associate with Update]
    end

    A4 --> S1
    A4 --> F1
    A4 --> M1
    A4 --> U1
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ STUDENT_UPDATES : creates
    USERS ||--o{ FACULTY_UPDATES : creates
    USERS ||--o{ REGISTRATION_REQUESTS : submits
    MEETINGS ||--o{ MEETING_UPDATES : contains
    STUDENT_UPDATES ||--o{ FILE_UPLOADS : has
    FACULTY_UPDATES ||--o{ FILE_UPLOADS : has

    USERS {
        string id PK
        string username
        string email
        string password_hash
        enum role "admin, student, faculty, secretary"
        string full_name
        datetime created_at
        boolean is_active
    }

    STUDENT_UPDATES {
        string id PK
        string user_id FK
        string content
        string refined_content
        datetime created_at
        string meeting_id FK
        list file_ids
    }

    FACULTY_UPDATES {
        string id PK
        string user_id FK
        string content
        datetime created_at
        string meeting_id FK
        list file_ids
    }

    MEETINGS {
        string id PK
        string title
        datetime date
        string description
        string meeting_type
        list agenda_items
        datetime created_at
    }

    FILE_UPLOADS {
        string id PK
        string filename
        string original_filename
        string content_type
        integer file_size
        string file_path
        string uploaded_by FK
        datetime uploaded_at
    }

    REGISTRATION_REQUESTS {
        string id PK
        string username
        string email
        string full_name
        string password_hash
        enum status "pending, approved, rejected"
        datetime created_at
        string processed_by FK
        datetime processed_at
    }
```

## API Endpoints Structure

```mermaid
graph LR
    subgraph "Authentication API (/auth)"
        Auth1[POST /login]
        Auth2[POST /logout]
        Auth3[GET /me]
        Auth4[POST /refresh]
    end

    subgraph "User Management API (/users)"
        User1[GET /users]
        User2[POST /users]
        User3[PUT /users/{id}]
        User4[DELETE /users/{id}]
        User5[PUT /users/{id}/role]
    end

    subgraph "Updates API (/updates)"
        Update1[GET /student]
        Update2[POST /student]
        Update3[GET /faculty]
        Update4[POST /faculty]
        Update5[POST /refine]
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
```

## Component Architecture

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
        end

        subgraph "API Layer"
            API1[Auth API]
            API2[Users API]
            API3[Meetings API]
            API4[Updates API]
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
            B2[Update Processing]
            B3[Meeting Management]
            B4[File Handling]
            B5[AI Integration]
        end

        subgraph "Data Layer"
            D1[Database Models]
            D2[In-Memory Storage]
            D3[File System]
            D4[Cache Layer]
        end
    end

    P1 --> S1
    P2 --> S1
    P3 --> S1
    P4 --> S1
    P5 --> S1

    S1 --> API1
    S3 --> API2
    P2 --> API3
    P3 --> API4

    API1 --> C1
    API2 --> B1
    API3 --> B3
    API4 --> B2

    C1 --> D2
    B1 --> D2
    B2 --> D2
    B3 --> D1
    B4 --> D3
    B5 --> Ollama

    C2 --> C1
    C3 --> D4
```

## Security & Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant R as Redis
    participant DB as PostgreSQL

    U->>F: Login Request
    F->>B: POST /auth/login
    B->>DB: Validate Credentials
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
    B-->>F: Resource Data
    F-->>U: Display Resource
```

## Deployment Architecture

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

        subgraph "Scripts"
            START[start.sh]
            STOP[stop.sh]
            DEPLOY[deploy.sh]
        end
    end

    subgraph "External Services"
        DNS[dd.kronisto.net]
        SSL_CERT[SSL Certificate]
    end

    DC --> BR0
    DC --> V1
    DC --> V2
    DC --> V3
    DC --> V4
    
    START --> DC
    DEPLOY --> DC
    
    DNS --> SSL_CERT
    SSL_CERT --> NPM
```