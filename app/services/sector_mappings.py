"""Mappings sectoriels pour personnaliser les sites par industrie

Ce module fournit des configurations par défaut selon le secteur d'activité
de l'entreprise, permettant de personnaliser les couleurs, icônes et 
structure des sections du site.
"""

from typing import Dict, Any, List


SECTOR_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "technology": {
        "default_colors": {
            "primary": "#3B82F6",    # Blue
            "secondary": "#8B5CF6",  # Purple
        },
        "default_icons": ["code", "server", "cloud", "cpu", "database", "terminal"],
        "section_order": ["hero", "features", "services", "about", "contact", "footer"],
        "cta_text": "Démarrer votre projet",
        "about_title": "Innovation & Excellence",
    },
    "restaurant": {
        "default_colors": {
            "primary": "#D97706",    # Amber-600 (Gold/Terracotta)
            "secondary": "#1F2937",  # Gray-800
            "accent": "#F59E0B"      # Gold
        },
        "default_icons": ["utensils", "coffee", "wine", "cake", "pizza", "salad"],
        "section_order": ["hero", "about", "menu", "features", "testimonials", "contact", "footer"],
        "cta_text": "Réserver une table",
        "about_title": "Notre Histoire",
        "theme_variant": "restaurant"
    },
    "health": {
        "default_colors": {
            "primary": "#10B981",    # Emerald
            "secondary": "#06B6D4",  # Cyan
        },
        "default_icons": ["heart", "stethoscope", "activity", "shield", "user-check", "clipboard"],
        "section_order": ["hero", "about", "services", "features", "contact", "footer"],
        # testimonials → Phase 2
        "cta_text": "Prendre rendez-vous",
        "about_title": "Votre Santé, Notre Priorité",
    },
    "education": {
        "default_colors": {
            "primary": "#6366F1",    # Indigo
            "secondary": "#EC4899",  # Pink
        },
        "default_icons": ["book", "graduation-cap", "pencil", "lightbulb", "users", "award"],
        "section_order": ["hero", "about", "services", "features", "contact", "footer"],
        "cta_text": "S'inscrire maintenant",
        "about_title": "Former les Leaders de Demain",
    },
    "ecommerce": {
        "default_colors": {
            "primary": "#F59E0B",    # Amber
            "secondary": "#10B981",  # Emerald
        },
        "default_icons": ["shopping-cart", "package", "truck", "credit-card", "tag", "percent"],
        "section_order": ["hero", "features", "services", "about", "contact", "footer"],
        "cta_text": "Découvrir nos produits",
        "about_title": "Qualité & Service",
    },
    "salon": {
        "default_colors": {
            "primary": "#EC4899",    # Pink
            "secondary": "#8B5CF6",  # Purple
        },
        "default_icons": ["scissors", "sparkles", "heart", "star", "droplet", "crown"],
        "section_order": ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
        "cta_text": "Prendre rendez-vous",
        "about_title": "Notre Savoir-Faire",
    },
    "artisanat": {
        "default_colors": {
            "primary": "#D97706",    # Amber
            "secondary": "#92400E",  # Brown
        },
        "default_icons": ["hammer", "palette", "gem", "hand", "brush", "scissors"],
        "section_order": ["hero", "about", "gallery", "services", "contact", "footer"],
        "cta_text": "Découvrir nos créations",
        "about_title": "L'Art de Nos Mains",
    },
    "transport": {
        "default_colors": {
            "primary": "#0891B2",    # Cyan
            "secondary": "#0D9488",  # Teal
        },
        "default_icons": ["truck", "map-pin", "clock", "package", "route", "navigation"],
        "section_order": ["hero", "services", "features", "about", "contact", "footer"],
        "cta_text": "Demander un devis",
        "about_title": "Votre Partenaire Mobilité",
    },
    "default": {
        "default_colors": {
            "primary": "#3B82F6",    # Blue
            "secondary": "#10B981",  # Emerald
        },
        "default_icons": ["star", "check", "zap", "award", "target", "trending-up"],
        "section_order": ["hero", "about", "services", "features", "contact", "footer"],
        "cta_text": "Nous contacter",
        "about_title": "À Propos de Nous",
    }
}


def get_sector_config(sector: str) -> Dict[str, Any]:
    """
    Retourne la configuration sectorielle ou celle par défaut.
    
    Args:
        sector: Nom du secteur d'activité (ex: "technology", "restaurant")
        
    Returns:
        Dictionnaire contenant les configurations du secteur
    """
    if not sector:
        return SECTOR_MAPPINGS["default"]
    
    s = sector.lower()
    # Gestion des alias courants (UI vs Backend)
    if "restaurant" in s or "alimentation" in s:
        return SECTOR_MAPPINGS["restaurant"]
    if "tech" in s or "digital" in s:
        return SECTOR_MAPPINGS["technology"]
    if "santé" in s or "bien-être" in s:
        return SECTOR_MAPPINGS["health"]
    if "coiffure" in s or "beauté" in s or "salon" in s:
        return SECTOR_MAPPINGS["salon"]
    if "commerce" in s or "boutique" in s:
        return SECTOR_MAPPINGS["ecommerce"]
    
    return SECTOR_MAPPINGS.get(s, SECTOR_MAPPINGS["default"])


def get_sector_colors(sector: str) -> Dict[str, str]:
    """
    Retourne les couleurs par défaut pour un secteur.
    
    Args:
        sector: Nom du secteur d'activité
        
    Returns:
        Dictionnaire des couleurs (primary, secondary)
    """
    config = get_sector_config(sector)
    return config.get("default_colors", SECTOR_MAPPINGS["default"]["default_colors"])


def get_sector_icons(sector: str) -> List[str]:
    """
    Retourne les icônes par défaut pour un secteur.
    
    Args:
        sector: Nom du secteur d'activité
        
    Returns:
        Liste des noms d'icônes
    """
    config = get_sector_config(sector)
    return config.get("default_icons", SECTOR_MAPPINGS["default"]["default_icons"])


def get_section_order(sector: str) -> List[str]:
    """
    Retourne l'ordre des sections pour un secteur.
    
    Args:
        sector: Nom du secteur d'activité
        
    Returns:
        Liste ordonnée des types de sections
    """
    config = get_sector_config(sector)
    return config.get("section_order", SECTOR_MAPPINGS["default"]["section_order"])
