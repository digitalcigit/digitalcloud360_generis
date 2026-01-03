#!/usr/bin/env python3
"""
Test E2E pour vérifier que business_name est correctement préservé
du onboarding à la génération du site.
"""

import asyncio
import json
import httpx
import uuid
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
}

# Test data
TEST_BUSINESS_NAME = f"TestBusiness_{datetime.now().strftime('%H%M%S')}"
TEST_SECTOR = "tech"
TEST_USER_ID = 1

async def test_e2e_flow():
    """Test complet du flux onboarding -> coaching -> site generation"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "="*80)
        print("TEST E2E: Business Name Preservation")
        print("="*80)
        
        # Step 1: Get auth token
        print("\n[1/5] Obtaining auth token...")
        token_response = await client.post(
            f"{API_BASE}/auth/token/",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        if token_response.status_code != 200:
            print(f"❌ Failed to get token: {token_response.status_code}")
            print(token_response.text)
            return False
        
        token = token_response.json()["access"]
        headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        print(f"✅ Token obtained: {token[:20]}...")
        
        # Step 2: Onboarding
        print(f"\n[2/5] Onboarding with business_name='{TEST_BUSINESS_NAME}'...")
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
        print(f"✅ Onboarding successful")
        print(f"   Session ID: {session_id}")
        print(f"   Business Name: {onboarding_data['onboarding']['business_name']}")
        
        # Step 3: Start coaching session (WITH session_id from onboarding)
        print(f"\n[3/5] Starting coaching session with session_id={session_id}...")
        start_response = await client.post(
            f"{API_BASE}/coaching/start",
            json={"session_id": session_id},
            headers=headers
        )
        
        if start_response.status_code != 200:
            print(f"❌ Start coaching failed: {start_response.status_code}")
            print(start_response.text)
            return False
        
        coaching_data = start_response.json()
        returned_session_id = coaching_data["session_id"]
        print(f"✅ Coaching session started")
        print(f"   Returned Session ID: {returned_session_id}")
        print(f"   Current Step: {coaching_data['current_step']}")
        
        # Verify session_id is preserved
        if returned_session_id != session_id:
            print(f"❌ ERROR: Session ID mismatch!")
            print(f"   Expected: {session_id}")
            print(f"   Got: {returned_session_id}")
            return False
        
        # Step 4: Complete coaching steps
        print(f"\n[4/5] Completing coaching steps...")
        steps_data = {
            "vision": "Créer une plateforme SaaS innovante pour les entrepreneurs",
            "mission": "Aider les entrepreneurs à automatiser leur business",
            "clientele": "PME et startups en Afrique de l'Ouest",
            "differentiation": "IA personnalisée et support en français",
            "offre": "Plateforme SaaS avec coaching IA intégré"
        }
        
        step_names = ["vision", "mission", "clientele", "differentiation", "offre"]
        for i, step_name in enumerate(step_names, 1):
            step_response = await client.post(
                f"{API_BASE}/coaching/step",
                json={
                    "session_id": session_id,
                    "user_response": steps_data[step_name]
                },
                headers=headers
            )
            
            if step_response.status_code != 200:
                print(f"❌ Step {step_name} failed: {step_response.status_code}")
                print(step_response.text)
                return False
            
            print(f"   ✅ Step {i}/5 ({step_name}) completed")
        
        # Step 5: Verify business_name in logs
        print(f"\n[5/5] Verifying business_name preservation...")
        
        # Get logs from container
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "genesis-api", "--tail", "200"],
            capture_output=True,
            text=True,
            cwd="c:\\genesis"
        )
        
        logs = result.stdout + result.stderr
        
        # Check for key log entries
        checks = {
            "onboarding_saved": f"business_name='{TEST_BUSINESS_NAME}'",
            "coaching_start_request": f"received_session_id={session_id}",
            "business_brief_constructed": f"business_name='{TEST_BUSINESS_NAME}'",
        }
        
        all_passed = True
        for check_name, check_value in checks.items():
            if check_value in logs:
                print(f"   ✅ {check_name}: Found '{check_value}'")
            else:
                print(f"   ❌ {check_name}: NOT found '{check_value}'")
                all_passed = False
        
        if all_passed:
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED - business_name correctly preserved!")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("❌ SOME TESTS FAILED")
            print("="*80)
            print("\nRelevant logs:")
            for line in logs.split('\n'):
                if TEST_BUSINESS_NAME in line or session_id in line:
                    print(f"  {line}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_e2e_flow())
    exit(0 if success else 1)
