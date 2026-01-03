"""Script pour compléter rapidement le coaching et générer le site"""
import asyncio
import httpx
import json

SESSION_ID = "16ba1224-f1d1-4d1e-9b1d-eae9982f7d4d"
API_URL = "http://localhost:8002/api/v1/coaching"

# Réponses prédéfinies pour chaque étape
RESPONSES = {
    "VISION": "Devenir LA référence de la cuisine africaine authentique à Abidjan, reconnu pour la qualité, l'authenticité et l'accueil chaleureux.",
    "MISSION": "Offrir une expérience culinaire africaine authentique avec des recettes familiales transmises de génération en génération, dans une ambiance chaleureuse comme à la maison.",
    "CLIENTELE": "Familles africaines et expatriés recherchant une cuisine authentique, professionnels pour déjeuners d'affaires, touristes découvrant la gastronomie locale.",
    "DIFFERENTIATION": "Recettes familiales uniques transmises depuis 3 générations, ingrédients frais du marché local chaque jour, ambiance familiale authentique avec décor traditionnel.",
    "OFFRE": "Restaurant sur place 50 couverts, service traiteur pour événements, livraison rapide dans Abidjan, plats à emporter, menu du jour et spécialités du weekend."
}

async def complete_coaching():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Token dev
        token_resp = await client.get("http://localhost:8002/api/v1/auth/dev-token")
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"=== COMPLETION RAPIDE COACHING ===")
        print(f"Session: {SESSION_ID}")
        print()
        
        for step, response in RESPONSES.items():
            print(f"📝 Étape {step}...")
            
            # Envoyer plusieurs fois si nécessaire (pour les follow-ups)
            for attempt in range(5):
                resp = await client.post(
                    f"{API_URL}/respond",
                    json={"session_id": SESSION_ID, "user_response": response},
                    headers=headers
                )
                data = resp.json()
                current = data.get("current_step", "")
                is_complete = data.get("is_step_complete", False)
                
                print(f"   Attempt {attempt+1}: current={current}, complete={is_complete}")
                
                if current != step or is_complete:
                    break
                    
                # Si pas complet, ajouter plus de détails
                response = response + " C'est mon engagement principal."
            
            # Vérifier si site généré
            if data.get("site_data"):
                print()
                print("🎉 SITE GÉNÉRÉ !")
                print(f"Preview URL: http://localhost:3002/preview/{SESSION_ID}")
                return data
        
        print()
        print(f"✅ Coaching terminé")
        print(f"Preview URL: http://localhost:3002/preview/{SESSION_ID}")
        return data

if __name__ == "__main__":
    result = asyncio.run(complete_coaching())
