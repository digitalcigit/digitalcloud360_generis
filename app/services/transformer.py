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
    
    def transform(self, brief: Union[BusinessBrief, BusinessBriefData]) -> Dict[str, Any]:
        """
        Convert a BusinessBrief to a SiteDefinition.
        
        Args:
            brief: BusinessBrief model instance
            
        Returns:
            Dictionary matching SiteDefinition Pydantic schema
            
        Raises:
            ValidationError: Si le JSON généré ne respecte pas le schema
        """
        # Get sector configuration
        sector_config = get_sector_config(brief.sector if brief.sector else "default")
        
        # Extract theme colors from content generation or use sector defaults
        theme_colors = self._extract_theme_colors(brief, sector_config)
        
        # Build the site definition
        site_dict = {
            "metadata": {
                "title": brief.business_name,
                "description": brief.mission[:160] if brief.mission else "",
                "favicon": self._extract_logo_url(brief),
                "ogImage": self._extract_hero_image(brief)
            },
            "theme": {
                "colors": theme_colors,
                "fonts": {
                    "heading": "Inter",
                    "body": "Inter"
                }
            },
            "pages": [
                self._build_home_page(brief, sector_config)
            ]
        }
        
        # Validation Pydantic obligatoire avant return
        SiteDefinition(**site_dict)
        
        return site_dict
    
    def _extract_theme_colors(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, str]:
        """Extract theme colors from brief or use sector defaults"""
        # Start with sector-based defaults
        sector_colors = sector_config.get("default_colors", {})
        default_colors = {
            "primary": sector_colors.get("primary", "#3B82F6"),
            "secondary": sector_colors.get("secondary", "#10B981"),
            "background": "#FFFFFF",
            "text": "#1F2937"
        }
        
        # Override with colors from content_generation if available
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
            "features": lambda: self._map_features_section(brief, sector_config),
            "contact": lambda: self._map_contact_section(brief),
            "footer": lambda: self._map_footer_section(brief),
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
    
    def _map_hero_section(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, Any]:
        """Génère la section Hero"""
        cta_text = sector_config.get("cta_text", "Nous contacter")
        
        return {
            "id": "hero",
            "type": "hero",
            "content": {
                "title": brief.value_proposition or brief.business_name,
                "subtitle": brief.mission,
                "description": brief.differentiation[:200] if brief.differentiation else None,
                "image": self._extract_hero_image(brief),
                "cta": {
                    "text": cta_text,
                    "link": "#contact",
                    "variant": "primary"
                },
                "alignment": "center",
                "overlay": False
            }
        }
    
    def _map_about_section(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, Any]:
        """Génère la section À propos"""
        about_title = sector_config.get("about_title", "À Propos de Nous")
        
        # Extract stats if available
        stats = None
        if brief.content_generation and isinstance(brief.content_generation, dict):
            raw_stats = brief.content_generation.get("stats", [])
            if raw_stats:
                stats = [{"value": s.get("value", ""), "label": s.get("label", "")} 
                        for s in raw_stats[:4]]  # Max 4 stats
        
        # Extract about image
        about_image = None
        if brief.content_generation and isinstance(brief.content_generation, dict):
            about_image = brief.content_generation.get("about_image")
        
        return {
            "id": "about",
            "type": "about",
            "content": {
                "title": about_title,
                "subtitle": brief.business_name,
                "description": brief.mission or "",
                "mission": brief.mission,
                "vision": brief.vision,
                "image": about_image,
                "stats": stats
            }
        }
    
    def _map_services_section(self, brief: BusinessBrief, sector_config: Dict) -> Optional[Dict[str, Any]]:
        """Génère la section Services"""
        services = []
        default_icons = sector_config.get("default_icons", ["star", "check", "zap"])
        
        # Extract services from brief.services or content_generation
        raw_services = []
        if brief.services:
            # Services can be a list of strings or dicts
            raw_services = brief.services if isinstance(brief.services, list) else []
        
        if brief.content_generation and isinstance(brief.content_generation, dict):
            gen_services = brief.content_generation.get("services", [])
            if gen_services:
                raw_services = gen_services
        
        if not raw_services:
            return None
        
        for i, service in enumerate(raw_services[:6]):  # Max 6 services
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
    
    def _map_footer_section(self, brief: BusinessBrief) -> Dict[str, Any]:
        """Génère la section Footer"""
        logo_url = self._extract_logo_url(brief)
        
        # Extract social links for footer
        social_links = None
        if brief.content_generation and isinstance(brief.content_generation, dict):
            socials = brief.content_generation.get("social_links", [])
            if socials:
                social_links = [
                    {"platform": s.get("platform"), "url": s.get("url")}
                    for s in socials if s.get("platform") and s.get("url")
                ]
        
        # Year dynamique
        from datetime import datetime
        current_year = datetime.now().year
        
        return {
            "id": "footer",
            "type": "footer",
            "content": {
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
                "socialLinks": social_links
            }
        }
