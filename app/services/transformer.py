"""Transformer service to convert BusinessBrief to SiteDefinition"""

from typing import Dict, Any, List
from app.models.coaching import BusinessBrief
import json

class BriefToSiteTransformer:
    """Transform a BusinessBrief into a SiteDefinition JSON structure"""
    
    def transform(self, brief: BusinessBrief) -> Dict[str, Any]:
        """
        Convert a BusinessBrief to a SiteDefinition.
        
        Args:
            brief: BusinessBrief model instance
            
        Returns:
            Dictionary matching SiteDefinition TypeScript interface
        """
        # Extract theme colors from content generation or use defaults
        theme_colors = self._extract_theme_colors(brief)
        
        # Build the site definition
        site_definition = {
            "metadata": {
                "title": brief.business_name,
                "description": brief.mission[:160] if brief.mission else "",  # SEO meta description
                "favicon": self._extract_logo_url(brief)
            },
            "theme": {
                "colors": theme_colors,
                "fonts": {
                    "heading": "Inter",
                    "body": "Inter"
                }
            },
            "pages": [
                self._build_home_page(brief)
            ]
        }
        
        return site_definition
    
    def _extract_theme_colors(self, brief: BusinessBrief) -> Dict[str, str]:
        """Extract theme colors from brief or use defaults"""
        # Try to get colors from content_generation or use sector-based defaults
        default_colors = {
            "primary": "#3B82F6",      # Blue
            "secondary": "#10B981",    # Green
            "background": "#FFFFFF",   # White
            "text": "#1F2937"          # Dark gray
        }
        
        if brief.content_generation and isinstance(brief.content_generation, dict):
            colors = brief.content_generation.get("theme_colors", {})
            if colors:
                return {**default_colors, **colors}
        
        return default_colors
    
    def _extract_logo_url(self, brief: BusinessBrief) -> str:
        """Extract logo URL from logo_creation results"""
        if brief.logo_creation and isinstance(brief.logo_creation, dict):
            return brief.logo_creation.get("logo_url", "")
        return ""
    
    def _build_home_page(self, brief: BusinessBrief) -> Dict[str, Any]:
        """Build the home page structure"""
        sections = []
        
        # Hero section
        sections.append({
            "id": "hero",
            "type": "hero",
            "content": {
                "title": brief.value_proposition,
                "subtitle": brief.mission,
                "image": self._extract_hero_image(brief),
                "cta": {
                    "text": "Commencer",
                    "link": "#contact"
                }
            }
        })
        
        # Features section (from content_generation or differentiation)
        features = self._extract_features(brief)
        if features:
            sections.append({
                "id": "features",
                "type": "features",
                "content": {
                    "title": "Nos Services",
                    "features": features
                }
            })
        
        # Footer section
        sections.append({
            "id": "footer",
            "type": "footer",
            "content": {
                "copyright": f"© 2024 {brief.business_name}. Tous droits réservés.",
                "links": [
                    {"text": "À propos", "url": "#about"},
                    {"text": "Contact", "url": "#contact"}
                ]
            }
        })
        
        return {
            "id": "home",
            "slug": "/",
            "title": "Accueil",
            "sections": sections
        }
    
    def _extract_hero_image(self, brief: BusinessBrief) -> str:
        """Extract hero image from content generation"""
        if brief.content_generation and isinstance(brief.content_generation, dict):
            return brief.content_generation.get("hero_image", "")
        return ""
    
    def _extract_features(self, brief: BusinessBrief) -> List[Dict[str, str]]:
        """Extract features from content_generation or create from differentiation"""
        features = []
        
        # Try to get from content_generation first
        if brief.content_generation and isinstance(brief.content_generation, dict):
            gen_features = brief.content_generation.get("features", [])
            if gen_features:
                return gen_features
        
        # Fallback: create basic features from differentiation
        if brief.differentiation:
            # Split differentiation into points (simple heuristic)
            points = brief.differentiation.split('.')[:3]  # Max 3 features
            for i, point in enumerate(points):
                if point.strip():
                    features.append({
                        "title": f"Avantage {i+1}",
                        "description": point.strip(),
                        "icon": "star"  # Default icon
                    })
        
        return features
