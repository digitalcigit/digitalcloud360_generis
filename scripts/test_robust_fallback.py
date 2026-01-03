
import asyncio
import json
from typing import Dict, Any

async def test_robust_fallback():
    # Test case 1: Key exists but is None
    onboarding = {"business_name": None}
    business_name = onboarding.get("business_name") or "Projet Sans Nom"
    print(f"Case 1 (None): {business_name} - Expected: Projet Sans Nom")
    assert business_name == "Projet Sans Nom"

    # Test case 2: Key exists but is empty string
    onboarding = {"business_name": ""}
    business_name = onboarding.get("business_name") or "Projet Sans Nom"
    print(f"Case 2 (Empty): {business_name} - Expected: Projet Sans Nom")
    assert business_name == "Projet Sans Nom"

    # Test case 3: Key exists and has value
    onboarding = {"business_name": "My Business"}
    business_name = onboarding.get("business_name") or "Projet Sans Nom"
    print(f"Case 3 (Value): {business_name} - Expected: My Business")
    assert business_name == "My Business"

    # Test case 4: Key does not exist
    onboarding = {}
    business_name = onboarding.get("business_name") or "Projet Sans Nom"
    print(f"Case 4 (Missing): {business_name} - Expected: Projet Sans Nom")
    assert business_name == "Projet Sans Nom"

if __name__ == "__main__":
    asyncio.run(test_robust_fallback())
    print("All tests passed!")
