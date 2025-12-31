"""
Script de test pour valider le ThemeRecommendationAgent.
Vérifie qu'un restaurant matche avec 'Savor'.
"""

import asyncio
import sys
from pathlib import Path
import json

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models.theme import Theme
from app.core.agents.theme_recommender import ThemeRecommendationAgent

async def test_recommendation_restaurant():
    print("\n" + "="*60)
    print("🧪 TEST: RECOMMANDATION THÈME POUR RESTAURANT")
    print("="*60 + "\n")
    
    # Simuler un brief de restaurant
    restaurant_brief = {
        "business_name": "Le Gourmet Dakarois",
        "industry_sector": "restaurant",
        "vision": "Devenir la référence de la cuisine fusion ouest-africaine à Dakar.",
        "mission": "Offrir une expérience culinaire unique mêlant tradition et modernité dans un cadre chaleureux.",
        "target_market": "Jeunes cadres, touristes gourmets et familles cherchant de la qualité.",
        "competitive_advantage": "Ingrédients 100% locaux, recettes ancestrales revisitées par un chef étoilé.",
        "value_proposition": "Une explosion de saveurs africaines dans un écrin de modernité."
    }
    
    try:
        async with AsyncSessionLocal() as session:
            # Charger les thèmes depuis la DB
            result = await session.execute(select(Theme).where(Theme.is_active == True))
            themes = result.scalars().all()
            
            if not themes:
                print("❌ Erreur: Aucun thème trouvé en base. Lancez le seed d'abord.")
                return

            print(f"🔍 Analyse du brief pour {restaurant_brief['business_name']}...")
            print(f"📚 {len(themes)} thèmes chargés pour comparaison.\n")
            
            agent = ThemeRecommendationAgent()
            recommendations = await agent.recommend(restaurant_brief, themes)
            
            print("📊 RÉSULTATS DE L'AGENT:")
            print("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                status = "✅" if (i == 1 and rec.slug == "savor") else "  "
                print(f"{status} {i}. THÈME: {rec.slug.upper()} | SCORE: {rec.match_score}%")
                print(f"   💡 RAISON: {rec.reasoning}\n")
            
            # Vérifier si Savor est premier
            if recommendations and recommendations[0].slug == "savor":
                print("🎉 SUCCÈS: 'Savor' est la recommandation #1 pour un restaurant !")
            else:
                print("⚠️  AVERTISSEMENT: 'Savor' n'est pas arrivé en tête. Vérifiez la logique ou les tags.")
            
    except Exception as e:
        print(f"\n❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_recommendation_restaurant())
