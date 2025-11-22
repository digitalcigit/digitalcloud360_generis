"""
Script de tests manuels E2E - Phase 1 Sprint 3
Génération de 5 business briefs pour validation qualité

Usage:
    python scripts/test_manual_e2e.py
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime
import json
import io

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
import structlog

logger = structlog.get_logger()

# 5 Business Briefs de test
TEST_BRIEFS = [
    {
        "name": "Brief 1 - Startup Tech Dakar",
        "data": {
            "business_name": "TechHub Dakar",
            "vision": "Devenir la référence de l'innovation technologique en Afrique de l'Ouest d'ici 2030",
            "mission": "Démocratiser l'accès aux solutions tech pour les PME sénégalaises et accompagner leur transformation digitale",
            "target_audience": "PME et startups au Sénégal, entrepreneurs 25-45 ans, secteurs tertiaire et services",
            "differentiation": "Support client bilingue (français/wolof), intégration paiement mobile (Orange Money, Wave), accompagnement personnalisé avec formateurs locaux",
            "value_proposition": "Solutions technologiques abordables et adaptées au contexte africain avec support multilingue et paiement mobile",
            "sector": "Technology / SaaS",
            "location": {
                "city": "Dakar",
                "country": "Sénégal",
                "region": "Afrique de l'Ouest"
            }
        }
    },
    {
        "name": "Brief 2 - Restaurant Wolof",
        "data": {
            "business_name": "Thieboudienne Royal",
            "vision": "Faire rayonner la cuisine sénégalaise authentique dans toute l'Afrique de l'Ouest",
            "mission": "Offrir une expérience culinaire traditionnelle de qualité dans un cadre moderne et convivial",
            "target_audience": "Familles sénégalaises, expatriés, touristes, 18-60 ans, classe moyenne à aisée",
            "differentiation": "Recettes familiales transmises de génération en génération, ingrédients locaux bio, ambiance culturelle authentique avec musique mbalax",
            "value_proposition": "Cuisine sénégalaise authentique avec service rapide et prix accessibles",
            "sector": "Food & Beverage / Restaurant",
            "location": {
                "city": "Dakar",
                "country": "Sénégal",
                "region": "Plateau"
            }
        }
    },
    {
        "name": "Brief 3 - E-commerce Mode Africaine",
        "data": {
            "business_name": "Wax Fashion Market",
            "vision": "Devenir la marketplace #1 de la mode africaine contemporaine en ligne",
            "mission": "Connecter créateurs africains et clients du monde entier via une plateforme e-commerce moderne",
            "target_audience": "Femmes 20-40 ans, diaspora africaine, passionnés de mode africaine, revenus moyens-élevés",
            "differentiation": "Vérification authenticité tissus wax, livraison internationale express, service personnalisation sur-mesure, paiement mobile intégré",
            "value_proposition": "Mode africaine authentique livrée partout dans le monde avec garantie qualité",
            "sector": "Retail / E-commerce Fashion",
            "location": {
                "city": "Abidjan",
                "country": "Côte d'Ivoire",
                "region": "Afrique de l'Ouest"
            }
        }
    },
    {
        "name": "Brief 4 - Consulting RH",
        "data": {
            "business_name": "AfriTalent Solutions",
            "vision": "Transformer le recrutement en Afrique grâce à l'IA et l'expertise locale",
            "mission": "Accompagner les entreprises africaines dans leur développement RH avec des solutions innovantes",
            "target_audience": "PME et grandes entreprises en Afrique francophone, DRH, responsables recrutement",
            "differentiation": "Connaissance approfondie marché africain, base de données talents qualifiés, IA pour matching compétences, accompagnement formation",
            "value_proposition": "Recrutement efficace et formations adaptées au contexte africain",
            "sector": "Professional Services / HR Consulting",
            "location": {
                "city": "Douala",
                "country": "Cameroun",
                "region": "Afrique Centrale"
            }
        }
    },
    {
        "name": "Brief 5 - Formation en Ligne",
        "data": {
            "business_name": "AfricaLearn Academy",
            "vision": "Démocratiser l'éducation de qualité accessible à tous les africains",
            "mission": "Proposer des formations professionnelles certifiantes en ligne adaptées au marché africain",
            "target_audience": "Étudiants et jeunes professionnels africains 18-35 ans, chercheurs d'emploi, reconversion professionnelle",
            "differentiation": "Contenus en français et langues locales, certificats reconnus internationalement, tarifs adaptés économie africaine, mentorat personnalisé",
            "value_proposition": "Formations professionnelles de qualité accessibles partout en Afrique",
            "sector": "Education / EdTech",
            "location": {
                "city": "Lomé",
                "country": "Togo",
                "region": "Afrique de l'Ouest"
            }
        }
    }
]


async def test_brief_generation(brief_config: dict, index: int):
    """Tester la génération d'un business brief"""
    
    print(f"\n{'='*80}")
    print(f"TEST {index}/5 : {brief_config['name']}")
    print(f"{'='*80}")
    
    # Start timer BEFORE try block
    start_time = time.time()
    
    try:
        # Initialize services
        orchestrator = LangGraphOrchestrator()
        redis_fs = RedisVirtualFileSystem()
        
        print(f"⏱️  Démarrage génération...")
        print(f"   Secteur: {brief_config['data']['sector']}")
        print(f"   Localisation: {brief_config['data']['location']['city']}, {brief_config['data']['location']['country']}")
        
        # Run orchestration
        final_state = await orchestrator.run({"business_brief": brief_config['data']})
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Prepare results
        brief_id = f"test_brief_{index}_{int(time.time())}"
        user_id = 999  # Test user
        
        results = {
            "brief_id": brief_id,
            "user_id": user_id,
            "test_name": brief_config['name'],
            "results": final_state,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save to Redis
        await redis_fs.write_session(user_id, brief_id, results)
        
        # Analyze results
        print(f"\n✅ GÉNÉRATION RÉUSSIE")
        print(f"   Durée: {duration:.2f}s")
        print(f"   Brief ID: {brief_id}")
        
        # Check research results
        if "research" in final_state:
            research = final_state["research"]
            print(f"\n📊 RESEARCH:")
            if isinstance(research, dict):
                if "market_insights" in research:
                    insights = research["market_insights"][:200] if len(research.get("market_insights", "")) > 200 else research.get("market_insights", "N/A")
                    print(f"   Market insights: {insights}...")
                if "competitors" in research:
                    competitors_count = len(research.get("competitors", []))
                    print(f"   Competitors found: {competitors_count}")
                if "opportunities" in research:
                    opps_count = len(research.get("opportunities", []))
                    print(f"   Opportunities found: {opps_count}")
        
        # Check content results
        if "content" in final_state:
            content = final_state["content"]
            print(f"\n📝 CONTENT:")
            if isinstance(content, dict):
                if "homepage" in content:
                    homepage = content["homepage"]
                    if isinstance(homepage, dict):
                        langs = list(homepage.keys())
                        print(f"   Langues générées: {', '.join(langs)}")
                        if "fr" in homepage:
                            fr_preview = homepage["fr"][:150] if len(homepage["fr"]) > 150 else homepage["fr"]
                            print(f"   Preview FR: {fr_preview}...")
        
        # Check logo
        if "logo" in final_state:
            logo = final_state["logo"]
            print(f"\n🎨 LOGO:")
            if isinstance(logo, dict) and "url" in logo:
                print(f"   URL: {logo.get('url', 'N/A')}")
                print(f"   Style: {logo.get('style', 'N/A')}")
        
        # Validation criteria
        validations = {
            "Durée < 40s": duration < 40,
            "Research présent": "research" in final_state,
            "Content présent": "content" in final_state,
            "Brief ID généré": brief_id is not None,
            "Redis persisté": True  # Si on arrive ici, c'est OK
        }
        
        print(f"\n✔️  VALIDATIONS:")
        for criterion, passed in validations.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        all_passed = all(validations.values())
        
        return {
            "success": True,
            "brief_id": brief_id,
            "duration": duration,
            "validations": validations,
            "all_validations_passed": all_passed,
            "error": None
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ ÉCHEC GÉNÉRATION")
        print(f"   Erreur: {str(e)}")
        print(f"   Durée avant échec: {duration:.2f}s")
        
        return {
            "success": False,
            "brief_id": None,
            "duration": duration,
            "validations": {},
            "all_validations_passed": False,
            "error": str(e)
        }


async def main():
    """Execute all E2E tests"""
    
    print("\n" + "="*80)
    print(" TESTS MANUELS E2E - PHASE 1 SPRINT 3")
    print(" Genesis AI - Business Brief Generation")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Nombre de tests: {len(TEST_BRIEFS)}")
    
    results = []
    
    # Run all tests
    for i, brief_config in enumerate(TEST_BRIEFS, start=1):
        result = await test_brief_generation(brief_config, i)
        results.append({
            "test_name": brief_config['name'],
            **result
        })
        
        # Pause entre tests
        if i < len(TEST_BRIEFS):
            print(f"\n⏸️  Pause 2s avant test suivant...")
            await asyncio.sleep(2)
    
    # Summary
    print(f"\n\n{'='*80}")
    print(" RÉSUMÉ TESTS E2E")
    print(f"{'='*80}\n")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - successful_tests
    
    all_validations_passed = sum(1 for r in results if r.get("all_validations_passed", False))
    
    total_duration = sum(r["duration"] for r in results)
    avg_duration = total_duration / total_tests if total_tests > 0 else 0
    
    print(f"Tests exécutés: {total_tests}")
    print(f"Succès: {successful_tests} ✅")
    print(f"Échecs: {failed_tests} ❌")
    print(f"Validations complètes: {all_validations_passed}/{total_tests}")
    print(f"\nDurée totale: {total_duration:.2f}s")
    print(f"Durée moyenne: {avg_duration:.2f}s")
    
    # Detailed results
    print(f"\n{'='*80}")
    print(" DÉTAILS PAR TEST")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, start=1):
        status = "✅ SUCCÈS" if result["success"] else "❌ ÉCHEC"
        print(f"{i}. {result['test_name']}: {status}")
        print(f"   Durée: {result['duration']:.2f}s")
        if result["success"]:
            print(f"   Brief ID: {result['brief_id']}")
            validations_ok = sum(1 for v in result['validations'].values() if v)
            validations_total = len(result['validations'])
            print(f"   Validations: {validations_ok}/{validations_total}")
        else:
            print(f"   Erreur: {result['error']}")
        print()
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "test_results_e2e.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "all_validations_passed": all_validations_passed,
                "total_duration_seconds": round(total_duration, 2),
                "average_duration_seconds": round(avg_duration, 2)
            },
            "tests": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"{'='*80}")
    print(f"📄 Résultats sauvegardés: {results_file}")
    print(f"{'='*80}\n")
    
    # Exit code
    exit_code = 0 if failed_tests == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
