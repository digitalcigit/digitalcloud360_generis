#!/usr/bin/env python3
"""
Test E2E Playwright - Coaching Flow
Teste le processus complet d'onboarding et coaching via UI
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_coaching_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Naviguer vers la page d'onboarding
            print("📍 Navigating to onboarding page...")
            await page.goto("http://localhost:3002/coaching/onboarding")
            await page.wait_for_load_state("networkidle")
            
            # 2. Injecter le token valide
            print("🔐 Injecting auth token...")
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcl9pZCI6MSwiZXhwIjoxNzY5MTI4MDc3fQ.J6McLsG4fXMcXf9EjXRvUgP9D__PV3eei4lDS5gSr-g"
            await page.evaluate(f"""
                localStorage.setItem('auth-storage', JSON.stringify({{
                    state: {{ token: '{token}', user: {{ id: 1, email: 'test.po@example.com' }} }},
                    version: 0
                }}));
            """)
            
            # 3. Remplir le formulaire d'onboarding
            print("📝 Filling onboarding form...")
            await page.fill('input[placeholder="Mon Super Business"]', "Mon Restaurant Africain")
            
            # 4. Sélectionner le secteur
            await page.select_option('select', "restaurant")
            
            # 5. Cliquer sur "Plus tard" pour le logo
            print("⏭️ Skipping logo upload...")
            await page.click('button:has-text("⏭️ Plus tard")')
            await page.wait_for_timeout(1000)
            
            # 6. Soumettre le formulaire
            print("✅ Submitting onboarding form...")
            await page.click('button:has-text("Commencer le coaching")')
            
            # 7. Attendre la redirection vers la page de coaching
            print("⏳ Waiting for coaching page...")
            await page.wait_for_url("**/coaching", timeout=10000)
            
            # 8. Vérifier que la page de coaching est chargée
            title = await page.title()
            print(f"✅ Successfully navigated to coaching page: {title}")
            
            # 9. Vérifier la présence d'éléments clés
            content = await page.content()
            if "Vision" in content or "coaching" in content.lower():
                print("✅ Coaching page content verified")
            else:
                print("⚠️ Coaching page content not as expected")
            
            # Prendre une capture d'écran
            await page.screenshot(path="coaching_page.png")
            print("📸 Screenshot saved: coaching_page.png")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path="error_screenshot.png")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_coaching_flow())
    exit(0 if success else 1)
