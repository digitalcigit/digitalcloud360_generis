#!/usr/bin/env python3
"""
Test E2E avec les identifiants fournis: dcitest@digital.ci / DiGiT@2025
"""

import asyncio
import json
import httpx
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = "dcitest@digital.ci"
TEST_PASSWORD = "DiGiT@2025"
TEST_BUSINESS_NAME = f"TestBiz_{datetime.now().strftime('%H%M%S')}"
TEST_SECTOR = "tech"

async def test_e2e():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "="*80)
        print("TEST E2E: Business Name Preservation")
        print("="*80)
        
        # Step 1: Get token
        print(f"\n[1/5] Login avec {TEST_EMAIL}...")
        try:
            token_response = await client.post(
                f"{API_BASE}/auth/token/",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if token_response.status_code != 200:
                print(f"❌ Login failed: {token_response.status_code}")
                print(token_response.text)
                return False
            
            token = token_response.json()["access"]
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            print(f"✅ Authentification réussie")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Step 2: Onboarding
        print(f"\n[2/5] Onboarding avec business_name='{TEST_BUSINESS_NAME}'...")
        try:
            onboarding_response = await client.post(
                f"{API_BASE}/coaching/onboarding",
                json={
                    "business_name": TEST_BUSINESS_NAME,
                    "sector": TEST_SECTOR,
                    "logo_source": "later"
                },
                headers=headers
            )
            
            if onboarding_response.status_code != 201:
                print(f"❌ Onboarding failed: {onboarding_response.status_code}")
                print(onboarding_response.text)
                return False
            
            onboarding_data = onboarding_response.json()
            session_id = onboarding_data["session_id"]
            print(f"✅ Onboarding réussi")
            print(f"   Session ID: {session_id}")
            print(f"   Business Name: {onboarding_data['onboarding']['business_name']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Step 3: Start coaching
        print(f"\n[3/5] Démarrage coaching avec session_id={session_id}...")
        try:
            start_response = await client.post(
                f"{API_BASE}/coaching/start",
                json={"session_id": session_id},
                headers=headers
            )
            
            if start_response.status_code != 200:
                print(f"❌ Start failed: {start_response.status_code}")
                print(start_response.text)
                return False
            
            coaching_data = start_response.json()
            returned_session_id = coaching_data["session_id"]
            
            if returned_session_id != session_id:
                print(f"❌ Session ID mismatch!")
                print(f"   Expected: {session_id}")
                print(f"   Got: {returned_session_id}")
                return False
            
            print(f"✅ Coaching démarré")
            print(f"   Session ID préservé: {returned_session_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Step 4: Complete steps
        print(f"\n[4/5] Complétion des étapes coaching...")
        steps_data = {
            "vision": "Créer une plateforme SaaS innovante",
            "mission": "Aider les entrepreneurs",
            "clientele": "PME en Afrique",
            "differentiation": "IA personnalisée",
            "offre": "Plateforme SaaS"
        }
        
        for i, (step_name, response_text) in enumerate(steps_data.items(), 1):
            try:
                step_response = await client.post(
                    f"{API_BASE}/coaching/step",
                    json={
                        "session_id": session_id,
                        "user_response": response_text
                    },
                    headers=headers
                )
                
                if step_response.status_code != 200:
                    print(f"❌ Step {step_name} failed: {step_response.status_code}")
                    return False
                
                print(f"   ✅ Étape {i}/5 ({step_name})")
            except Exception as e:
                print(f"❌ Error on step {step_name}: {e}")
                return False
        
        # Step 5: Verify logs
        print(f"\n[5/5] Vérification dans les logs...")
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "genesis-api", "--tail", "300"],
            capture_output=True,
            text=True
        )
        
        logs = result.stdout + result.stderr
        
        checks = {
            "onboarding_saved": TEST_BUSINESS_NAME,
            "coaching_start_request": session_id,
            "business_brief_constructed": TEST_BUSINESS_NAME,
        }
        
        all_passed = True
        for check_name, check_value in checks.items():
            found = False
            for line in logs.split('\n'):
                if check_name in line and check_value in line:
                    found = True
                    break
            
            if found:
                print(f"   ✅ {check_name}: FOUND")
            else:
                print(f"   ❌ {check_name}: NOT FOUND")
                all_passed = False
        
        if all_passed:
            print("\n" + "="*80)
            print("✅ TEST RÉUSSI - business_name correctement préservé!")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("❌ TEST ÉCHOUÉ")
            print("="*80)
            return False

if __name__ == "__main__":
    success = asyncio.run(test_e2e())
    exit(0 if success else 1)
