---
title: "Work Order GEN-12 - Tests E2E Playwright"
tags: ["playwright", "e2e", "testing", "sprint-5", "genesis-ai"]
status: "ready"
date: "2025-12-17"
assignee: "Dev Senior"
estimation: "9h (~1.1 jours)"
priority: "medium"
---

# 📋 WORK ORDER GEN-12 — Tests E2E Playwright

**Date :** 17/12/2025  
**Tech Lead :** Cascade  
**Sprint :** 5 (final story)  
**Dépendance :** GEN-11 (Preview Page) ✅ Complété

---

## 🎯 Objectif

Valider automatiquement le flux complet de bout en bout :

```
SSO Login → /chat → Message "site" → Brief généré → /preview/[siteId] → Site affiché
```

---

## 📦 Livrables

| # | Fichier | Description |
|---|---------|-------------|
| 1 | `genesis-frontend/playwright.config.ts` | Configuration Playwright |
| 2 | `genesis-frontend/e2e/auth.spec.ts` | Test SSO → Chat page |
| 3 | `genesis-frontend/e2e/chat.spec.ts` | Test envoi message → réponse |
| 4 | `genesis-frontend/e2e/site-generation.spec.ts` | Test brief → preview visible |
| 5 | `genesis-frontend/e2e/preview.spec.ts` | Test navigation preview |
| 6 | `genesis-frontend/e2e/responsive.spec.ts` | Test responsive viewports |
| 7 | `tests/test_core/test_transformer.py` | Tests unitaires Transformer |
| 8 | `docs/TESTING_GUIDE.md` | Documentation scénarios |

---

## 📝 Sub-tasks Détaillées

### ST-1: Setup Playwright Config (1h)

**Fichier :** `genesis-frontend/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3002',
        trace: 'on-first-retry',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        {
            name: 'mobile',
            use: { ...devices['iPhone 13'] },
        },
        {
            name: 'tablet',
            use: { ...devices['iPad Pro'] },
        },
    ],
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3002',
        reuseExistingServer: !process.env.CI,
    },
});
```

**Dépendances à ajouter :**
```bash
npm install -D @playwright/test
npx playwright install
```

**Script package.json :**
```json
{
    "scripts": {
        "test:e2e": "playwright test",
        "test:e2e:ui": "playwright test --ui"
    }
}
```

---

### ST-2: Test Auth SSO → Chat (1h)

**Fichier :** `genesis-frontend/e2e/auth.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
    test('should redirect unauthenticated user to login', async ({ page }) => {
        await page.goto('/chat');
        
        // Should redirect to DC360 Hub or show auth error
        await expect(page).toHaveURL(/localhost:3000|login|unauthorized/);
    });

    test('should access chat page with valid SSO token', async ({ page, context }) => {
        // Setup: Inject mock auth cookie
        await context.addCookies([{
            name: 'access_token',
            value: process.env.TEST_ACCESS_TOKEN || 'mock_token_for_e2e',
            domain: 'localhost',
            path: '/',
        }]);

        await page.goto('/chat');
        
        // Should see chat interface
        await expect(page.locator('text=Genesis AI')).toBeVisible();
        await expect(page.locator('input[placeholder*="business"]')).toBeVisible();
    });
});
```

**Note :** Pour les tests E2E réels, utiliser un token de test valide ou un mock auth.

---

### ST-3: Test Chat Message → Response (1h)

**Fichier :** `genesis-frontend/e2e/chat.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
    test.beforeEach(async ({ page, context }) => {
        // Setup auth
        await context.addCookies([{
            name: 'access_token',
            value: process.env.TEST_ACCESS_TOKEN || 'mock_token',
            domain: 'localhost',
            path: '/',
        }]);
        await page.goto('/chat');
    });

    test('should display welcome message', async ({ page }) => {
        await expect(page.locator('text=Genesis')).toBeVisible();
        await expect(page.locator('text=Parlez-moi')).toBeVisible();
    });

    test('should send message and receive response', async ({ page }) => {
        const input = page.locator('input[placeholder*="business"]');
        const sendButton = page.locator('button:has-text("Envoyer")');

        await input.fill('Je veux créer un site pour mon restaurant');
        await sendButton.click();

        // Wait for response
        await expect(page.locator('.bg-gray-700').last()).toBeVisible({ timeout: 10000 });
    });
});
```

---

### ST-4: Test Brief → Site Preview (2h) ⚡ Critique

**Fichier :** `genesis-frontend/e2e/site-generation.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Site Generation Flow', () => {
    test.beforeEach(async ({ page, context }) => {
        await context.addCookies([{
            name: 'access_token',
            value: process.env.TEST_ACCESS_TOKEN || 'mock_token',
            domain: 'localhost',
            path: '/',
        }]);
    });

    test('should generate site and navigate to preview', async ({ page }) => {
        await page.goto('/chat');

        // Send message that triggers site generation
        const input = page.locator('input[placeholder*="business"]');
        await input.fill('Je veux créer un site pour mon entreprise');
        await page.locator('button:has-text("Envoyer")').click();

        // Wait for "Voir mon site" button
        const viewSiteButton = page.locator('button:has-text("Voir mon site")');
        await expect(viewSiteButton).toBeVisible({ timeout: 15000 });

        // Click and verify navigation to preview
        await viewSiteButton.click();
        await expect(page).toHaveURL(/\/preview\/site_/);
    });

    test('should display site preview with toolbar', async ({ page }) => {
        // Assuming we have a valid site_id from previous test
        // In real scenario, this would use a fixture or setup step
        await page.goto('/chat');
        
        // Trigger generation
        await page.locator('input[placeholder*="business"]').fill('site web');
        await page.locator('button:has-text("Envoyer")').click();
        
        // Navigate to preview
        await page.locator('button:has-text("Voir mon site")').click({ timeout: 15000 });

        // Verify toolbar elements
        await expect(page.locator('[aria-label="Viewport mobile"]')).toBeVisible();
        await expect(page.locator('[aria-label="Viewport desktop"]')).toBeVisible();
        await expect(page.locator('[aria-label="Plein écran"]')).toBeVisible();
    });
});
```

---

### ST-5: Test Preview Navigation (1h)

**Fichier :** `genesis-frontend/e2e/preview.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Preview Page', () => {
    test('should show error for invalid siteId', async ({ page, context }) => {
        await context.addCookies([{
            name: 'access_token',
            value: 'mock_token',
            domain: 'localhost',
            path: '/',
        }]);

        // Invalid siteId format
        await page.goto('/preview/invalid-id');
        await expect(page.locator('text=ID de site invalide')).toBeVisible();
    });

    test('should navigate back to chat', async ({ page, context }) => {
        await context.addCookies([{
            name: 'access_token',
            value: 'mock_token',
            domain: 'localhost',
            path: '/',
        }]);

        // Valid format but non-existent
        await page.goto('/preview/site_00000000-0000-0000-0000-000000000000');
        
        // Click back button
        await page.locator('[aria-label="Retour au chat"]').click();
        await expect(page).toHaveURL('/chat');
    });
});
```

---

### ST-6: Test Responsive Viewports (1h)

**Fichier :** `genesis-frontend/e2e/responsive.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
    test.beforeEach(async ({ context }) => {
        await context.addCookies([{
            name: 'access_token',
            value: 'mock_token',
            domain: 'localhost',
            path: '/',
        }]);
    });

    test('chat page on mobile', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/chat');
        
        // Should be visible and usable on mobile
        await expect(page.locator('input[placeholder*="business"]')).toBeVisible();
    });

    test('chat page on tablet', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto('/chat');
        
        await expect(page.locator('input[placeholder*="business"]')).toBeVisible();
    });

    test('preview toolbar viewport switching', async ({ page }) => {
        await page.goto('/chat');
        
        // Generate site first
        await page.locator('input[placeholder*="business"]').fill('site');
        await page.locator('button:has-text("Envoyer")').click();
        await page.locator('button:has-text("Voir mon site")').click({ timeout: 15000 });

        // Test viewport buttons
        await page.locator('[aria-label="Viewport mobile"]').click();
        await page.locator('[aria-label="Viewport tablette"]').click();
        await page.locator('[aria-label="Viewport desktop"]').click();
    });
});
```

---

### ST-7: Tests Unitaires Transformer (1.5h)

**Fichier :** `tests/test_core/test_transformer.py`

```python
import pytest
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData, ServiceItem


@pytest.fixture
def transformer():
    return BriefToSiteTransformer()


@pytest.fixture
def sample_brief():
    return BusinessBriefData(
        business_name="Mon Restaurant",
        sector="restaurant",
        mission="Offrir une cuisine authentique",
        services=[
            ServiceItem(title="Cuisine traditionnelle", description="Plats du terroir"),
            ServiceItem(title="Livraison", description="À domicile"),
        ],
        email="contact@monrestaurant.com",
        phone="+33 1 23 45 67 89",
    )


class TestBriefToSiteTransformer:
    def test_transform_returns_valid_structure(self, transformer, sample_brief):
        result = transformer.transform(sample_brief)
        
        assert "metadata" in result
        assert "theme" in result
        assert "pages" in result
        assert len(result["pages"]) > 0

    def test_transform_includes_business_name(self, transformer, sample_brief):
        result = transformer.transform(sample_brief)
        
        # Business name should appear in hero or metadata
        assert result["metadata"]["site_name"] == "Mon Restaurant"

    def test_transform_maps_services(self, transformer, sample_brief):
        result = transformer.transform(sample_brief)
        
        # Find services section
        home_page = result["pages"][0]
        services_section = next(
            (s for s in home_page["sections"] if s["type"] == "services"),
            None
        )
        
        assert services_section is not None
        assert len(services_section["content"]["items"]) == 2

    def test_transform_sector_fallback(self, transformer):
        brief = BusinessBriefData(
            business_name="Unknown Sector",
            sector="unknown_sector_xyz",
        )
        
        result = transformer.transform(brief)
        
        # Should use default template
        assert result is not None
        assert "pages" in result

    def test_transform_contact_info(self, transformer, sample_brief):
        result = transformer.transform(sample_brief)
        
        home_page = result["pages"][0]
        contact_section = next(
            (s for s in home_page["sections"] if s["type"] == "contact"),
            None
        )
        
        assert contact_section is not None
        assert "contact@monrestaurant.com" in str(contact_section)
```

---

### ST-8: Documentation (0.5h)

**Fichier :** `docs/TESTING_GUIDE.md`

```markdown
# Guide de Tests — Genesis AI

## Tests Unitaires (Jest)

```bash
cd genesis-frontend
npm test
```

## Tests E2E (Playwright)

### Prérequis
- Docker running avec les services genesis-api et frontend
- Token de test valide (ou mock auth)

### Exécution locale
```bash
cd genesis-frontend
npm run test:e2e
```

### Exécution avec UI
```bash
npm run test:e2e:ui
```

### Exécution Docker
```bash
docker-compose -f docker-compose.test.yml up e2e-tests
```

## Tests Backend (pytest)

```bash
docker-compose exec genesis-api pytest tests/
```

## Scénarios Couverts

| Scénario | Fichier | Criticité |
|----------|---------|-----------|
| Auth SSO → Chat | `e2e/auth.spec.ts` | 🔴 Haute |
| Chat message → Response | `e2e/chat.spec.ts` | 🔴 Haute |
| Brief → Site Preview | `e2e/site-generation.spec.ts` | 🔴 Haute |
| Preview navigation | `e2e/preview.spec.ts` | 🟡 Moyenne |
| Responsive viewports | `e2e/responsive.spec.ts` | 🟡 Moyenne |
| Transformer unit | `test_transformer.py` | 🟡 Moyenne |

## CI/CD

Les tests E2E sont exécutés automatiquement sur chaque PR via GitHub Actions.
```

---

## 🔧 Configuration Docker pour Tests

**Fichier :** `docker-compose.test.yml`

```yaml
version: '3.8'

services:
  e2e-tests:
    image: mcr.microsoft.com/playwright:v1.40.0-jammy
    working_dir: /app
    volumes:
      - ./genesis-frontend:/app
    environment:
      - PLAYWRIGHT_BASE_URL=http://frontend:3000
      - CI=true
    depends_on:
      - frontend
      - genesis-api
    networks:
      - genesis-ai-network
    command: npx playwright test
```

---

## ✅ Critères de Validation

| Critère | Condition |
|---------|-----------|
| Playwright setup | `npx playwright test` s'exécute sans erreur |
| Tests auth | Login mock fonctionne |
| Tests chat | Message → Response OK |
| Tests generation | Brief → Preview visible |
| Tests responsive | 3 viewports testés |
| Tests backend | pytest green |
| Documentation | Guide complet |

---

## 📊 Estimation

| Sub-task | Estimation |
|----------|------------|
| ST-1 Setup Playwright | 1h |
| ST-2 Test Auth | 1h |
| ST-3 Test Chat | 1h |
| ST-4 Test Generation | 2h |
| ST-5 Test Preview | 1h |
| ST-6 Test Responsive | 1h |
| ST-7 Tests Transformer | 1.5h |
| ST-8 Documentation | 0.5h |
| **TOTAL** | **9h** |

---

## 🚀 Commandes de Livraison

```bash
# Branche
git checkout -b feature/gen-12-e2e-tests

# Validation locale
cd genesis-frontend
npm install -D @playwright/test
npx playwright install
npm run test:e2e

# Backend tests
docker-compose exec genesis-api pytest tests/test_core/test_transformer.py

# Push
git add .
git commit -m "test(GEN-12): E2E Playwright + Transformer unit tests"
git push origin feature/gen-12-e2e-tests

# PR
gh pr create --title "test(GEN-12): E2E tests Playwright" --base master
```

---

*Tech Lead Genesis AI — 17/12/2025*
