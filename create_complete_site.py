"""Créer un site complet Chez Maman Afrique via l'orchestrateur"""
import asyncio
import json
import uuid
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData
from app.core.integrations.redis_fs import RedisVirtualFileSystem

async def create_complete_site():
    session_id = str(uuid.uuid4())
    print(f"=== CRÉATION SITE COMPLET ===")
    print(f"Session ID: {session_id}")
    print()
    
    # 1. Business brief complet
    business_brief = {
        "business_name": "Chez Maman Afrique",
        "industry_sector": "restaurant",
        "location": {"city": "Abidjan", "country": "Cote d'Ivoire"},
        "vision": "Devenir LA reference de la cuisine africaine authentique a Abidjan, reconnu pour la qualite et l'accueil chaleureux",
        "mission": "Offrir une experience culinaire africaine authentique avec des recettes familiales transmises de generation en generation",
        "target_market": "Familles africaines, professionnels pour dejeuners, touristes decouvrant la gastronomie locale",
        "competitive_advantage": "Recettes familiales uniques depuis 3 generations. Ingredients frais du marche local. Ambiance familiale authentique.",
        "services": [
            {"title": "Restaurant sur place", "description": "Salle climatisee 50 couverts"},
            {"title": "Livraison", "description": "Livraison rapide dans Abidjan"},
            {"title": "Traiteur", "description": "Service traiteur pour evenements"},
            {"title": "Plats a emporter", "description": "Commandez et recuperez"}
        ]
    }
    
    # 2. Orchestration complète (tous les agents)
    print("🚀 Lancement orchestration (6 agents)...")
    orchestrator = LangGraphOrchestrator()
    
    orchestration_result = await orchestrator.run({
        "user_id": 1,
        "brief_id": session_id,
        "business_brief": business_brief
    })
    
    print(f"✅ Orchestration terminée: {orchestration_result.get('overall_confidence', 0):.0%} confiance")
    print()
    
    # 3. Transformer en SiteDefinition
    print("🔄 Transformation en SiteDefinition...")
    transformer = BriefToSiteTransformer()
    
    enriched_brief = BusinessBriefData(
        business_name=business_brief["business_name"],
        industry_sector=business_brief["industry_sector"],
        location=business_brief.get("location", {}),
        vision=business_brief.get("vision", ""),
        mission=business_brief.get("mission", ""),
        target_market=business_brief.get("target_market", ""),
        services=business_brief.get("services", []),
        competitive_advantage=business_brief.get("competitive_advantage", ""),
        market_research=orchestration_result.get("market_research", {}),
        content_generation=orchestration_result.get("content_generation", {}),
        logo_creation=orchestration_result.get("logo_creation", {}),
        image_generation=orchestration_result.get("image_generation", {}),
        template_selection=orchestration_result.get("template_selection", {}),
        seo_optimization=orchestration_result.get("seo_optimization", {})
    )
    
    site_definition = transformer.transform(enriched_brief)
    
    # 4. Sauvegarder en Redis
    print("💾 Sauvegarde en Redis...")
    redis = RedisVirtualFileSystem()
    await redis.write_file(f"site:{session_id}", json.dumps(site_definition))
    
    # 5. Afficher résumé
    print()
    print("=== SITE GÉNÉRÉ ===")
    print(f"Business: {site_definition.get('metadata', {}).get('business_name', 'N/A')}")
    
    theme = site_definition.get("theme", {})
    colors = theme.get("colors", {})
    print(f"Theme: primary={colors.get('primary')}, secondary={colors.get('secondary')}")
    
    fonts = theme.get("fonts", {})
    print(f"Fonts: heading={fonts.get('heading')}, body={fonts.get('body')}")
    
    pages = site_definition.get("pages", [])
    if pages:
        sections = pages[0].get("sections", [])
        print(f"Sections: {len(sections)}")
        for s in sections[:5]:
            print(f"  - {s.get('type')}: {s.get('data', {}).get('title', '')[:40]}")
    
    print()
    print(f"🌐 PREVIEW URL: http://localhost:3002/preview/{session_id}")
    
    return session_id

if __name__ == "__main__":
    session_id = asyncio.run(create_complete_site())
    print(f"\nOuvrez: http://localhost:3002/preview/{session_id}")
