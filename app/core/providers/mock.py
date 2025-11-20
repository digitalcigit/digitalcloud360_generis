"""
Mock Providers for Development and Testing

Simule les comportements des providers AI sans appels externes.
Utilisé pour Sprint 1 et tests automatisés.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseLLMProvider, BaseSearchProvider, BaseImageProvider


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM Provider pour tests et développement"""
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse mockée"""
        # Simule latence réseau
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(self.config.get("latency_ms", 500) / 1000)
        
        return f"""Réponse générée par Mock LLM Provider
Modèle: {self.model}
Prompt: {prompt[:100]}...
Temperature: {temperature}

Ceci est une réponse simulée pour le développement et les tests.
En production, ce texte serait généré par {self.model}."""
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Génère une réponse structurée mockée"""
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(self.config.get("latency_ms", 500) / 1000)
        
        # Génère une réponse structurée basique selon le schéma
        mock_response = {
            "generated_by": f"mock-{self.model}",
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": prompt[:50],
            "data": {}
        }
        
        # Remplit avec des valeurs par défaut selon le schéma
        for key, value_type in response_schema.items():
            if value_type == "string":
                mock_response["data"][key] = f"Mock {key}"
            elif value_type == "number":
                mock_response["data"][key] = 42
            elif value_type == "array":
                mock_response["data"][key] = ["item1", "item2", "item3"]
            elif value_type == "object":
                mock_response["data"][key] = {"mock": "data"}
        
        return mock_response
    
    async def health_check(self) -> bool:
        """Mock provider toujours disponible"""
        return True


class MockSearchProvider(BaseSearchProvider):
    """Mock Search Provider pour tests et développement"""
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Recherche web mockée"""
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(self.config.get("latency_ms", 500) / 1000)
        
        # Génère des résultats de recherche fictifs
        mock_results = []
        for i in range(min(max_results, 5)):
            mock_results.append({
                "title": f"Résultat {i+1} pour: {query}",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"Extrait pertinent du résultat {i+1} concernant {query}...",
                "domain": f"example{i+1}.com",
                "published_date": "2025-01-01",
                "relevance_score": 0.9 - (i * 0.1)
            })
        
        return {
            "results": mock_results,
            "query": query,
            "search_metadata": {
                "total_results": len(mock_results),
                "search_depth": search_depth,
                "provider": "mock",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def analyze_market(
        self,
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse de marché mockée"""
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(1.0)  # Analyse plus longue
        
        sector = business_context.get("sector", "commerce")
        city = business_context.get("city", "Abidjan")
        country = business_context.get("country", "Côte d'Ivoire")
        
        return {
            "market_size": {
                "estimated_value": "15M XOF",
                "growth_rate": "12% annuel",
                "market_maturity": "En croissance"
            },
            "competitors": [
                {
                    "name": f"Concurrent A - {sector}",
                    "strengths": ["Présence locale", "Prix compétitifs"],
                    "weaknesses": ["Service client limité", "Technologie ancienne"],
                    "market_share": "25%"
                },
                {
                    "name": f"Concurrent B - {sector}",
                    "strengths": ["Marque forte", "Large gamme"],
                    "weaknesses": ["Prix élevés", "Délais livraison"],
                    "market_share": "18%"
                }
            ],
            "opportunities": [
                f"Marché {sector} en forte croissance à {city}",
                "Digitalisation limitée des concurrents",
                "Demande croissante pour services de qualité",
                "Niche sous-exploitée dans segment premium"
            ],
            "pricing_insights": {
                "average_price_range": "5,000 - 50,000 XOF",
                "price_sensitivity": "Moyenne",
                "recommended_positioning": "Milieu de gamme avec valeur ajoutée"
            },
            "differentiation_suggestions": [
                "Service client excellence via WhatsApp",
                "Livraison rapide et fiable",
                "Programme fidélité innovant",
                "Présence digitale professionnelle"
            ],
            "_metadata": {
                "location": f"{city}, {country}",
                "sector": sector,
                "generated_by": "mock-search-provider",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def health_check(self) -> bool:
        """Mock provider toujours disponible"""
        return True


class MockImageProvider(BaseImageProvider):
    """Mock Image Provider pour tests et développement"""
    
    async def generate_logo(
        self,
        business_name: str,
        industry: str,
        style: str = "modern",
        color_scheme: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Génération de logo mockée"""
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(2.0)  # Génération d'image plus longue
        
        colors = color_scheme or ["#0066CC", "#00CC66"]
        
        return {
            "image_url": f"https://placehold.co/400x400/0066CC/FFFFFF?text={business_name[:10]}",
            "image_data": None,  # En production: base64
            "prompt_used": f"Modern logo for {business_name}, {industry} industry, {style} style, colors: {colors}",
            "metadata": {
                "business_name": business_name,
                "industry": industry,
                "style": style,
                "color_scheme": colors,
                "size": "400x400",
                "format": "PNG",
                "provider": "mock",
                "timestamp": datetime.utcnow().isoformat()
            },
            "variations": [
                f"https://placehold.co/400x400/{colors[0][1:]}/FFFFFF?text={business_name[:5]}-1",
                f"https://placehold.co/400x400/{colors[1][1:]}/FFFFFF?text={business_name[:5]}-2"
            ]
        }
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """Génération d'image générique mockée"""
        if self.config.get("simulate_latency", True):
            await asyncio.sleep(2.0)
        
        return {
            "image_url": f"https://placehold.co/{size}/0066CC/FFFFFF?text=Generated+Image",
            "image_data": None,
            "metadata": {
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "provider": "mock",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def health_check(self) -> bool:
        """Mock provider toujours disponible"""
        return True
