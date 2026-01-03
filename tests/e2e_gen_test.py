import asyncio
import httpx
import json
import sys
import os

# Default to internal Docker port if running inside container, or override via env
BASE_URL = os.getenv("GENESIS_API_URL", "http://localhost:8000")

async def run_test():
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Onboarding
        print("1. Onboarding...")
        onboarding_payload = {
            "business_name": "Chez Tante Awa",
            "sector": "restaurant",
            "logo_source": "later"
        }
        # Assuming we need a token or dev-token. The backend might allow unauth for dev or we can get one.
        # Let's try to get a dev token first if endpoint exists, otherwise proceed (backend might be open in dev).
        # Based on previous file reads, there is auth.
        
        # Simulating auth flow might be complex. Let's try to grab a token first.
        # c:\genesis\genesis-frontend\src\app\coaching\onboarding\page.tsx uses /api/auth/dev-token on frontend which proxies to backend?
        # Let's assume we can get a token or bypass if we are local.
        # Actually, let's use the `run_command` to get a token via a script if needed, or just try to hit the endpoints.
        # Wait, the frontend calls `coachingApi`.
        
        # Let's look at `app/main.py` or auth routes to see how to get a token easily.
        # Or I can just check if I can generate a token via python using the app code directly? No, running alongside.
        
        # Let's try to login as a test user or create one.
        # Alternatively, since I have access to the codebase, I can perhaps run a script that imports app code and runs the logic directly?
        # That might be safer than relying on HTTP if I don't have a user.
        # But `run_command` runs in the shell.
        
        # Let's try to use the API.
        # Create a test user first?
        # Or maybe there's a hardcoded dev token.
        
        # Try to get dev token first
        print("   Getting dev token...")
        try:
            resp = await client.get(f"{BASE_URL}/api/v1/auth/dev-token")
            if resp.status_code == 200:
                token = resp.json()["access_token"]
                print("   Got dev token.")
            else:
                raise Exception("Dev token not available")
        except Exception:
            # Register user
            email = "test_e2e_v2@example.com"
            password = "password123"
            
            print("   Registering/Logging in...")
            try:
                resp = await client.post(f"{BASE_URL}/api/v1/auth/register", json={"email": email, "password": password, "name": "Test User"})
                if resp.status_code not in [200, 201, 400]: # 400 if exists
                     print(f"Register failed: {resp.text}")
                     return
            except Exception as e:
                print(f"Register exception: {e}")
                
            # Login
            resp = await client.post(f"{BASE_URL}/api/v1/auth/token", data={"username": email, "password": password})
            if resp.status_code != 200:
                print(f"Login failed: {resp.text}")
                return
                
            token = resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        
        # Onboarding
        print(f"   Using Token: {token[:10]}...")
        resp = await client.post(f"{BASE_URL}/api/v1/coaching/onboarding", json=onboarding_payload, headers=headers)
        if resp.status_code not in [200, 201]:
            print(f"Onboarding failed: {resp.text}")
            return
        session_id = resp.json()["session_id"]
        print(f"   Session ID: {session_id}")
        
        # Start
        resp = await client.post(f"{BASE_URL}/api/v1/coaching/start", json={"session_id": session_id}, headers=headers)
        
        # Steps
        steps = [
            ("vision", "Je veux devenir le restaurant de référence pour le Tiep bou dien authentique à Dakar, dans une ambiance familiale."),
            ("mission", "Offrir des plats généreux, faits maison avec des produits frais du marché, comme si on mangeait à la maison."),
            ("clientele", "Les travailleurs du quartier Plateau le midi, et les familles le soir et weekend."),
            ("differentiation", "Ma sauce secrète transmise par ma grand-mère et l'accueil légendaire de mon équipe."),
            ("offre", "Un menu simple : Tiep rouge, Tiep blanc, Yassa poulet, et Jus de Bissap. Prix accessibles.")
        ]
        
        for step_name, response_text in steps:
            print(f"2. Sending Step: {step_name}...")
            payload = {
                "session_id": session_id,
                "user_response": response_text
            }
            resp = await client.post(f"{BASE_URL}/api/v1/coaching/step", json=payload, headers=headers)
            if resp.status_code != 200:
                print(f"Step {step_name} failed: {resp.text}")
                return
            data = resp.json()
            if data.get("is_step_complete") and step_name == "offre":
                print("   Generation triggered!")
                
        # Now wait for generation (polling Redis or checking status? The last step response includes site_data if complete)
        # The last step response `data` might already have `site_data` if `is_step_complete` is True.
        
        site_data = data.get("site_data")
        if not site_data:
            print("   Site data not in immediate response, checking Redis...")
            # We can't check Redis easily from here without redis-py, but let's assume it should be in response
            # based on `app/api/v1/coaching.py`.
            pass
            
        if site_data:
            print("\n--- VALIDATION RESULTS ---")
            
            # 1. Check Smart Content (Features/Menu)
            print("\n[SMART CONTENT]")
            features = site_data.get("pages", [{}])[0].get("sections", [])
            feature_section = next((s for s in features if s["type"] == "features"), None)
            if feature_section:
                print(f"Title: {feature_section['content']['title']}")
                print(f"Subtitle: {feature_section['content']['subtitle']}")
                for item in feature_section['content']['features']:
                    print(f"- {item['title']}: {item['description']} (Image: {'YES' if item.get('image') else 'NO'})")
            else:
                print("FAILED: No features section found.")

            # 2. Check Visual Soul (Images)
            print("\n[VISUAL SOUL]")
            hero_section = next((s for s in features if s["type"] == "hero"), None)
            if hero_section:
                print(f"Hero Image: {hero_section['content']['image']}")
            
            services_section = next((s for s in features if s["type"] == "services"), None)
            if services_section:
                print("Service Images:")
                for svc in services_section['content']['services']:
                    print(f"- {svc['title']}: Image={'YES' if svc.get('image') else 'NO'}")

            # 3. Check Copywriting
            print("\n[COPYWRITING]")
            if hero_section:
                print(f"Hero Title: {hero_section['content']['title']}")
                print(f"Hero Subtitle: {hero_section['content']['subtitle']}")
                print(f"Hero Desc: {hero_section['content']['description']}")
                
            footer_section = next((s for s in features if s["type"] == "footer"), None)
            if footer_section:
                print(f"Footer Desc: {footer_section['content']['description']}")

if __name__ == "__main__":
    asyncio.run(run_test())
