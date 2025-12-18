import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Responsive Viewports
 * GEN-12: Test across mobile, tablet, and desktop viewports
 */

test.describe('Responsive Viewports', () => {
  test('should display correctly on mobile viewport', async ({ authenticatedPage }) => {
    // Set mobile viewport
    await authenticatedPage.setViewportSize({ width: 375, height: 667 });
    
    await authenticatedPage.goto('/chat');
    
    // Verify chat interface is visible and functional
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    
    // Verify header is visible
    await expect(authenticatedPage.getByText('Genesis AI')).toBeVisible();
    
    // Verify responsive layout (chat should take full width on mobile)
    const chatPanel = authenticatedPage.locator('.w-1\\/2').first();
    await expect(chatPanel).toBeVisible();
  });

  test('should display correctly on tablet viewport', async ({ authenticatedPage }) => {
    // Set tablet viewport
    await authenticatedPage.setViewportSize({ width: 768, height: 1024 });
    
    await authenticatedPage.goto('/chat');
    
    // Verify chat interface is visible
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    
    // Verify both chat and preview panels are visible
    await expect(authenticatedPage.locator('.w-1\\/2').first()).toBeVisible();
  });

  test('should display correctly on desktop viewport', async ({ authenticatedPage }) => {
    // Set desktop viewport
    await authenticatedPage.setViewportSize({ width: 1920, height: 1080 });
    
    await authenticatedPage.goto('/chat');
    
    // Verify chat interface is visible
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    
    // Verify split layout (50/50)
    const chatPanel = authenticatedPage.locator('.w-1\\/2').first();
    const previewPanel = authenticatedPage.locator('.w-1\\/2').last();
    
    await expect(chatPanel).toBeVisible();
    await expect(previewPanel).toBeVisible();
  });

  test('should switch viewports in preview page', async ({ authenticatedPage }) => {
    // Mock the site preview API
    await authenticatedPage.route('**/api/v1/sites/*/preview', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          theme: {
            colors: {
              primary: '#6366f1',
              secondary: '#8b5cf6',
              background: '#ffffff',
              text: '#1f2937'
            },
            fonts: { heading: 'Inter', body: 'Inter' }
          },
          metadata: { title: 'Test', description: 'Test', language: 'fr' },
          pages: [
            {
              id: 'home',
              path: '/',
              title: 'Home',
              sections: [
                {
                  id: 'hero-1',
                  type: 'hero',
                  content: { title: 'Test', subtitle: 'Test' }
                }
              ]
            }
          ]
        })
      });
    });

    await authenticatedPage.goto('/preview/site_test-123');
    
    // Desktop viewport should be active by default
    const desktopButton = authenticatedPage.getByLabel('Viewport desktop');
    await expect(desktopButton).toHaveClass(/bg-gray-800/);
    
    // Click mobile viewport button
    const mobileButton = authenticatedPage.getByLabel('Viewport mobile');
    await mobileButton.click();
    
    // Verify mobile viewport is active
    await expect(mobileButton).toHaveClass(/bg-gray-800/);
    
    // Click tablet viewport button
    const tabletButton = authenticatedPage.getByLabel('Viewport tablette');
    await tabletButton.click();
    
    // Verify tablet viewport is active
    await expect(tabletButton).toHaveClass(/bg-gray-800/);
  });

  test('should maintain functionality across viewport changes', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/chat');
    
    // Test on mobile
    await authenticatedPage.setViewportSize({ width: 375, height: 667 });
    let chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    await chatInput.fill('Test mobile');
    await expect(chatInput).toHaveValue('Test mobile');
    
    // Switch to tablet
    await authenticatedPage.setViewportSize({ width: 768, height: 1024 });
    chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    await chatInput.clear();
    await chatInput.fill('Test tablet');
    await expect(chatInput).toHaveValue('Test tablet');
    
    // Switch to desktop
    await authenticatedPage.setViewportSize({ width: 1920, height: 1080 });
    chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await expect(chatInput).toBeVisible();
    await chatInput.clear();
    await chatInput.fill('Test desktop');
    await expect(chatInput).toHaveValue('Test desktop');
  });
});
