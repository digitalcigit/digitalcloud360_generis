import asyncio
import httpx
import json
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY2MzM0ODAzfQ.Bi4YzlWTXPNkAnbRGQK25fWtzNRgAGu4Lp_xAwSQPNM"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

async def run_test():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("🚀 Starting Manual E2E Test for Sprint 3 (Backend Agents)...")

        # 1. Start Session
        print("\n1️⃣  Starting Coaching Session...")
        response = await client.post(f"{API_URL}/coaching/start", json={}, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to start session: {response.text}")
            return
        
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Session started: {session_id}")

        # 2. Simulate Steps with RICHER responses to pass validation
        steps = [
            ("Vision", "D'ici 5 ans, je veux créer la référence de l'alimentation saine à Dakar, avec une flotte de 50 livreurs électriques et un réseau de 20 producteurs locaux partenaires. Je veux impacter la santé de 10 000 Dakarois tout en soutenant l'économie locale durable."),
            ("Mission", "Notre mission est de démocratiser l'accès à une alimentation équilibrée au bureau, en valorisant les produits du terroir sénégalais et en réduisant l'empreinte carbone de la livraison urbaine grâce à notre logistique verte."),
            ("Clientèle", "Nous ciblons principalement les cadres sup et employés de bureau (25-45 ans) du quartier du Plateau et des Almadies. Ils sont soucieux de leur santé, manquent de temps pour cuisiner, et cherchent une alternative fiable aux fast-foods, avec un pouvoir d'achat moyen-supérieur."),
            ("Différenciation", "Contrairement aux autres livraisons, nous garantissons 0 plastique (emballages consignés), 100% produits locaux (pas d'import), et une livraison bas carbone. De plus, nos menus sont validés par des nutritionnistes locaux."),
            ("Offre", "Nous proposons un abonnement 'Semaine Vitalité' à 15.000 FCFA comprenant 5 déjeuners complets (entrée + plat + jus naturel) livrés chaque midi. Commande flexible via WhatsApp ou Web, paiement mobile (Wave/OM) et option végétarienne incluse.")
        ]

        for step_name, user_response in steps:
            print(f"\n2️⃣  Processing Step: {step_name}...")
            print(f"   Input: {user_response}")
            
            payload = {
                "session_id": session_id,
                "user_response": user_response
            }
            
            # Note: The API might take time for the last step as it triggers orchestration
            response = await client.post(f"{API_URL}/coaching/step", json=payload, headers=HEADERS)
            
            if response.status_code != 200:
                print(f"❌ Step {step_name} failed: {response.text}")
                return
            
            data = response.json()
            is_complete = data.get("is_step_complete", False)
            confidence = data.get("confidence_score", 0.0)
            coach_msg = data.get("coach_message", "")
            
            print(f"   Status: {'✅ COMPLETE' if is_complete else '⚠️ INCOMPLETE'}")
            print(f"   Confidence: {confidence}")
            print(f"   Coach says: {coach_msg}")

            if not is_complete:
                print(f"🛑 Stopping test because step {step_name} was not validated.")
                return

            print(f"✅ Step {step_name} validated.")
            
            if data.get("site_data"):
                print("\n🎉 SITE GENERATION TRIGGERED!")
                site_data = data["site_data"]
                verify_sprint3_features(site_data)
                return

        print("\n⚠️  Loop finished but no site_data received. Check logs.")

def verify_sprint3_features(site_data):
    print("\n🔍 Verifying Sprint 3 Features in Site Definition...")
    
    # Real SiteDefinition structure: metadata, theme, pages[]
    metadata = site_data.get("metadata", {})
    theme = site_data.get("theme", {})
    pages = site_data.get("pages", [])
    
    # 1. Check Pages and Sections
    print(f"\n   📄 Pages: {len(pages)}")
    if pages:
        sections = pages[0].get("sections", [])
        print(f"   📦 Sections in home page: {len(sections)}")
        section_types = [s.get("type") for s in sections]
        print(f"   🔹 Section types: {section_types}")
        
        # Check for hero section with potential logo
        hero_section = next((s for s in sections if s.get("type") == "hero"), None)
        if hero_section and hero_section.get("content", {}).get("image"):
            print(f"   ✅ Hero image found")
        
        # Check footer for logo
        footer_section = next((s for s in sections if s.get("type") == "footer"), None)
        if footer_section:
            footer_logo = footer_section.get("content", {}).get("logo")
            if footer_logo and "placehold" not in footer_logo.lower():
                print(f"   ✅ Logo URL (DALL-E): {footer_logo[:60]}...")
            elif footer_logo:
                print(f"   ⚠️  Logo is placeholder: {footer_logo}")
            else:
                print(f"   ❌ No logo found in footer")
    
    # 2. Check Metadata (SEO)
    print(f"\n   🔍 SEO Metadata:")
    print(f"   - Title: {metadata.get('title', 'N/A')}")
    print(f"   - Description: {metadata.get('description', 'N/A')[:60] if metadata.get('description') else 'N/A'}...")
    print(f"   - Favicon: {'✅ Present' if metadata.get('favicon') else '❌ Missing'}")
    
    # 3. Check Theme
    colors = theme.get("colors", {})
    print(f"\n   🎨 Theme Colors:")
    print(f"   - Primary: {colors.get('primary', 'N/A')}")
    print(f"   - Secondary: {colors.get('secondary', 'N/A')}")
    
    if metadata.get('title') and len(sections) > 0:
        print("\n   ✅ Site Definition looks good! Sprint 3 agents worked.")
    else:
        print("\n   ⚠️  Site Definition incomplete.")

if __name__ == "__main__":
    asyncio.run(run_test())
