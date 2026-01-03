"""Transformer service to convert BusinessBrief to SiteDefinition

Ce module transforme un BusinessBrief (généré par les sub-agents IA) en un
SiteDefinition JSON utilisable par le Block Renderer frontend.
"""

from typing import Dict, Any, List, Optional, Union
from app.models.coaching import BusinessBrief
from app.schemas.business_brief_data import BusinessBriefData
from app.schemas.site_definition import SiteDefinition
from app.services.sector_mappings import get_sector_config, get_sector_colors, get_sector_icons
import json


class BriefToSiteTransformer:
    """Transform a BusinessBrief into a SiteDefinition JSON structure"""
    
    def transform(self, brief: Union[BusinessBrief, BusinessBriefData], theme: Any = None) -> Dict[str, Any]:
        """
        Convert a BusinessBrief to a SiteDefinition.
        
        Args:
            brief: BusinessBrief model instance
            theme: Optional Theme model instance
            
        Returns:
            Dictionary matching SiteDefinition Pydantic schema
        """
        import structlog
        logger = structlog.get_logger()

        # Get sector configuration
        sector_name = brief.sector if brief.sector else "default"
        sector_config = get_sector_config(sector_name)
        
        logger.info("transformer_start", 
                    brief_sector=sector_name, 
                    resolved_config=sector_config,
                    theme_name=theme.name if theme else "None",
                    theme_features=theme.features if theme else {})

        # Extract theme colors
        theme_colors = self._extract_theme_colors(brief, sector_config, theme)
        logger.info("transformer_colors", colors=theme_colors)
        
        # Build the site definition
        site_dict = {
            "metadata": {
                "title": brief.business_name,
                "description": brief.mission[:160] if brief.mission else "",
                "favicon": self._extract_logo_url(brief),
                "ogImage": self._extract_hero_image(brief)
            },
            "theme": {
                "id": str(theme.id) if theme else "default",
                "slug": theme.slug if theme else "default",
                "name": theme.name if theme else "Default",
                "colors": theme_colors,
                "fonts": {
                    "heading": theme.heading_font if theme and hasattr(theme, 'heading_font') else "Inter",
                    "body": "Inter",
                    "accent": theme.features.get("accent_font") if theme and hasattr(theme, 'features') and isinstance(theme.features, dict) else None
                },
                "config": theme.features if theme else {}
            },
            "pages": [
                self._build_home_page(brief, sector_config)
            ]
        }
        
        # Validation Pydantic obligatoire avant return
        SiteDefinition(**site_dict)
        
        return site_dict
    
    def _extract_theme_colors(self, brief: BusinessBrief, sector_config: Dict, theme: Any = None) -> Dict[str, str]:
        """Extract theme colors from brief, theme or use sector defaults"""
        # Start with sector-based defaults
        sector_colors = sector_config.get("default_colors", {})
        
        # Priority 1: Theme colors from the selected Theme model (stored in features JSON)
        primary_color = None
        accent_color = None
        
        if theme and hasattr(theme, 'features') and isinstance(theme.features, dict):
            primary_color = theme.features.get('primary_color')
            accent_color = theme.features.get('accent_color')
        
        if not primary_color:
            primary_color = sector_colors.get("primary", "#3B82F6")
            
        if not accent_color:
            accent_color = sector_colors.get("accent") # May be None
        
        default_colors = {
            "primary": primary_color,
            "secondary": sector_colors.get("secondary", "#10B981"),
            "background": "#FFFFFF",
            "text": "#1F2937"
        }
        
        if accent_color:
            default_colors["accent"] = accent_color
        
        # Priority 2: Override with colors from content_generation if available
        if brief.content_generation and isinstance(brief.content_generation, dict):
            colors = brief.content_generation.get("theme_colors", {})
            if colors:
                return {**default_colors, **colors}
        
        return default_colors
    
    def _extract_logo_url(self, brief: BusinessBrief) -> Optional[str]:
        """Extract logo URL from logo_creation results"""
        if brief.logo_creation and isinstance(brief.logo_creation, dict):
            return brief.logo_creation.get("logo_url")
        return None
    
    def _extract_hero_image(self, brief: BusinessBrief) -> Optional[str]:
        """Extract hero image from content generation"""
        if brief.content_generation and isinstance(brief.content_generation, dict):
            return brief.content_generation.get("hero_image")
        return None
    
    def _build_home_page(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, Any]:
        """Build the home page structure based on sector configuration"""
        sections = []
        section_order = sector_config.get("section_order", [
            "hero", "about", "services", "features", "contact", "footer"
        ])
        
        # Build sections in sector-specific order
        section_builders = {
            "hero": lambda: self._map_hero_section(brief, sector_config),
            "about": lambda: self._map_about_section(brief, sector_config),
            "services": lambda: self._map_services_section(brief, sector_config),
            "menu": lambda: self._map_menu_section(brief, sector_config),
            "features": lambda: self._map_features_section(brief, sector_config),
            "contact": lambda: self._map_contact_section(brief),
            "footer": lambda: self._map_footer_section(brief, sector_config),
        }
        
        for section_type in section_order:
            if section_type in section_builders:
                section = section_builders[section_type]()
                if section:
                    sections.append(section)
        
        return {
            "id": "home",
            "slug": "/",
            "title": "Accueil",
            "sections": sections
        }
    
    def _map_hero_section(self, brief: Union[BusinessBrief, BusinessBriefData], sector_config: Dict) -> Dict[str, Any]:
        """Génère la section Hero en utilisant le contenu LLM généré s'il existe"""
        
        # Determine variant based on sector config
        variant = "standard"
        if sector_config.get("theme_variant") == "restaurant":
            variant = "split"  # Default to split for restaurants for now

        # Extract hero image with fallback for restaurants
        hero_image = self._extract_hero_image(brief)
        if not hero_image and sector_config.get("theme_variant") == "restaurant":
            hero_image = "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80"

        # PRIORITÉ 1: Contenu généré par ContentSubAgent
        if brief.content_generation and isinstance(brief.content_generation, dict):
            homepage = brief.content_generation.get("homepage", {})
            hero = homepage.get("hero_section", {})
            
            if hero and isinstance(hero, dict):
                return {
                    "id": "hero",
                    "type": "hero",
                    "content": {
                        "title": hero.get("title") or brief.value_proposition or brief.business_name,
                        "subtitle": hero.get("subtitle") or (brief.mission[:120] if brief.mission else ""),
                        "description": hero.get("hero_paragraph") or (brief.differentiation[:200] if brief.differentiation else None),
                        "image": hero_image,
                        "cta": {
                            "text": hero.get("primary_cta") or sector_config.get("cta_text", "Nous contacter"),
                            "link": "#contact",
                            "variant": "primary"
                        },
                        "alignment": "center",
                        "overlay": False,
                        "variant": variant
                    }
                }
        
        # FALLBACK: Valeurs brutes du brief
        cta_text = sector_config.get("cta_text", "Nous contacter")
        return {
            "id": "hero",
            "type": "hero",
            "content": {
                "title": brief.value_proposition or brief.business_name,
                "subtitle": (brief.mission[:120] if brief.mission else ""),
                "description": (brief.differentiation[:200] if brief.differentiation else None),
                "image": hero_image,
                "cta": {
                    "text": cta_text,
                    "link": "#contact",
                    "variant": "primary"
                },
                "alignment": "center",
                "overlay": False,
                "variant": variant
            }
        }
    
    def _map_menu_section(self, brief: Union[BusinessBrief, BusinessBriefData], sector_config: Dict) -> Optional[Dict[str, Any]]:
        """Génère la section Menu (Savor V2)"""
        categories = []
        
        # PRIORITÉ 1: Menu structuré généré par l'IA
        if brief.content_generation and isinstance(brief.content_generation, dict):
            gen_menu = brief.content_generation.get("menu")
            if gen_menu and isinstance(gen_menu, list):
                categories = gen_menu # On suppose que la structure est déjà correcte

        # PRIORITÉ 2: Fallback sur les services -> Menu
        if not categories:
            menu_items = []
            services = []
            
            # Récupération des services (depuis le brief ou la génération)
            if hasattr(brief, 'services') and brief.services:
                services = list(brief.services)
            elif brief.content_generation and isinstance(brief.content_generation, dict):
                 raw_services = brief.content_generation.get("services", [])
                 if isinstance(raw_services, list):
                     services = raw_services

            # FALLBACK ULTIME: Services par défaut si vide (pour restaurants)
            if not services and sector_config.get("theme_variant") == "restaurant":
                services = ["Entrées Gourmandes", "Plats Signature", "Desserts Maison", "Sélection de Vins"]

            for i, s in enumerate(services[:8]): # Limite à 8 items
                is_highlight = i < 2 # Highlight first two items by default
                if isinstance(s, str):
                    menu_items.append({
                        "title": s,
                        "description": f"Délicieux {s.lower()} préparé avec soin.",
                        "price": "15-25", # Placeholder
                        "dietary": [],
                        "isHighlight": is_highlight
                    })
                elif isinstance(s, dict):
                    menu_items.append({
                        "title": s.get("title", f"Plat {i+1}"),
                        "description": s.get("description", ""),
                        "price": s.get("price", "20"),
                        "image": s.get("image"),
                        "dietary": s.get("dietary", []),
                        "isHighlight": s.get("is_highlight") or s.get("isHighlight") or is_highlight
                    })
            
            if menu_items:
                categories.append({
                    "id": "carte",
                    "title": "La Carte",
                    "items": menu_items
                })

        if not categories:
            return None

        return {
            "id": "menu",
            "type": "menu",
            "content": {
                "title": "Notre Carte",
                "subtitle": "Une expérience culinaire unique",
                "categories": categories,
                "currency": "€"
            }
        }

    def _map_about_section(self, brief: Union[BusinessBrief, BusinessBriefData], sector_config: Dict) -> Dict[str, Any]:
        """Génère la section À propos"""
        about_title = sector_config.get("about_title", "À Propos de Nous")
        
        # Determine variant
        variant = "simple"
        if sector_config.get("theme_variant") == "restaurant":
            variant = "enhanced"
        
        # Extract stats if available
        stats = None
        if brief.content_generation and isinstance(brief.content_generation, dict):
            raw_stats = brief.content_generation.get("stats", [])
            if raw_stats:
                stats = [{"value": s.get("value", ""), "label": s.get("label", "")} 
                        for s in raw_stats[:4]]  # Max 4 stats
        
        # FALLBACK STATS for enhanced variant (Savor V2)
        if variant == "enhanced" and not stats:
            stats = [
                {"value": "15+", "label": "Ans d'Excellence"},
                {"value": "100%", "label": "Produits Frais"},
                {"value": "24/7", "label": "Passion Culinaire"}
            ]

        # Extract about image
        about_image = None
        if brief.content_generation and isinstance(brief.content_generation, dict):
            about_image = brief.content_generation.get("about_image")
        
        # Fallback image
        if not about_image:
            about_image = "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=800&q=80"

        return {
            "id": "about",
            "type": "about",
            "content": {
                "title": about_title,
                "subtitle": brief.business_name,
                "description": brief.mission or "Une expérience culinaire inoubliable au service du goût.",
                "mission": brief.mission,
                "vision": brief.vision,
                "image": about_image,
                "stats": stats,
                "variant": variant
            }
        }
    
    def _map_services_section(self, brief: BusinessBrief, sector_config: Dict) -> Optional[Dict[str, Any]]:
        """Génère la section Services"""
        services = []
        default_icons = sector_config.get("default_icons", ["star", "check", "zap"])
        
        # Extract services from brief.services or content_generation
        raw_services = []
        if brief.services:
            # Services can be a list of strings or dicts - convert to list explicitly
            raw_services = list(brief.services) if brief.services else []
        
        if brief.content_generation and isinstance(brief.content_generation, dict):
            gen_services = brief.content_generation.get("services", [])
            if gen_services and isinstance(gen_services, list):
                raw_services = gen_services
        
        if not raw_services:
            return None
        
        # Ensure raw_services is a list before slicing
        services_to_process = list(raw_services)[:6] if raw_services else []
        
        for i, service in enumerate(services_to_process):  # Max 6 services
            if isinstance(service, str):
                # Simple string service
                services.append({
                    "id": f"service-{i+1}",
                    "title": service,
                    "description": f"Découvrez notre service {service}",
                    "icon": default_icons[i % len(default_icons)]
                })
            elif isinstance(service, dict):
                # Detailed service dict
                services.append({
                    "id": f"service-{i+1}",
                    "title": service.get("title", f"Service {i+1}"),
                    "description": service.get("description", ""),
                    "icon": service.get("icon", default_icons[i % len(default_icons)]),
                    "price": service.get("price"),
                    "image": service.get("image"),
                    "href": service.get("href")
                })
        
        if not services:
            return None
        
        return {
            "id": "services",
            "type": "services",
            "content": {
                "title": "Nos Services",
                "subtitle": "Ce que nous offrons",
                "services": services,
                "layout": "grid"
            }
        }
    
    def _map_features_section(self, brief: BusinessBrief, sector_config: Dict) -> Optional[Dict[str, Any]]:
        """Génère la section Features/Avantages"""
        features = []
        default_icons = sector_config.get("default_icons", ["star", "check", "zap"])
        
        # Try to get from content_generation first
        if brief.content_generation and isinstance(brief.content_generation, dict):
            gen_features = brief.content_generation.get("features", [])
            if gen_features:
                for i, f in enumerate(gen_features[:6]):
                    if isinstance(f, dict):
                        features.append({
                            "id": f"feature-{i+1}",
                            "title": f.get("title", f"Avantage {i+1}"),
                            "description": f.get("description", ""),
                            "icon": f.get("icon", default_icons[i % len(default_icons)]),
                            "image": f.get("image")
                        })
        
        # Fallback: create features from differentiation
        if not features and brief.differentiation:
            points = [p.strip() for p in brief.differentiation.split('.') if p.strip()][:4]
            for i, point in enumerate(points):
                features.append({
                    "id": f"feature-{i+1}",
                    "title": f"Avantage {i+1}",
                    "description": point,
                    "icon": default_icons[i % len(default_icons)]
                })
        
        if not features:
            return None
        
        return {
            "id": "features",
            "type": "features",
            "content": {
                "title": "Pourquoi Nous Choisir",
                "subtitle": "Nos points forts",
                "features": features,
                "layout": "grid"
            }
        }
    
    def _map_contact_section(self, brief: BusinessBrief) -> Dict[str, Any]:
        """Génère la section Contact"""
        # Extract contact info from content_generation
        email = None
        phone = None
        address = None
        social_links = None
        
        if brief.content_generation and isinstance(brief.content_generation, dict):
            email = brief.content_generation.get("email")
            phone = brief.content_generation.get("phone")
            
            # Address
            addr = brief.content_generation.get("address")
            if addr and isinstance(addr, dict):
                address = {
                    "street": addr.get("street", ""),
                    "city": addr.get("city", ""),
                    "country": addr.get("country", ""),
                    "postalCode": addr.get("postalCode")
                }
            
            # Social links
            socials = brief.content_generation.get("social_links", [])
            if socials:
                social_links = [
                    {"platform": s.get("platform"), "url": s.get("url")}
                    for s in socials if s.get("platform") and s.get("url")
                ]
        
        return {
            "id": "contact",
            "type": "contact",
            "content": {
                "title": "Contactez-nous",
                "subtitle": "Nous sommes à votre écoute",
                "description": f"N'hésitez pas à nous contacter pour discuter de votre projet avec {brief.business_name}.",
                "email": email,
                "phone": phone,
                "address": address,
                "socialLinks": social_links if social_links else None,
                "showForm": True,
                "formFields": [
                    {"name": "name", "type": "text", "label": "Nom", "required": True},
                    {"name": "email", "type": "email", "label": "Email", "required": True},
                    {"name": "phone", "type": "tel", "label": "Téléphone", "required": False},
                    {"name": "message", "type": "textarea", "label": "Message", "required": True}
                ]
            }
        }
    
    def _map_footer_section(self, brief: BusinessBrief, sector_config: Dict = None) -> Dict[str, Any]:
        """Génère la section Footer"""
        logo_url = self._extract_logo_url(brief)
        
        # Determine variant
        variant = "simple"
        if sector_config and sector_config.get("theme_variant") == "restaurant":
            variant = "restaurant"

        # Extract social links for footer
        social_links = None
        email = None
        phone = None
        address_str = None

        if brief.content_generation and isinstance(brief.content_generation, dict):
            socials = brief.content_generation.get("social_links", [])
            if socials:
                social_links = [
                    {"platform": s.get("platform"), "url": s.get("url")}
                    for s in socials if s.get("platform") and s.get("url")
                ]
            
            email = brief.content_generation.get("email")
            phone = brief.content_generation.get("phone")
            addr = brief.content_generation.get("address")
            if addr and isinstance(addr, dict):
                street = addr.get("street", "")
                city = addr.get("city", "")
                address_str = f"{street}, {city}" if street and city else city or street

        # Year dynamique
        from datetime import datetime
        current_year = datetime.now().year
        
        content = {
            "logo": logo_url,
            "companyName": brief.business_name,
            "description": brief.mission[:100] if brief.mission else None,
            "copyright": f"© {current_year} {brief.business_name}. Tous droits réservés.",
            "links": [
                {"text": "Accueil", "url": "#hero"},
                {"text": "À propos", "url": "#about"},
                {"text": "Services", "url": "#services"},
                {"text": "Contact", "url": "#contact"}
            ],
            "socialLinks": social_links,
            "variant": variant
        }

        # Add V2 Restaurant specific fields
        if variant == "restaurant":
            content["openingHours"] = [
                {"days": "Lundi - Vendredi", "hours": "12:00 - 14:30 | 19:00 - 22:30"},
                {"days": "Samedi", "hours": "19:00 - 23:00"},
                {"days": "Dimanche", "hours": "Fermé"}
            ]
            content["newsletter"] = {
                "title": "Newsletter",
                "description": "Inscrivez-vous pour recevoir nos actualités et offres spéciales.",
                "placeholder": "Votre email",
                "buttonText": "S'inscrire"
            }
            content["contactInfo"] = {
                "email": email or "contact@example.com",
                "phone": phone or "+33 1 23 45 67 89",
                "address": address_str or "Paris, France"
            }

        return {
            "id": "footer",
            "type": "footer",
            "content": content
        }
