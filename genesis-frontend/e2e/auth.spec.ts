import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Authentication Flow
 * GEN-12: SSO login to chat page with mocked auth routes
 */

test.describe('Authentication Flow', () => {
  test('should authenticate and redirect to chat page', async ({ authenticatedPage }) => {
    // Navigate to chat page
    await authenticatedPage.goto('/chat');
    
    // Verify we're on the chat page (not redirected to home)
    await expect(authenticatedPage).toHaveURL(/\/chat/);
    
    // Verify header shows user email
    await expect(authenticatedPage.getByText('e2e-test@example.com')).toBeVisible();
    
    // Verify Genesis AI header is present
    await expect(authenticatedPage.getByText('Genesis AI')).toBeVisible();
  });

  test('should show chat interface when authenticated', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/chat');
    
    // Verify chat input is visible
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    
    // Verify send button is visible
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    await expect(sendButton).toBeVisible();
    
    // Verify initial assistant message
    await expect(authenticatedPage.getByText(/Je suis Genesis/)).toBeVisible();
  });

  test('should redirect to home when not authenticated', async ({ page }) => {
    // Navigate to chat without auth
    await page.goto('/chat');
    
    // Should redirect to home page
    await expect(page).toHaveURL('/');
    
    // Verify login link is present
    await expect(page.getByText(/Se connecter via DC360/)).toBeVisible();
  });
});
