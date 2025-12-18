# Testing Guide - Genesis AI

## Overview

This guide covers all testing strategies for the Genesis AI project, including backend unit tests, integration tests, and frontend E2E tests.

## Table of Contents

1. [Backend Tests (Python/Pytest)](#backend-tests)
2. [Frontend E2E Tests (Playwright)](#frontend-e2e-tests)
3. [Docker Test Environment](#docker-test-environment)
4. [CI/CD Integration](#cicd-integration)

---

## Backend Tests

### Test Structure

```
tests/
├── conftest.py              # Local test fixtures
├── conftest_docker.py       # Docker test fixtures
├── test_api/
│   ├── test_auth.py        # Authentication endpoints
│   ├── test_chat.py        # Chat API
│   └── test_sites.py       # Site generation API
├── test_services/
│   └── test_transformer.py # BriefToSiteTransformer
└── test_integrations/
    └── test_redis.py       # Redis VFS integration
```

### Running Backend Tests

#### Local Environment

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_api/test_auth.py::test_register_user -v
```

#### Docker Environment

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up genesis-test

# Run auth tests only
docker-compose -f docker-compose.test.yml up genesis-test-auth

# Run integration tests only
docker-compose -f docker-compose.test.yml up genesis-test-integrations

# Clean up after tests
docker-compose -f docker-compose.test.yml down -v
```

### Test Database

- **Local**: PostgreSQL on `localhost:5433`
- **Docker**: PostgreSQL on `test-db:5432` (internal network)
- **Credentials**: `test_user:test_password` / `test_db`

### Test Configuration

Environment variables for testing:
```bash
TESTING_MODE=true
ENVIRONMENT=testing_docker
TEST_DATABASE_URL=postgresql+asyncpg://test_user:test_password@test-db:5432/test_db
REDIS_URL=redis://redis:6379/0
STRICT_HEALTH_CHECKS=false
VALIDATE_EXTERNAL_APIS=false
```

---

## Frontend E2E Tests

### Test Structure

```
genesis-frontend/e2e/
├── fixtures/
│   └── auth.ts              # Auth fixtures (JWT + mocks)
├── auth.spec.ts             # Authentication flow
├── chat.spec.ts             # Chat interface
├── site-generation.spec.ts  # Site generation flow
├── preview.spec.ts          # Preview page
├── responsive.spec.ts       # Responsive viewports
└── README.md                # E2E test documentation
```

### Authentication Strategy (GEN-12)

**Real JWT + Mocked Routes:**
- Generate real JWT from `genesis-api` (`/api/v1/auth/token`)
- Mock frontend auth routes (`/api/auth/me`, `/api/auth/validate`) to bypass DC360
- Isolate external dependencies while maintaining realistic auth flow

### Running E2E Tests

#### Local Development

```bash
cd genesis-frontend

# Install dependencies (if not done)
npm install

# Install Playwright browsers (if not done)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run tests in UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Run specific test file
npx playwright test e2e/auth.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Debug specific test
npx playwright test --debug e2e/auth.spec.ts
```

#### Docker Environment

```bash
# Run E2E tests in Docker
docker-compose -f docker-compose.test.yml up e2e-tests

# Run with logs and exit on completion
docker-compose -f docker-compose.test.yml up --abort-on-container-exit e2e-tests

# Clean up after tests
docker-compose -f docker-compose.test.yml down -v
```

### Test Coverage

1. **Authentication Flow** (`auth.spec.ts`)
   - SSO login to chat page
   - Authenticated user display
   - Redirect for unauthenticated users

2. **Chat Interface** (`chat.spec.ts`)
   - Message sending and receiving
   - Input validation
   - Loading states
   - Keyboard shortcuts (Enter key)

3. **Site Generation** (`site-generation.spec.ts`)
   - Brief generation trigger (message contains "site")
   - Site preview visibility
   - Navigation to preview page
   - Site renderer display

4. **Preview Page** (`preview.spec.ts`)
   - Preview toolbar functionality
   - Navigation back to chat
   - Error handling (invalid site ID, not found)
   - Viewport controls

5. **Responsive Viewports** (`responsive.spec.ts`)
   - Mobile viewport (375px)
   - Tablet viewport (768px)
   - Desktop viewport (1920px)
   - Viewport switching in preview
   - Functionality across viewport changes

### Environment Variables

```bash
# Frontend URL (default: http://localhost:3000)
PLAYWRIGHT_BASE_URL=http://localhost:3000

# Genesis API URL for JWT generation (default: http://localhost:8002)
GENESIS_API_URL=http://localhost:8002

# CI mode (enables retries, sequential execution)
CI=true
```

### Test Artifacts

- **Screenshots**: Captured on failure → `test-results/`
- **Videos**: Recorded on failure → `test-results/`
- **Traces**: Captured on first retry → `test-results/`
- **HTML Report**: `playwright-report/` (view with `npx playwright show-report`)

---

## Docker Test Environment

### Services

#### Backend Tests
- `genesis-test`: Main test service (all tests)
- `genesis-test-auth`: Authentication tests only
- `genesis-test-integrations`: Integration tests only

#### Frontend E2E Tests
- `frontend-test`: Next.js production build
- `e2e-tests`: Playwright test runner

#### Infrastructure
- `test-db`: PostgreSQL test database
- `redis`: Redis for VFS and caching

### Network

All services run on `genesis-ai-network` (subnet: `172.31.0.0/16`)

### Ports

- `test-db`: `5433:5432` (PostgreSQL)
- `redis`: `6382:6379` (Redis)
- `frontend-test`: `3000:3000` (Next.js)

### Running Full Test Suite

```bash
# Start all test services
docker-compose -f docker-compose.test.yml up

# Run backend tests only
docker-compose -f docker-compose.test.yml up genesis-test

# Run E2E tests only
docker-compose -f docker-compose.test.yml up e2e-tests

# Run specific backend test suite
docker-compose -f docker-compose.test.yml up genesis-test-auth

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

---

## CI/CD Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit genesis-test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E Tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit e2e-tests
      - name: Upload Playwright Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: genesis-frontend/playwright-report/
```

### Test Configuration for CI

Playwright is configured to:
- Retry failed tests (2 retries)
- Run tests sequentially (no parallel)
- Generate HTML and JSON reports
- Capture traces on first retry

---

## Troubleshooting

### Backend Tests

**Issue**: Database connection errors
```bash
# Check test-db is running
docker-compose -f docker-compose.test.yml ps test-db

# Check logs
docker-compose -f docker-compose.test.yml logs test-db

# Restart test-db
docker-compose -f docker-compose.test.yml restart test-db
```

**Issue**: Redis connection errors
```bash
# Check redis is running
docker-compose -f docker-compose.test.yml ps redis

# Test Redis connection
docker-compose -f docker-compose.test.yml exec redis redis-cli ping
```

### E2E Tests

**Issue**: Tests fail with "Not authenticated"
- Ensure `genesis-api` is running and accessible
- Check `GENESIS_API_URL` environment variable
- Verify test user can be created/authenticated

**Issue**: Tests timeout
- Increase timeout in test: `{ timeout: 60000 }`
- Check network connectivity between services in Docker
- Verify frontend and backend are fully started

**Issue**: Viewport tests fail
- Ensure viewport switching logic is correct
- Check CSS responsive breakpoints
- Verify viewport buttons have correct aria-labels

**Issue**: Browser not installed
```bash
# Install Playwright browsers
cd genesis-frontend
npx playwright install
```

---

## Best Practices

### Backend Tests
1. Use fixtures for database setup/teardown
2. Isolate tests (no shared state)
3. Mock external API calls (DC360, Tavily, etc.)
4. Use async/await consistently
5. Clean up resources in fixtures

### E2E Tests
1. Use `authenticatedPage` fixture for tests requiring auth
2. Wait for network idle after navigation: `waitForLoadState('networkidle')`
3. Use role-based selectors: `getByRole`, `getByLabel`, `getByPlaceholder`
4. Set appropriate timeouts for API-dependent operations
5. Each test should be independent

### Docker Tests
1. Always clean up volumes after tests: `docker-compose down -v`
2. Use health checks for service dependencies
3. Set `TESTING_MODE=true` for test-specific behavior
4. Disable strict health checks: `STRICT_HEALTH_CHECKS=false`
5. Use separate test database (never production)

---

## Test Metrics

### Coverage Goals
- Backend: >80% code coverage
- E2E: Critical user flows covered
- Integration: All external service integrations tested

### Performance
- Backend unit tests: <5s per test
- E2E tests: <60s per test (including API calls)
- Full test suite: <10 minutes

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js Testing](https://nextjs.org/docs/testing)
