"""
Seed script pour injecter les 5 thèmes fondateurs de Genesis AI.

Usage:
    docker exec genesis-api python -m app.scripts.seed_themes
    
    Ou en local:
    python -m app.scripts.seed_themes
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models.theme import Theme


# Les 5 thèmes fondateurs définis par le Tech Lead
SEED_THEMES = [
    {
        "name": "Nova",
        "slug": "nova",
        "description": "Design moderne et épuré pour startups tech et entreprises B2B innovantes. "
                       "Lignes nettes, espaces généreux et typographie contemporaine.",
        "category": "generic",
        "compatibility_tags": ["tech", "modern", "startup", "b2b", "saas", "innovation", "digital"],
        "features": {
            "primary_color": "#3B82F6",
            "secondary_color": "#1E40AF",
            "heading_font": "Inter",
            "body_font": "Inter",
            "style": "minimalist",
            "animations": True,
            "dark_mode_ready": True
        },
        "thumbnail_url": "https://placehold.co/600x400/3B82F6/FFFFFF?text=Nova",
        "preview_url": None,
        "is_active": True,
        "is_premium": False
    },
    {
        "name": "Savor",
        "slug": "savor",
        "description": "Thème chaleureux et appétissant pour restaurants, cafés et métiers de bouche. "
                       "Couleurs gourmandes et mise en valeur des visuels.",
        "category": "restaurant",
        "compatibility_tags": ["food", "restaurant", "warm", "visual", "cafe", "bakery", "catering", "bar"],
        "features": {
            "primary_color": "#E63946",
            "secondary_color": "#F4A261",
            "heading_font": "Playfair Display",
            "body_font": "Lato",
            "style": "warm",
            "animations": True,
            "menu_layout": "grid",
            "reservation_widget": True
        },
        "thumbnail_url": "https://placehold.co/600x400/E63946/FFFFFF?text=Savor",
        "preview_url": None,
        "is_active": True,
        "is_premium": False
    },
    {
        "name": "Luxe",
        "slug": "luxe",
        "description": "Élégance sobre et raffinée pour hôtellerie, beauté et marques premium. "
                       "Typographie sophistiquée et palette neutre haut de gamme.",
        "category": "luxury",
        "compatibility_tags": ["luxury", "hotel", "beauty", "elegance", "spa", "fashion", "jewelry", "real_estate"],
        "features": {
            "primary_color": "#111827",
            "secondary_color": "#D4AF37",
            "heading_font": "Cormorant Garamond",
            "body_font": "Montserrat",
            "style": "elegant",
            "animations": True,
            "dark_mode_ready": True,
            "gold_accents": True
        },
        "thumbnail_url": "https://placehold.co/600x400/111827/D4AF37?text=Luxe",
        "preview_url": None,
        "is_active": True,
        "is_premium": True
    },
    {
        "name": "Impact",
        "slug": "impact",
        "description": "Design engagé pour ONG, associations et projets écologiques. "
                       "Couleurs naturelles et message fort.",
        "category": "ngo",
        "compatibility_tags": ["nature", "ngo", "ecology", "authentic", "green", "sustainable", "charity", "community"],
        "features": {
            "primary_color": "#059669",
            "secondary_color": "#34D399",
            "heading_font": "Merriweather",
            "body_font": "Open Sans",
            "style": "organic",
            "animations": True,
            "donation_widget": True,
            "impact_counter": True
        },
        "thumbnail_url": "https://placehold.co/600x400/059669/FFFFFF?text=Impact",
        "preview_url": None,
        "is_active": True,
        "is_premium": False
    },
    {
        "name": "Craft",
        "slug": "craft",
        "description": "Thème créatif et artisanal pour artisans, créateurs et portfolios. "
                       "Mise en valeur du travail fait main et de l'authenticité.",
        "category": "artisan",
        "compatibility_tags": ["artisan", "creative", "handmade", "portfolio", "artist", "designer", "photographer", "craftsman"],
        "features": {
            "primary_color": "#78350F",
            "secondary_color": "#D97706",
            "heading_font": "Syne",
            "body_font": "Work Sans",
            "style": "creative",
            "animations": True,
            "gallery_layout": "masonry",
            "portfolio_mode": True
        },
        "thumbnail_url": "https://placehold.co/600x400/78350F/FFFFFF?text=Craft",
        "preview_url": None,
        "is_active": True,
        "is_premium": False
    }
]


async def seed_themes(session: AsyncSession) -> dict:
    """
    Insère les thèmes fondateurs en base.
    Utilise upsert: si le slug existe déjà, ignore (pas de doublons).
    
    Returns:
        dict avec stats: {"inserted": int, "skipped": int, "total": int}
    """
    stats = {"inserted": 0, "skipped": 0, "total": len(SEED_THEMES)}
    
    for theme_data in SEED_THEMES:
        # Vérifier si le thème existe déjà
        existing = await session.execute(
            select(Theme).where(Theme.slug == theme_data["slug"])
        )
        if existing.scalar_one_or_none():
            print(f"  ⏭️  Thème '{theme_data['name']}' existe déjà, ignoré.")
            stats["skipped"] += 1
            continue
        
        # Créer le nouveau thème
        theme = Theme(**theme_data)
        session.add(theme)
        print(f"  ✅ Thème '{theme_data['name']}' créé.")
        stats["inserted"] += 1
    
    await session.commit()
    return stats


async def main():
    """Point d'entrée principal du script de seed."""
    print("\n" + "="*60)
    print("🌱 GENESIS AI - Seed des Thèmes Fondateurs")
    print("="*60 + "\n")
    
    try:
        async with AsyncSessionLocal() as session:
            stats = await seed_themes(session)
        
        print("\n" + "-"*40)
        print(f"📊 Résultats:")
        print(f"   • Thèmes créés: {stats['inserted']}")
        print(f"   • Thèmes ignorés (déjà existants): {stats['skipped']}")
        print(f"   • Total traités: {stats['total']}")
        print("-"*40 + "\n")
        
        if stats["inserted"] > 0:
            print("✅ Seed terminé avec succès!\n")
        else:
            print("ℹ️  Aucun nouveau thème inséré (tous existent déjà).\n")
            
    except Exception as e:
        print(f"\n❌ Erreur lors du seed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
