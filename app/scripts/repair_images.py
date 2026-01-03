import asyncio
import json
import structlog
from app.core.agents.image import ImageAgent
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.services.transformer import BriefToSiteTransformer
from app.models.coaching import BusinessBrief

# Configure logging
logging = structlog.get_logger()

SESSION_ID = "9dbd044e-d23c-4c0f-ad89-8f323077bc25"

async def repair_images():
    print(f"Starting image repair for session {SESSION_ID}...")
    
    redis_fs = RedisVirtualFileSystem()
    image_agent = ImageAgent()
    transformer = BriefToSiteTransformer()
    
    # 1. Récupérer la session (Business Brief)
    # Note: Dans Redis, la clé est session:{id} ou genesis:session:{user_id}:{brief_id}
    
    redis = redis_fs.redis
    session_json = await redis.get(f"session:{SESSION_ID}")
    
    business_name = "Chez Tante Awa"
    sector = "Restaurant Sénégalais"
    
    if session_json:
        session_data = json.loads(session_json)
        print("Session data loaded.")
        business_name = session_data.get("onboarding", {}).get("business_name", business_name)
        sector = session_data.get("onboarding", {}).get("sector", sector)
    else:
        print("Session not found in Redis. Using defaults for repair.")
        # On continue avec les valeurs par défaut
    
    # Simuler des services/features si pas dans le brief brut (car on a fait un `complete_coaching_premium` simplifié)
    services = ["Le Thiéboudienne de Tante Awa", "Le Yassa Poulet Fondant", "Le Mafé Généreux", "Jus de Bissap Maison"]
    features = ["Cuisine Authentique", "Produits Frais Locaux", "Ambiance Familiale"]
    
    print(f"Regenerating images for {business_name} ({sector})...")
    print("This will download images locally to /app/app/static/images/")
    
    # 2. Regénérer les images (force no cache pour être sûr d'avoir les versions locales)
    # On modifie temporairement ImageAgent pour forcer le téléchargement si nécessaire, 
    # mais run() le fait déjà si on lui demande.
    # Ici on va appeler generate_all_site_images.
    
    # Important: On doit s'assurer que le cache Redis de l'ImageAgent ne nous renvoie pas les vieilles URLs expirées.
    # L'astuce est de passer un context légèrement différent ou de clear le cache, 
    # mais le plus simple est de modifier le cache_key ou d'ignorer le cache.
    # Malheureusement generate_all_site_images n'a pas de param use_cache.
    # On va supposer que les nouvelles clés (avec paths locaux) ne sont pas en cache.
    # Si elles le sont (car run() appelé avant sans download), c'est problématique.
    # => On va flusher le cache d'images pour ce business avant.
    
    # Clean cache (manuel, un peu bourrin mais efficace pour repair)
    # On ne peut pas facilement deviner les clés de cache exactes ici sans refaire la logique.
    # On va faire confiance à la modif de code: si le cache renvoie une URL distante, on pourrait la retélécharger.
    # MAIS ImageAgent.run() retourne le cache direct.
    # FIX: On va supprimer manuellement les clés de cache potentielles si on peut, 
    # OU on compte sur le fait que j'ai ajouté la persistance locale MAINTENANT, donc les appels précédents
    # n'avaient pas "local_persistence": True dans les métadonnées.
    
    # Hack: On va appeler run() avec use_cache=False pour être sûr.
    # Ah zut, generate_all_site_images ne propage pas use_cache=False dans l'implémentation actuelle.
    # Je vais modifier ImageAgent.run pour qu'il checke si l'image est locale.
    # Pour l'instant, je vais patcher ImageAgent ici ou juste appeler run() manuellement en boucle.
    
    images_result = {}
    
    # Hero
    print("Generating Hero...")
    hero_res = await image_agent.run(business_name, sector, "hero", use_cache=False)
    images_result["hero_image"] = hero_res["image_url"]
    
    # Services
    print("Generating Services...")
    svc_images = []
    for svc in services:
        res = await image_agent.run(business_name, sector, "service", context=svc, use_cache=False)
        svc_images.append(res["image_url"])
    images_result["service_images"] = svc_images
    
    # Features
    print("Generating Features...")
    feat_images = []
    for feat in features:
        res = await image_agent.run(business_name, sector, "feature", context=feat, use_cache=False)
        feat_images.append(res["image_url"])
    images_result["feature_images"] = feat_images
    
    print("Images generated:")
    print(json.dumps(images_result, indent=2))
    
    # 3. Mettre à jour le Site Definition dans Redis
    # On doit charger le SiteDefinition actuel, updater les images, et resauvegarder.
    
    site_key = f"site:{SESSION_ID}"
    site_json = await redis.get(site_key)
    
    if site_json:
        site_def = json.loads(site_json)
        
        # Update Hero
        if "pages" in site_def:
            for page in site_def["pages"]:
                if page["id"] == "home":
                    for section in page["sections"]:
                        if section["type"] == "hero":
                            section["content"]["image"] = images_result["hero_image"]
                        
                        if section["type"] == "services":
                            for idx, svc_item in enumerate(section["content"].get("services", [])):
                                if idx < len(images_result["service_images"]):
                                    svc_item["image"] = images_result["service_images"][idx]
                                    
                        if section["type"] == "features":
                            for idx, feat_item in enumerate(section["content"].get("features", [])):
                                if idx < len(images_result["feature_images"]):
                                    feat_item["image"] = images_result["feature_images"][idx]
                                    
        # Update Metadata OG Image
        site_def["metadata"]["ogImage"] = images_result["hero_image"]
        
        # Save back
        await redis.set(site_key, json.dumps(site_def))
        print("Site definition updated in Redis.")
        
    else:
        print("Error: Site definition not found in Redis to update.")

if __name__ == "__main__":
    asyncio.run(repair_images())
