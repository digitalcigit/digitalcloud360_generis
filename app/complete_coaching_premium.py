"""Script pour compléter rapidement le coaching premium et générer le site"""
import asyncio
import httpx
import json
import os

# Configuration pour exécution DANS le conteneur Docker (port 8000 interne)
# Si exécution depuis le host, utiliser 8002
BASE_URL = os.getenv("GENESIS_API_URL", "http://localhost:8000")
API_URL = f"{BASE_URL}/api/v1/coaching"
AUTH_URL = f"{BASE_URL}/api/v1/auth"

# Réponses prédéfinies pour chaque étape (en français pour correspondre au contexte)
RESPONSES = {
    "vision": "Devenir le restaurant de référence pour la cuisine africaine authentique et chaleureuse dans la ville, en célébrant les saveurs locales.",
    "mission": "Nous sublimons les recettes traditionnelles en les préparant maison avec des ingrédients frais et sourcés localement, pour vous offrir une expérience culinaire authentique dans une ambiance chaleureuse et familiale.",
    "clientele": "Notre clientèle cible inclut les familles locales, les professionnels du quartier en quête d'une pause déjeuner authentique, et les amateurs éclairés de gastronomie africaine.",
    "differentiation": "Notre excellence repose sur trois piliers : des recettes ancestrales transmises avec rigueur, une hospitalité authentique où chaque convive est accueilli comme un membre de la famille, et un engagement absolu envers la fraîcheur - nos épices sont broyées au mortier chaque matin.",
    "offre": "Découvrez notre offre culinaire complète : des menus déjeuner variés mettant à l'honneur des classiques africains comme le Tiep rouge, le Yassa et le Mafé, une carte du soir élaborée, et un service traiteur dédié pour sublimer vos événements familiaux. Pour couronner l'expérience, ne manquez pas nos spécialités maison, le jus de Bissap et le Dégué en dessert."
}

async def complete_coaching():
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Token pour dcitest@digital.ci
        print(f"Authenticating against {AUTH_URL}...")
        login_data = {"username": "dcitest@digital.ci", "password": "DiGiT@l2025"}
        
        try:
            login_resp = await client.post(
                f"{AUTH_URL}/token",
                data=login_data
            )
        except httpx.ConnectError:
            print(f"❌ Connection failed to {AUTH_URL}. Are you running this inside the container?")
            return
        
        if login_resp.status_code != 200:
            print("Login failed, attempting registration...")
            reg_resp = await client.post(
                f"{AUTH_URL}/register",
                json={
                    "email": "dcitest@digital.ci",
                    "password": "DiGiT@l2025",
                    "name": "Premium User"
                }
            )
            if reg_resp.status_code in [200, 201]:
                print("Registration successful, retrying login...")
                login_resp = await client.post(
                    f"{AUTH_URL}/token",
                    data=login_data
                )
            else:
                print(f"Registration failed: {reg_resp.text}")
                
        if login_resp.status_code != 200:
            print(f"Auth failed final: {login_resp.text}")
            return
            
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start a NEW session to ensure fresh state
        print("Starting new coaching session...")
        onboarding_payload = {
            "business_name": "Chez Tante Awa Premium",
            "sector": "restaurant",
            "logo_source": "later"
        }
        onboard_resp = await client.post(
            f"{API_URL}/onboarding",
            json=onboarding_payload,
            headers=headers
        )
        if onboard_resp.status_code not in [200, 201]:
            print(f"Onboarding failed: {onboard_resp.text}")
            return
            
        new_session_id = onboard_resp.json()["session_id"]
        print(f"=== RAPID COACHING COMPLETION PREMIUM ===")
        print(f"New Session: {new_session_id}")
        print()
        
        # Start the session
        await client.post(f"{API_URL}/start", json={"session_id": new_session_id}, headers=headers)
        
        for step_key, response in RESPONSES.items():
            print(f"Step {step_key}...")
            
            # Envoyer la réponse
            payload = {
                "session_id": new_session_id,
                "user_response": response
            }
            
            resp = await client.post(
                f"{API_URL}/step",
                json=payload,
                headers=headers
            )
            
            if resp.status_code != 200:
                print(f"Step {step_key} failed: {resp.text}")
                continue
                
            data = resp.json()
            current = data.get("current_step", "")
            is_complete = data.get("is_step_complete", False)
            
            print(f"   Response: current={current}, complete={is_complete}")
            
            # Si site généré (dernière étape)
            if data.get("site_data"):
                print()
                print("SITE GENERATED SUCCESSFULLY!")
                print(f"Preview URL: http://localhost:3002/preview/{new_session_id}")
                return data
        
        print()
        print(f"Coaching finished (Final check)")
        # Une dernière vérification pour le site
        site_resp = await client.get(f"{API_URL}/{new_session_id}/site", headers=headers)
        if site_resp.status_code == 200:
            print("Site data available!")
            print(f"Preview URL: http://localhost:3002/preview/{new_session_id}")
        else:
            print("Site data not yet available (background generation?)")
            
        return data

if __name__ == "__main__":
    try:
        asyncio.run(complete_coaching())
    except Exception as e:
        print(f"Error: {e}")
