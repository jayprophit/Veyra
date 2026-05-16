# Contributing to Veyra

Thank you for your interest in contributing to Veyra! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Node.js 22+
- pnpm 10+
- Docker (optional, for containerized development)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/jayprophit/Veyra.git
cd Veyra

# Install dependencies
pnpm install

# Start development
pnpm dev
```

## Development Workflow

### Branching Strategy

- `main` - stable integration branch
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

Examples:
- `feat(api-gateway): add user authentication endpoint`
- `fix(web): resolve memory leak in chart component`
- `docs(readme): update installation instructions`

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request with a clear description

## Coding Standards

### TypeScript/JavaScript

- Use TypeScript for type safety
- Follow ESLint configuration
- Use Prettier for code formatting
- Write meaningful variable and function names
- Add JSDoc comments for public APIs

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Follow Black formatting

### Testing

- Write unit tests for new features
- Add integration tests for API endpoints
- Ensure test coverage above 80%
- Use descriptive test names

## Project Structure

```
apps/
  web/          # React web application
  mobile/       # Mobile application
  desktop/      # Desktop application

services/
  api-gateway/      # API gateway and routing
  market-data/      # Market data service
  analytics/        # Analytics service
  auth/             # Authentication service
  alerts/           # Alerts service
  portfolio/        # Portfolio management
  ai-engine/        # AI/ML engine
  backtesting/      # Backtesting service
  execution/        # Trade execution

packages/
  ui/              # Shared UI components
  types/           # Shared TypeScript types
  sdk/             # Client SDK
  shared-utils/    # Shared utilities
  config/          # Shared configuration

infrastructure/
  docker/          # Docker configurations
  kubernetes/      # Kubernetes manifests
  terraform/       # Terraform configurations
  cloudflare/      # Cloudflare Workers

tools/
  scripts/         # Utility scripts
  devops/          # DevOps automation

tests/
  integration/     # Integration tests
  e2e/            # End-to-end tests
  performance/    # Performance tests
  security/       # Security tests
```

## Areas for Contribution

### High Priority

- API gateway implementation
- Market data service
- Authentication service
- Testing infrastructure
- Documentation

### Medium Priority

- Analytics service
- Portfolio management
- Backtesting engine
- Observability setup

### Low Priority

- Mobile application
- Desktop application
- Advanced AI features

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Node.js version, etc.)
- Screenshots if applicable

## Feature Requests

For feature requests:

- Describe the feature clearly
- Explain the use case
- Suggest a possible implementation
- Consider if it aligns with project goals

## Questions

For questions:

- Check existing documentation first
- Search existing issues
- Provide context when asking
- Be patient with responses

## License

By contributing to Veyra, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Veyra!
