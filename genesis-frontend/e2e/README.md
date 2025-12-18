# E2E Tests - Genesis Frontend

## Overview

This directory contains end-to-end (E2E) tests for the Genesis AI frontend using Playwright.

## Test Strategy (GEN-12)

### Authentication
- **Real JWT**: Tests use real JWT tokens generated from `genesis-api` (`/api/v1/auth/token`)
- **Mocked Routes**: Frontend auth routes (`/api/auth/me`, `/api/auth/validate`) are mocked to bypass DC360 dependency
- **Isolation**: Tests are isolated from external dependencies while maintaining realistic authentication flow

### Test Coverage

1. **Authentication Flow** (`auth.spec.ts`)
   - SSO login to chat page
   - Authenticated user display
   - Redirect behavior for unauthenticated users

2. **Chat Interface** (`chat.spec.ts`)
   - Message sending and receiving
   - Input validation
   - Loading states
   - Keyboard shortcuts (Enter key)

3. **Site Generation** (`site-generation.spec.ts`)
   - Brief generation trigger
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

## Running Tests

### Local Development

```bash
# Install dependencies
npm install

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
```

### Docker Environment

```bash
# Run E2E tests in Docker
docker-compose -f docker-compose.test.yml up e2e-tests

# Run with logs
docker-compose -f docker-compose.test.yml up --abort-on-container-exit e2e-tests

# Clean up after tests
docker-compose -f docker-compose.test.yml down -v
```

## Environment Variables

- `PLAYWRIGHT_BASE_URL`: Base URL for the frontend (default: `http://localhost:3000`)
- `GENESIS_API_URL`: Genesis API URL for JWT generation (default: `http://localhost:8002`)
- `CI`: Set to `true` in CI environment for optimized settings

## Test Fixtures

### `fixtures/auth.ts`

Provides authenticated page fixture with:
- Real JWT token generation from `genesis-api`
- Mocked `/api/auth/me` and `/api/auth/validate` routes
- Pre-authenticated page ready for testing

Usage:
```typescript
import { test, expect } from './fixtures/auth';

test('my test', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/chat');
  // Page is already authenticated
});
```

## Debugging

### View Test Report

```bash
npx playwright show-report
```

### Debug Specific Test

```bash
npx playwright test --debug e2e/auth.spec.ts
```

### Screenshots and Videos

- Screenshots: Captured on failure
- Videos: Recorded on failure
- Traces: Captured on first retry

All artifacts are saved to `test-results/` directory.

## CI/CD Integration

Tests are configured to run in CI with:
- Retry on failure (2 retries)
- Sequential execution (no parallel)
- HTML and JSON reporters
- Trace collection on retry

## Troubleshooting

### Tests Fail with "Not authenticated"
- Ensure `genesis-api` is running and accessible
- Check `GENESIS_API_URL` environment variable
- Verify test user can be created/authenticated

### Tests Timeout
- Increase timeout in test: `{ timeout: 60000 }`
- Check network connectivity between services in Docker
- Verify frontend and backend are fully started

### Viewport Tests Fail
- Ensure viewport switching logic is correct
- Check CSS responsive breakpoints
- Verify viewport buttons have correct aria-labels

### Cookie Setting Errors in Docker
If you see `browserContext.addCookies: Cookie must have domain or url`:
- The `setAuthCookie` function in `fixtures/auth.ts` extracts domain from `PLAYWRIGHT_BASE_URL`
- Ensure `PLAYWRIGHT_BASE_URL` is correctly set in Docker environment

### Database 500 Errors
If auth endpoints return 500 errors:
- Reset Docker volumes: `docker-compose -f docker-compose.test.yml down -v`
- Verify DB is initialized: check `genesis-test-server` logs for table creation
- Ensure `ENVIRONMENT=testing_docker` is set for the test server

### API Mocking Strategy
All E2E tests mock backend API endpoints to ensure stability:
- `/api/chat` - Mocked for chat flow simulation
- `/api/v1/sites/generate` - Mocked for site generation
- `/api/v1/sites/*/preview` - Mocked for preview data
- `/api/auth/me`, `/api/auth/validate` - Mocked for auth bypass

## Best Practices

1. **Use Fixtures**: Always use `authenticatedPage` fixture for tests requiring auth
2. **Wait for Network**: Use `waitForLoadState('networkidle')` after navigation
3. **Specific Selectors**: Use role-based selectors (`getByRole`, `getByLabel`) over CSS
4. **Timeouts**: Set appropriate timeouts for API-dependent operations
5. **Isolation**: Each test should be independent and not rely on previous test state
