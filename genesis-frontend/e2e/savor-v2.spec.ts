import { test, expect } from './fixtures/auth';

/**
 * E2E Tests: Savor V2 Theme Rendering
 * Validates the rendering of new advanced blocks (Hero Split, Menu, Footer Restaurant, About Enhanced)
 */

test.describe('Savor V2 Theme Rendering', () => {
  
  const mockSavorV2Site = {
    site_id: "site_savor_v2",
    brief_id: "brief_savor_v2",
    user_id: 1,
    created_at: new Date().toISOString(),
    site_definition: {
      metadata: {
        title: "Le Délice Impérial",
        description: "Experience gastronomique",
      },
      theme: {
        colors: {
          primary: '#D97706',
          secondary: '#1F2937', 
          accent: '#F59E0B',
          background: '#ffffff',
          text: '#1a1a1a'
        },
        fonts: { 
          heading: 'Playfair Display', 
          body: 'Lato',
          accent: 'Great Vibes'
        }
      },
      pages: [
        {
          id: 'home',
          slug: '/',
          title: 'Accueil',
          sections: [
            {
              id: 'hero-v2',
              type: 'hero',
              content: {
                title: 'L\'Art de la Gastronomie',
                subtitle: 'Une expérience inoubliable',
                description: 'Découvrez des saveurs authentiques dans un cadre d\'exception.',
                image: 'https://placehold.co/1920x1080',
                variant: 'split',
                cta: { text: 'Réserver une table', link: '#contact', variant: 'primary' }
              }
            },
            {
              id: 'about-v2',
              type: 'about',
              content: {
                title: 'Notre Passion',
                subtitle: 'Depuis 1985',
                description: 'Une histoire de famille et de goût.',
                mission: 'Servir le meilleur',
                image: 'https://placehold.co/800x600',
                variant: 'enhanced',
                stats: [{ value: '30+', label: 'Années' }, { value: '5000+', label: 'Clients' }]
              }
            },
            {
              id: 'menu-v2',
              type: 'menu',
              content: {
                title: 'Notre Carte',
                subtitle: 'Sélection du Chef',
                currency: '€',
                categories: [
                  {
                    id: 'starters',
                    title: 'Entrées',
                    items: [
                      { title: 'Carpaccio de Saint-Jacques', description: 'Huile de truffe', price: '22', dietary: ['Gluten Free'] },
                      { title: 'Foie Gras Maison', price: '28' }
                    ]
                  },
                  {
                    id: 'mains',
                    title: 'Plats',
                    items: [
                      { title: 'Filet de Bœuf Rossini', price: '45', isHighlight: true },
                      { title: 'Risotto aux Cèpes', price: '32', dietary: ['Vegetarian'] }
                    ]
                  }
                ]
              }
            },
            {
              id: 'footer-v2',
              type: 'footer',
              content: {
                copyright: '© 2026 Le Délice Impérial',
                variant: 'restaurant',
                companyName: 'Le Délice Impérial',
                description: 'Restaurant gastronomique au cœur de Paris.',
                openingHours: [
                  { days: 'Lundi - Vendredi', hours: '12h - 14h30' },
                  { days: 'Samedi - Dimanche', hours: '19h - 23h' }
                ],
                contactInfo: {
                  address: '123 Avenue des Champs, Paris',
                  email: 'contact@delice.com',
                  phone: '+33 1 23 45 67 89'
                }
              }
            }
          ]
        }
      ]
    }
  };

  test.beforeEach(async ({ authenticatedPage }) => {
    // Mock the Generate API to return our Savor V2 structure
    await authenticatedPage.route('**/api/v1/sites/generate', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockSavorV2Site)
        });
    });

    // Mock Preview API as well just in case
    await authenticatedPage.route('**/api/v1/sites/*/preview', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockSavorV2Site.site_definition)
        });
    });
  });

  test('should render Savor V2 components correctly', async ({ authenticatedPage }) => {
    // Navigate to preview (simulate flow or direct access)
    // Here we can simulate the chat generation flow which calls /generate
    await authenticatedPage.goto('/chat');
    
    // Mock chat response to trigger generation logic in frontend
    await authenticatedPage.route('**/api/chat', async (route) => {
        await route.fulfill({
            status: 200,
            body: JSON.stringify({
                response: "Génération du site Savor V2...",
                briefGenerated: true,
                briefId: "brief_savor_v2"
            })
        });
    });

    // Trigger generation via Chat UI
    const chatInput = authenticatedPage.getByPlaceholder('Décrivez votre business...');
    await chatInput.fill('Restaurant gastronomique Savor V2');
    await authenticatedPage.getByRole('button', { name: 'Envoyer' }).click();

    // Wait for "Votre site est prêt" (which comes after /generate success)
    await expect(authenticatedPage.getByText('Votre site est prêt')).toBeVisible({ timeout: 15000 });

    // Click "Voir mon site"
    await authenticatedPage.getByRole('button', { name: 'Voir mon site' }).click();

    // --- VALIDATION ---

    // 1. Validate Fonts (Check CSS variables on body)
    // Note: Hard to check computed styles easily in E2E without evaluate, but we can check if fonts are loaded or classes applied
    // We'll trust visual check for fonts, but check content.

    // 2. Validate Hero Split
    const heroSection = authenticatedPage.locator('#hero-v2');
    await expect(heroSection).toBeVisible();
    // Split variant usually has a grid with 2 columns.
    await expect(heroSection.locator('h1')).toHaveText('L\'Art de la Gastronomie');
    await expect(heroSection.locator('text=Une expérience inoubliable')).toBeVisible();
    
    // 3. Validate About Enhanced
    const aboutSection = authenticatedPage.locator('#about-v2');
    await expect(aboutSection).toBeVisible();
    // Check for "Notre Passion"
    await expect(aboutSection.locator('h2')).toHaveText('Notre Passion');
    // Check for stats
    await expect(aboutSection.locator('text=30+')).toBeVisible();

    // 4. Validate Menu Block
    const menuSection = authenticatedPage.locator('#menu-v2');
    await expect(menuSection).toBeVisible();
    // Check Title
    await expect(menuSection.locator('h2')).toHaveText('Notre Carte');
    // Check Tabs
    await expect(menuSection.getByRole('button', { name: 'Entrées' })).toBeVisible();
    await expect(menuSection.getByRole('button', { name: 'Plats' })).toBeVisible();
    
    // Check Items (Default active tab is usually the first one)
    await expect(menuSection.locator('text=Carpaccio de Saint-Jacques')).toBeVisible();
    await expect(menuSection.locator('text=22 €')).toBeVisible();

    // Switch Tab
    await menuSection.getByRole('button', { name: 'Plats' }).click();
    await expect(menuSection.locator('text=Filet de Bœuf Rossini')).toBeVisible();

    // 5. Validate Footer Restaurant
    const footerSection = authenticatedPage.locator('#footer-v2');
    await expect(footerSection).toBeVisible();
    // Check Opening Hours presence
    await expect(footerSection.locator('text=Horaires')).toBeVisible();
    await expect(footerSection.locator('text=Lundi - Vendredi')).toBeVisible();
    // Check Contact
    await expect(footerSection.locator('text=123 Avenue des Champs, Paris')).toBeVisible();
    // Check Newsletter
    await expect(footerSection.locator('text=Newsletter')).toBeVisible();
  });
});
