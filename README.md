# DoR-Dash (Dose of Reality Dashboard)

A responsive, high-quality web application for managing student research meetings. DoR-Dash enables users to log in, submit bi-monthly updates with AI-assisted refinement, request support, and share presentation files.

## Features

- User authentication with role-based access control
- Bi-monthly update submission with AI-assisted text refinement
- Support request system
- File upload and sharing
- Dynamic roster management
- Automated presentation assignment
- Comprehensive admin controls

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: SvelteKit with Tailwind CSS
- **Database**: PostgreSQL
- **Caching**: Redis
- **AI Integration**: Ollama API with Mistral (CPU/RAM based)
- **Deployment**: Docker and Docker Compose

## Getting Started

### Prerequisites

- Python 3.8+ with venv
- Node.js and npm
- Access to PostgreSQL database (172.30.98.213:5432)
- Access to Redis server (172.30.98.214:6379)
- Ollama with Mistral AI model running locally at 172.30.98.14:11434

### Quick Start

The easiest way to set up and run the project is using the start script:

```bash
./scripts/start.sh
```

This script will:
1. Create the `.env` file with default values
2. Set up a Python virtual environment
3. Install backend and frontend dependencies
4. Apply database migrations
5. Start both the backend and frontend servers

To stop the application:

```bash
./scripts/stop.sh
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DoR-Dash
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   # Database Configuration
   POSTGRES_SERVER=172.30.98.213
   POSTGRES_PORT=5432
   POSTGRES_USER=DoRadmin
   POSTGRES_PASSWORD=1232
   POSTGRES_DB=DoR

   # Redis Configuration
   REDIS_SERVER=172.30.98.214
   REDIS_PORT=6379

   # JWT Settings
   SECRET_KEY=your_secure_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Ollama API Configuration
   OLLAMA_API_URL=http://172.30.98.14:11434/api/generate
   ```

3. Set up Python virtual environment for backend:
   ```bash
   python -m venv venv
   source venv/bin/activate
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. Apply database migrations:
   ```bash
   cd backend
   alembic upgrade head
   cd ..
   ```

6. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. In a separate terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0 --port 3000
   ```

8. Access the application at http://172.30.98.177:1717

### Environment Setup

#### Conda Environment

You can set up a Conda environment using the provided `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate DoR
```

#### Development Dependencies

For backend development:
```bash
cd backend
pip install -r requirements-dev.txt
```

For frontend development:
```bash
cd frontend
npm install
```

#### Development Mode

You can use the development Docker Compose configuration:

```bash
docker-compose -f docker-compose.dev.yml up
```

## Project Structure

```
/
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database models and connections
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   └── tests/              # Test suite
├── frontend/               # SvelteKit frontend application
│   ├── src/
│   │   ├── lib/            # Reusable components/utilities
│   │   ├── routes/         # Page components
│   │   └── stores/         # State management
│   └── static/             # Static assets
├── uploads/                # Uploaded files
├── logs/                   # Application logs
├── docker-compose.yml      # Container orchestration
├── docker-compose.dev.yml  # Development configuration
├── environment.yml         # Conda environment
└── .env                    # Environment variables
```

## Development

### Backend Development

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

## Production Deployment

For production deployment, ensure you:

1. Set a secure `SECRET_KEY` in the `.env` file
2. Set appropriate CORS settings
3. Consider using a production-grade web server (nginx, etc.)
4. Set up proper logging
5. Configure database backups

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.