"""Test complet orchestration Phase 2 Premium"""
import asyncio
import json
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator

async def generate_site():
    orchestrator = LangGraphOrchestrator()
    
    business_brief = {
        "business_name": "Chez Maman Afrique",
        "industry_sector": "restaurant",
        "location": {"city": "Abidjan", "country": "Cote d'Ivoire"},
        "vision": "Devenir LA reference de la cuisine africaine authentique a Abidjan",
        "mission": "Offrir une experience culinaire africaine authentique avec des recettes traditionnelles",
        "target_market": "Familles, professionnels, touristes recherchant une cuisine africaine authentique",
        "competitive_advantage": "Recettes familiales transmises de generation en generation. Ingredients frais et locaux. Ambiance chaleureuse.",
        "services": [
            {"title": "Restaurant sur place", "description": "Salle climatisee 50 couverts"},
            {"title": "Livraison", "description": "Livraison rapide dans Abidjan"},
            {"title": "Traiteur", "description": "Service traiteur pour evenements"},
            {"title": "Plats a emporter", "description": "Commandez et recuperez"}
        ]
    }
    
    print("=== LANCEMENT ORCHESTRATION PHASE 2 PREMIUM ===")
    print("Business: Chez Maman Afrique (restaurant)")
    print("Agents: Research -> Content -> Logo -> Images -> SEO -> Template")
    print()
    
    result = await orchestrator.run({
        "user_id": 1,
        "brief_id": "test-chez-maman-afrique",
        "business_brief": business_brief
    })
    
    print()
    print("=== RESULTATS ORCHESTRATION ===")
    print(f"Confidence: {result.get('overall_confidence', 0):.0%}")
    print(f"Ready for website: {result.get('is_ready_for_website', False)}")
    print()
    
    # Logo
    logo = result.get("logo_creation", {})
    logo_url = logo.get("logo_url", "N/A")
    print(f"LOGO: {logo_url[:80]}..." if len(str(logo_url)) > 80 else f"LOGO: {logo_url}")
    
    # Images
    images = result.get("image_generation", {})
    hero = images.get("hero_image", {})
    hero_url = hero.get("image_url", "N/A") if isinstance(hero, dict) else str(hero)
    print(f"HERO IMAGE: {hero_url[:80]}..." if len(str(hero_url)) > 80 else f"HERO IMAGE: {hero_url}")
    
    # Theme
    theme_result = result.get("template_selection", {})
    theme = theme_result.get("theme", {})
    colors = theme.get("colors", {})
    fonts = theme.get("fonts", {})
    print(f"TEMPLATE: {theme_result.get('template_name', 'N/A')}")
    print(f"COLORS: primary={colors.get('primary')}, secondary={colors.get('secondary')}, accent={colors.get('accent')}")
    print(f"FONTS: heading={fonts.get('heading')}, body={fonts.get('body')}")
    
    # SEO
    seo = result.get("seo_optimization", {})
    print(f"SEO TITLE: {seo.get('meta_title', 'N/A')}")
    print(f"SEO KEYWORDS: {seo.get('primary_keywords', [])[:5]}")
    
    return result

if __name__ == "__main__":
    asyncio.run(generate_site())
