import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Preview Page Navigation
 * GEN-12: Preview page functionality and navigation
 */

test.describe('Preview Page', () => {
  test('should display preview page with toolbar', async ({ authenticatedPage }) => {
    // Navigate directly to a preview page (assuming site exists)
    // In real scenario, we'd generate a site first, but for this test we'll mock the API
    
    // Mock the site preview API to return test data
    await authenticatedPage.route('**/api/v1/sites/*/preview', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          theme: {
            colors: {
              primary: '#6366f1',
              secondary: '#8b5cf6',
              accent: '#ec4899',
              background: '#ffffff',
              text: '#1f2937'
            },
            fonts: {
              heading: 'Inter',
              body: 'Inter'
            }
          },
          metadata: {
            title: 'Test Site',
            description: 'E2E Test Site',
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
                  content: {
                    title: 'Test Hero',
                    subtitle: 'Test Subtitle'
                  }
                }
              ]
            }
          ]
        })
      });
    });

    await authenticatedPage.goto('/preview/site_a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890');
    
    // Verify preview toolbar is visible
    await expect(authenticatedPage.getByText('Genesis Preview')).toBeVisible();
    
    // Verify back button is visible
    const backButton = authenticatedPage.getByRole('button', { name: /Chat/i });
    await expect(backButton).toBeVisible();
    
    // Verify viewport buttons are visible
    await expect(authenticatedPage.getByLabel('Viewport mobile')).toBeVisible();
    await expect(authenticatedPage.getByLabel('Viewport tablette')).toBeVisible();
    await expect(authenticatedPage.getByLabel('Viewport desktop')).toBeVisible();
  });

  test('should navigate back to chat from preview', async ({ authenticatedPage }) => {
    // Mock the site preview API
    await authenticatedPage.route('**/api/v1/sites/*/preview', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          theme: { colors: {}, fonts: {} },
          metadata: { title: 'Test', description: 'Test', language: 'fr' },
          pages: [{ id: 'home', path: '/', title: 'Home', sections: [] }]
        })
      });
    });

    await authenticatedPage.goto('/preview/site_a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890');
    
    // Click back button
    const backButton = authenticatedPage.getByRole('button', { name: /Chat/i });
    await backButton.click();
    
    // Verify navigation to chat page
    await expect(authenticatedPage).toHaveURL('/chat');
  });

  test('should show error for invalid site ID', async ({ authenticatedPage }) => {
    // Navigate with invalid site ID format
    await authenticatedPage.goto('/preview/invalid-site-id');
    
    // Verify error message is displayed
    await expect(authenticatedPage.getByText('ID de site invalide')).toBeVisible();
  });

  test('should show error when site not found', async ({ authenticatedPage }) => {
    // Mock 404 response
    await authenticatedPage.route('**/api/v1/sites/*/preview', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Site not found' })
      });
    });

    await authenticatedPage.goto('/preview/site_00000000-0000-0000-0000-000000000000');
    
    // Verify error message
    await expect(authenticatedPage.getByText(/Impossible de charger le site|Site non trouvé/)).toBeVisible();
  });
});
