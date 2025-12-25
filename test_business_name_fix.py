#!/usr/bin/env python3
"""
Test script to verify that the business_name fix is working correctly.
This script tests the preserve_onboarding_on_save function and validates
that onboarding data is preserved across Redis updates.
"""

import asyncio
import json
import redis.asyncio as redis
from typing import Dict, Any

# Simulate the preserve_onboarding_on_save function
async def preserve_onboarding_on_save(session_id: str, session_data: Dict[str, Any], redis_client: redis.Redis, ttl: int = 7200):
    """Sauvegarde session_data en Redis en préservant TOUJOURS les données d'onboarding"""
    current_json = await redis_client.get(f"session:{session_id}")
    if current_json:
        current_data = json.loads(current_json)
        # Toujours préserver l'onboarding s'il existe
        if "onboarding" in current_data:
            session_data["onboarding"] = current_data["onboarding"]
    
    await redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=ttl)


async def test_preserve_onboarding():
    """Test that onboarding data is preserved across Redis updates"""
    
    # Connect to Redis
    redis_client = await redis.from_url("redis://localhost:6379")
    
    session_id = "test-session-710c4550"
    
    try:
        # Step 1: Initial onboarding data
        print("✓ Step 1: Saving initial onboarding data...")
        initial_data = {
            "session_id": session_id,
            "user_id": 123,
            "current_step": "vision",
            "onboarding": {
                "business_name": "Restaurant Le Baobab",
                "sector": "Restaurant / Alimentation",
                "sector_resolved": "restaurant"
            }
        }
        await redis_client.set(f"session:{session_id}", json.dumps(initial_data), ex=7200)
        
        # Verify initial data
        stored = await redis_client.get(f"session:{session_id}")
        stored_data = json.loads(stored)
        assert stored_data["onboarding"]["business_name"] == "Restaurant Le Baobab"
        print(f"  ✓ Initial data saved: business_name = '{stored_data['onboarding']['business_name']}'")
        
        # Step 2: Update session without onboarding (simulating /step endpoint)
        print("\n✓ Step 2: Updating session data (simulating /step endpoint)...")
        updated_data = {
            "session_id": session_id,
            "user_id": 123,
            "current_step": "mission",
            # NOTE: onboarding is NOT included here - this is the problem we're fixing
        }
        await preserve_onboarding_on_save(session_id, updated_data, redis_client)
        
        # Verify that onboarding was preserved
        stored = await redis_client.get(f"session:{session_id}")
        stored_data = json.loads(stored)
        assert "onboarding" in stored_data, "❌ Onboarding was lost!"
        assert stored_data["onboarding"]["business_name"] == "Restaurant Le Baobab"
        print(f"  ✓ Onboarding preserved after update: business_name = '{stored_data['onboarding']['business_name']}'")
        
        # Step 3: Multiple updates to verify persistence
        print("\n✓ Step 3: Testing multiple updates...")
        for step in ["clientele", "differentiation", "offre"]:
            updated_data = {
                "session_id": session_id,
                "user_id": 123,
                "current_step": step,
            }
            await preserve_onboarding_on_save(session_id, updated_data, redis_client)
            
            stored = await redis_client.get(f"session:{session_id}")
            stored_data = json.loads(stored)
            assert "onboarding" in stored_data, f"❌ Onboarding lost at step {step}!"
            assert stored_data["onboarding"]["business_name"] == "Restaurant Le Baobab"
            print(f"  ✓ Step '{step}': business_name still = '{stored_data['onboarding']['business_name']}'")
        
        # Step 4: Verify final state
        print("\n✓ Step 4: Final verification...")
        stored = await redis_client.get(f"session:{session_id}")
        stored_data = json.loads(stored)
        
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"   Final session data:")
        print(f"   - session_id: {stored_data['session_id']}")
        print(f"   - current_step: {stored_data['current_step']}")
        print(f"   - onboarding.business_name: {stored_data['onboarding']['business_name']}")
        print(f"   - onboarding.sector: {stored_data['onboarding']['sector']}")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    finally:
        # Cleanup
        await redis_client.delete(f"session:{session_id}")
        await redis_client.close()


if __name__ == "__main__":
    result = asyncio.run(test_preserve_onboarding())
    exit(0 if result else 1)
