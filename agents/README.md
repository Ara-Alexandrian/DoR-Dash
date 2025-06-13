# DoR-Dash Specialized Sub-Agents

This directory contains specialized sub-agents for managing different aspects of the DoR-Dash project. Each agent has domain-specific expertise while inheriting shared project knowledge from the main `CLAUDE.md`.

## Agent Architecture

```
Main CLAUDE.md (shared project context)
├── WEBSITE_TESTING_AGENT.md    # E2E testing, API validation, UI testing
├── DATABASE_AGENT.md           # Schema management, migrations, data integrity
├── UI_AGENT.md                 # Frontend development, component design, UX
├── LLM_AGENT.md               # Ollama integration, AI features, text processing
└── REPOSITORY_AGENT.md        # Git operations, refactoring, documentation
```

## Agent Deployment

Each agent can be deployed with:
```bash
# Deploy with agent-specific instructions
Task(description="Agent deployment", prompt="Deploy [AGENT_NAME] with instructions from agents/[AGENT_FILE].md")
```

## Shared Resources

All agents inherit:
- Project structure and architecture (from main CLAUDE.md)
- Database credentials and connection details
- MCP server configurations (PostgreSQL, Redis, SSH, etc.)
- Deployment and container access information
- Security practices and development guidelines

## Agent Specializations

### Website Testing Agent
- **Focus**: End-to-end testing, API validation, regression testing
- **Tools**: cURL, pytest, Selenium-style testing via SSH
- **Scope**: Frontend/backend integration, user workflows

### Database Agent  
- **Focus**: Schema management, migrations, data integrity
- **Tools**: PostgreSQL MCP, Alembic, SQL optimization
- **Scope**: Database design, performance, backup/restore

### UI Agent
- **Focus**: Frontend development, component design, user experience
- **Tools**: SvelteKit, CSS, component libraries, responsive design
- **Scope**: User interface, accessibility, design systems

### LLM Agent
- **Focus**: Ollama integration, AI features, text processing
- **Tools**: Ollama API, text refinement, prompt engineering
- **Scope**: AI-assisted features, natural language processing

### Repository Agent
- **Focus**: Git operations, code refactoring, documentation management
- **Tools**: Git, code analysis, markdown validation, project structure
- **Scope**: Version control, code quality, documentation standards