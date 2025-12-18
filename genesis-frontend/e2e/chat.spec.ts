import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Chat Interface
 * GEN-12: Message sending and response handling
 */

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // Mock chat API response
    await authenticatedPage.route('**/api/chat', async (route) => {
      // Simulate network delay for loading state test
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: "Je peux vous aider à créer un site pour votre restaurant. Quel est son nom ?",
          briefGenerated: false,
          briefId: null,
          siteData: null
        })
      });
    });

    await authenticatedPage.goto('/chat');
    await authenticatedPage.waitForLoadState('networkidle');
  });

  test('should send a message and receive a response', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    // Type a message
    await chatInput.fill('Je veux créer un site pour mon restaurant');
    
    // Send the message
    await sendButton.click();
    
    // Verify user message appears
    await expect(authenticatedPage.getByText('Je veux créer un site pour mon restaurant')).toBeVisible();
    
    // Wait for loading indicator
    await expect(authenticatedPage.locator('.animate-bounce').first()).toBeVisible();
    
    // Wait for assistant response (timeout 30s for API call)
    await expect(authenticatedPage.locator('.bg-gray-700').last()).toBeVisible({ timeout: 30000 });
    
    // Verify input is cleared
    await expect(chatInput).toHaveValue('');
  });

  test('should disable send button when input is empty', async ({ authenticatedPage }) => {
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    // Button should be disabled initially (empty input)
    await expect(sendButton).toBeDisabled();
    
    // Type something
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await chatInput.fill('Test message');
    
    // Button should be enabled
    await expect(sendButton).toBeEnabled();
    
    // Clear input
    await chatInput.clear();
    
    // Button should be disabled again
    await expect(sendButton).toBeDisabled();
  });

  test('should handle Enter key to send message', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    
    // Type a message and press Enter
    await chatInput.fill('Test message via Enter key');
    await chatInput.press('Enter');
    
    // Verify message was sent
    await expect(authenticatedPage.getByText('Test message via Enter key')).toBeVisible();
  });

  test('should show loading state while waiting for response', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    await chatInput.fill('Test loading state');
    await sendButton.click();
    
    // Verify loading animation appears
    await expect(authenticatedPage.locator('.animate-bounce').first()).toBeVisible();
    
    // Verify send button is disabled during loading
    await expect(sendButton).toBeDisabled();
  });
});
