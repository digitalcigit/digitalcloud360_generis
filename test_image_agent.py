"""Test script for ImageAgent Phase 2 Premium - DALL-E 3"""
import asyncio
from app.core.agents.image import ImageAgent

async def test():
    agent = ImageAgent()
    
    print("=== TEST ImageAgent DALL-E 3 ===")
    print("Génération hero image pour 'Chez Maman Afrique' (restaurant)...")
    print()
    
    # Test génération hero uniquement via run()
    result = await agent.run(
        business_name="Chez Maman Afrique",
        industry_sector="restaurant",
        image_type="hero",
        context="cuisine africaine traditionnelle",
        style="professional"
    )
    
    print("=== RESULTAT ===")
    print(f"Image URL: {result.get('image_url', 'N/A')[:80]}...")
    print(f"Cached: {result.get('cached', False)}")
    meta = result.get('metadata', {})
    print(f"Prompt: {meta.get('prompt', 'N/A')[:100]}...")
    print(f"Source: {meta.get('source', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test())
