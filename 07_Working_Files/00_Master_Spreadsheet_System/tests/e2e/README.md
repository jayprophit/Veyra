# 🎭 E2E Tests - End-to-End Testing Suite

**Framework:** Playwright  
**Coverage:** Full user flows from UI to database  
**Browsers:** Chrome, Firefox, Safari, Edge  
**Devices:** Desktop, Mobile, Tablet

## Quick Start

```bash
# Install dependencies
npm install

# Install browsers
npx playwright install

# Run all tests
npx playwright test

# Run specific test
npx playwright test login.spec.ts

# Run with UI
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Generate report
npx playwright show-report
```

## Test Structure

```
e2e/
├── fixtures/           # Test data and helpers
├── pages/             # Page Object Models
├── specs/             # Test specifications
├── utils/             # Test utilities
└── config/            # Playwright config
```

## Environment Setup

Create `.env` file:
```
BASE_URL=http://localhost:8000
API_URL=http://localhost:8000/api
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123
```

## CI/CD Integration

Tests run automatically on:
- Every pull request
- Before deployment to staging
- Nightly regression suite
