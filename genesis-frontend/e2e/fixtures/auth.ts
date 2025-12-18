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
  const apiUrl = process.env.GENESIS_API_URL || 'http://localhost:8002';
  
  // Register test user (idempotent - will fail if exists, that's OK)
  try {
    console.log(`Registering test user at ${apiUrl}/api/v1/auth/register`);
    const res = await fetch(`${apiUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'e2e-test@example.com',
        name: 'E2E Test User',
        password: 'TestPassword123!'
      })
    });
    if (!res.ok) {
        console.log(`Registration response: ${res.status} ${res.statusText}`);
    }
  } catch (e) {
    console.log('Registration failed (might already exist):', e);
  }

  // Login to get JWT token
  const formData = new URLSearchParams();
  formData.append('username', 'e2e-test@example.com');
  formData.append('password', 'TestPassword123!');

  console.log(`Fetching token from ${apiUrl}/api/v1/auth/token`);
  const response = await fetch(`${apiUrl}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString()
  });

  if (!response.ok) {
    const text = await response.text();
    console.error(`Token response error: ${response.status} - ${text}`);
    throw new Error(`Failed to get test token: ${response.status} - ${text}`);
  }

  const data = await response.json();
  return data.access_token;
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
    
    // Navigate to home - AuthContext will validate token via mocked routes
    await page.goto('/');
    
    // Wait for auth to complete
    await page.waitForLoadState('networkidle');
    
    await use(page);
  }
});

export { expect } from '@playwright/test';
