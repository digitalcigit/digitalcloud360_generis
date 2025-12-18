import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Site Generation Flow
 * GEN-12: Brief generation → Site preview visibility
 */

test.describe('Site Generation Flow', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // Mock Chat API for brief generation
    await authenticatedPage.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: "D'accord, je vais générer un site pour votre restaurant.",
          briefGenerated: true,
          briefId: "brief_123",
          siteData: null
        })
      });
    });

    // Mock Site Generation API
    await authenticatedPage.route('**/api/v1/sites/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          site_id: "site_123",
          brief_id: "brief_123",
          user_id: 1,
          created_at: new Date().toISOString(),
          site_definition: {
            theme: {
              colors: {
                primary: '#6366f1',
                secondary: '#8b5cf6',
                background: '#ffffff',
                text: '#1f2937'
              },
              fonts: { heading: 'Inter', body: 'Inter' }
            },
            metadata: {
              title: 'Mon Restaurant Africain',
              description: 'Le meilleur de la cuisine africaine',
              language: 'fr'
            },
            pages: [
              {
                id: 'home',
                path: '/',
                title: 'Accueil',
                sections: [
                  {
                    id: 'hero-1',
                    type: 'hero',
                    content: { title: 'Bienvenue', subtitle: 'Restaurant Africain' }
                  }
                ]
              }
            ]
          }
        })
      });
    });

    // Mock Site Preview API (for when navigating to preview)
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
            metadata: {
              title: 'Mon Restaurant Africain',
              description: 'Le meilleur de la cuisine africaine',
              language: 'fr'
            },
            pages: [
              {
                id: 'home',
                path: '/',
                title: 'Accueil',
                sections: []
              }
            ]
          })
        });
      });

    await authenticatedPage.goto('/chat');
    await authenticatedPage.waitForLoadState('networkidle');
  });

  test('should generate brief and show site preview', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    // Send a message that triggers brief generation (contains "site")
    await chatInput.fill('Je veux un site web pour mon restaurant africain');
    await sendButton.click();
    
    // Wait for assistant response
    await authenticatedPage.waitForSelector('.bg-gray-700', { timeout: 30000 });
    
    // Wait for brief generation and site preview (may take time)
    // Look for the "Votre site est prêt" message
    await expect(
      authenticatedPage.getByText('Votre site est prêt')
    ).toBeVisible({ timeout: 60000 });
    
    // Verify "Voir mon site" button is visible
    const previewButton = authenticatedPage.getByRole('button', { name: 'Voir mon site' });
    await expect(previewButton).toBeVisible();
    await expect(previewButton).toBeEnabled();
  });

  test('should navigate to preview page when clicking "Voir mon site"', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    // Trigger brief generation
    await chatInput.fill('Créer un site pour mon business');
    await sendButton.click();
    
    // Wait for site preview
    await expect(
      authenticatedPage.getByText('Votre site est prêt')
    ).toBeVisible({ timeout: 60000 });
    
    // Click "Voir mon site" button
    const previewButton = authenticatedPage.getByRole('button', { name: 'Voir mon site' });
    await previewButton.click();
    
    // Verify navigation to preview page
    await expect(authenticatedPage).toHaveURL(/\/preview\/site_[a-f0-9-]+/);
    
    // Verify preview toolbar is visible
    await expect(authenticatedPage.getByText('Genesis Preview')).toBeVisible();
  });

  test('should show site preview in chat panel', async ({ authenticatedPage }) => {
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    const sendButton = authenticatedPage.getByRole('button', { name: 'Envoyer' });
    
    // Trigger brief generation
    await chatInput.fill('site web restaurant');
    await sendButton.click();
    
    // Wait for site preview
    await expect(
      authenticatedPage.getByText('Votre site est prêt')
    ).toBeVisible({ timeout: 60000 });
    
    // Verify SiteRenderer is displayed (white background for site content)
    const siteRenderer = authenticatedPage.locator('.bg-white.text-black');
    await expect(siteRenderer).toBeVisible();
  });
});
