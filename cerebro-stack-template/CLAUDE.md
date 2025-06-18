# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI assistants when working with code in this repository.

## Project Overview

**Project Name**: [Your Project Name]
**Type**: Full-stack web application
**Stack**: SvelteKit (Frontend) + FastAPI (Backend) + PostgreSQL + Redis
**Architecture**: Microservices with REST API and WebSocket support

## Key Principles

1. **Security First**: Always consider security implications in every change
2. **Performance Matters**: Optimize for speed and efficiency
3. **Documentation**: Keep documentation up-to-date with code changes
4. **Testing**: Write tests for new features and bug fixes
5. **Code Quality**: Follow established patterns and style guides

## Repository Structure

```
.
├── frontend/          # SvelteKit application
│   ├── src/
│   │   ├── lib/      # Shared components and utilities
│   │   ├── routes/   # Page components and API routes
│   │   └── app.html  # HTML template
│   └── static/       # Static assets
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core functionality
│   │   ├── models/   # Data models
│   │   └── services/ # Business logic
│   └── tests/        # Backend tests
├── docs/             # Documentation
├── qa/               # Quality assurance
├── scripts/          # Utility scripts
└── subroutines/      # Development procedures
```

## Development Guidelines

### Frontend (SvelteKit)

- Use TypeScript for type safety
- Follow Svelte conventions for reactivity
- Implement proper error boundaries
- Use the `$lib` alias for imports
- Leverage SvelteKit's built-in features (SSR, routing, etc.)

### Backend (FastAPI)

- Use async/await for all database operations
- Implement proper request validation with Pydantic
- Follow RESTful API design principles
- Use dependency injection for services
- Implement comprehensive error handling

### Database

- Use migrations for all schema changes
- Never store sensitive data unencrypted
- Implement proper indexing for performance
- Use transactions for data consistency
- Follow naming conventions for tables and columns

## Common Tasks

### Adding a New Feature

1. Create a feature branch
2. Update the database schema if needed
3. Implement backend API endpoints
4. Create frontend components and routes
5. Write tests for both frontend and backend
6. Update documentation
7. Submit a pull request

### Fixing a Bug

1. Reproduce the issue locally
2. Write a failing test that demonstrates the bug
3. Fix the issue
4. Verify the test passes
5. Check for similar issues elsewhere
6. Update relevant documentation

### Performance Optimization

1. Profile the application to identify bottlenecks
2. Implement caching where appropriate
3. Optimize database queries
4. Minimize bundle sizes
5. Document performance improvements

## Code Style and Conventions

### TypeScript/JavaScript

```typescript
// Use meaningful variable names
const userAuthenticationToken = generateToken();

// Prefer const over let
const API_ENDPOINT = '/api/v1';

// Use async/await over promises
async function fetchUserData(userId: string) {
  const response = await api.get(`/users/${userId}`);
  return response.data;
}
```

### Python

```python
# Use type hints
def calculate_total(items: list[Item]) -> Decimal:
    return sum(item.price for item in items)

# Use descriptive function names
async def get_user_by_email(email: str) -> User | None:
    return await User.find_one({"email": email})

# Handle errors explicitly
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

## Security Considerations

1. **Authentication**: JWT tokens with proper expiration
2. **Authorization**: Role-based access control (RBAC)
3. **Input Validation**: Sanitize all user inputs
4. **SQL Injection**: Use parameterized queries
5. **XSS Prevention**: Escape HTML content
6. **CSRF Protection**: Implement CSRF tokens
7. **Rate Limiting**: Prevent abuse with rate limits
8. **Secrets Management**: Use environment variables

## Testing Strategy

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test API endpoints
3. **E2E Tests**: Test complete user flows
4. **Performance Tests**: Load testing for scalability
5. **Security Tests**: Vulnerability scanning

## Deployment Notes

- Use Docker for consistent environments
- Implement health checks for all services
- Set up proper logging and monitoring
- Use CI/CD for automated deployments
- Follow the deployment checklist in `subroutines/deployment-checklist.md`

## External Dependencies

List key dependencies and their purposes:
- **SvelteKit**: Frontend framework
- **FastAPI**: Backend framework
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **Docker**: Containerization

## Common Issues and Solutions

### Issue: Slow API Response Times
**Solution**: Check database queries, add caching, optimize algorithms

### Issue: Frontend Build Failures
**Solution**: Clear node_modules, check for version conflicts

### Issue: Database Connection Errors
**Solution**: Verify connection string, check network connectivity

## Contact and Resources

- **Documentation**: [docs/](docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/yourproject/issues)
- **Wiki**: [Project Wiki](https://github.com/yourusername/yourproject/wiki)

## AI Assistant Tips

When working with this codebase:
1. Always check existing patterns before implementing new features
2. Prioritize security and performance in suggestions
3. Ensure backward compatibility for API changes
4. Write clear commit messages following conventional commits
5. Update tests and documentation alongside code changes

Remember: Good code is not just working code, but code that is secure, performant, maintainable, and well-documented.