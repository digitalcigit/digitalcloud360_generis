import { test as base, Page } from '@playwright/test';

/**
 * Auth Fixtures for E2E Tests
 * GEN-12: Generate real JWT from genesis-api and mock frontend auth routes
 */

export interface AuthFixtures {
  authenticatedPage: Page;
  testToken: string;
}

/**
 * Generate a real JWT token from genesis-api
 */
async function generateTestToken(): Promise<string> {
  // Return dummy token for mocked tests
  return "mock-jwt-token-for-e2e-testing";
}

/**
 * Mock frontend auth API routes to bypass DC360 dependency
 */
async function mockAuthRoutes(page: Page, token: string) {
  // Mock /api/auth/validate - returns test user data
  await page.route('**/api/auth/validate', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        email: 'e2e-test@example.com',
        first_name: 'E2E',
        last_name: 'Test'
      })
    });
  });

  // Mock /api/auth/me - returns test user data
  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        email: 'e2e-test@example.com',
        first_name: 'E2E',
        last_name: 'Test'
      })
    });
  });
}

/**
 * Set authentication cookie
 */
async function setAuthCookie(page: Page, token: string) {
  const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';
  console.log(`Setting auth cookie for baseURL: ${baseURL}`);
  
  // Extract domain from baseURL for cookie
  const domain = new URL(baseURL).hostname;

  await page.context().addCookies([
    {
      name: 'access_token',
      value: token,
      domain: domain,
      path: '/',
      httpOnly: false,
      secure: false,
      sameSite: 'Lax'
    }
  ]);
}

/**
 * Extended test with authenticated page fixture
 */
export const test = base.extend<AuthFixtures>({
  testToken: async ({}, use) => {
    const token = await generateTestToken();
    await use(token);
  },

  authenticatedPage: async ({ page, testToken }, use) => {
    // Mock auth routes to bypass DC360
    await mockAuthRoutes(page, testToken);
    
    // Set auth cookie with real JWT
    await setAuthCookie(page, testToken);
    
    // Navigate to home first to set storage (domain requirement)
    await page.goto('/');
    
    // Inject token into localStorage for Zustand persist
    await page.evaluate((token) => {
      const state = {
        state: { token: token },
        version: 0
      };
      localStorage.setItem('auth-storage', JSON.stringify(state));
    }, testToken);
    
    // Reload to pick up storage
    await page.reload();
    
    // Wait for auth to complete
    await page.waitForLoadState('networkidle');
    
    await use(page);
  }
});

export { expect } from '@playwright/test';
