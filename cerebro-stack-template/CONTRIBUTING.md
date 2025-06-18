# Contributing to [Project Name]

First off, thank you for considering contributing to this project! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [project email].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible. Fill out the required template, the information it asks for helps us resolve issues faster.

**Great Bug Reports** tend to have:
- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:
- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues](https://github.com/yourusername/yourproject/labels/beginner) - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues](https://github.com/yourusername/yourproject/labels/help%20wanted) - issues which should be a bit more involved than `beginner` issues.

### Pull Requests

The process described here has several goals:
- Maintain project quality
- Fix problems that are important to users
- Engage the community in working toward the best possible project
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](.github/PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

## Development Process

### Setting Up Your Development Environment

1. Fork the repo and create your branch from `main`:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   git checkout -b feature/your-feature-name
   ```

2. Install dependencies:
   ```bash
   ./scripts/setup.sh
   ```

3. Make your changes:
   - Write code following our style guides
   - Add tests for your changes
   - Update documentation as needed

4. Run tests to ensure everything works:
   ```bash
   ./scripts/run-tests.sh
   ```

5. Commit your changes using conventional commits:
   ```bash
   git commit -m "feat: add new feature"
   ```

6. Push to your fork and submit a pull request

### Development Workflow

1. **Create an Issue**: Before starting work, create or find an issue describing what you want to do
2. **Discuss**: For significant changes, discuss your approach in the issue before starting
3. **Branch**: Create a feature branch from `main`
4. **Code**: Make your changes following our guidelines
5. **Test**: Ensure all tests pass and add new tests as needed
6. **Document**: Update documentation to reflect your changes
7. **Commit**: Use meaningful commit messages
8. **Push**: Push your branch to your fork
9. **PR**: Submit a pull request referencing the issue

## Styleguides

### Git Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

* Use the present tense ("add feature" not "added feature")
* Use the imperative mood ("move cursor to..." not "moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Examples:
```
feat: add user authentication
fix: resolve race condition in data sync
docs: update API documentation
style: format code according to style guide
refactor: restructure user service
test: add missing tests for user service
chore: update dependencies
```

### TypeScript/JavaScript Styleguide

* Use TypeScript for all new code
* Follow the existing code style
* Use meaningful variable and function names
* Add JSDoc comments for public APIs
* Prefer functional programming patterns
* Avoid mutations when possible

```typescript
// Good
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Bad
export function calc(i: any[]) {
  let t = 0;
  for (let x = 0; x < i.length; x++) {
    t += i[x].price;
  }
  return t;
}
```

### Python Styleguide

* Follow PEP 8
* Use type hints for all functions
* Use docstrings for all public functions
* Prefer descriptive names over comments
* Use Black for formatting
* Use Ruff for linting

```python
# Good
async def get_user_by_email(email: str) -> User | None:
    """Retrieve a user by their email address.
    
    Args:
        email: The email address to search for
        
    Returns:
        The user if found, None otherwise
    """
    return await User.find_one({"email": email})

# Bad
async def getUser(e):
    # get user by email
    return await User.find_one({"email": e})
```

### Documentation Styleguide

* Use Markdown for all documentation
* Reference code with proper syntax highlighting
* Include examples for all features
* Keep documentation up-to-date with code changes
* Use clear, concise language
* Include diagrams where helpful

## Testing Guidelines

### Writing Tests

* Write tests for all new features
* Ensure tests are deterministic
* Use descriptive test names
* Follow the AAA pattern (Arrange, Act, Assert)
* Mock external dependencies
* Aim for high test coverage

```typescript
// Example test
describe('UserService', () => {
  it('should create a new user with valid data', async () => {
    // Arrange
    const userData = { email: 'test@example.com', name: 'Test User' };
    
    // Act
    const user = await userService.create(userData);
    
    // Assert
    expect(user.email).toBe(userData.email);
    expect(user.name).toBe(userData.name);
    expect(user.id).toBeDefined();
  });
});
```

### Running Tests

```bash
# Run all tests
./scripts/run-tests.sh

# Run frontend tests
npm run test

# Run backend tests
pytest

# Run specific test file
pytest tests/test_users.py
npm run test -- UserService.test.ts
```

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. Consult [GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information on using pull requests.

### Review Criteria

* **Correctness**: Does the code do what it's supposed to do?
* **Testing**: Are there adequate tests?
* **Documentation**: Is the code well-documented?
* **Style**: Does the code follow our style guides?
* **Performance**: Are there any performance concerns?
* **Security**: Are there any security issues?

## Community

* Join our [Discord server](https://discord.gg/yourproject)
* Follow us on [Twitter](https://twitter.com/yourproject)
* Read our [blog](https://blog.yourproject.com)
* Subscribe to our [newsletter](https://yourproject.com/newsletter)

## Recognition

Contributors who have made significant contributions may be invited to become maintainers. We also recognize contributors in our:
* README.md contributors section
* Release notes
* Project website

## Questions?

Don't hesitate to ask questions! You can:
* Open an issue with the question label
* Ask in our Discord server
* Email us at [project email]

Thank you for contributing! 🎉