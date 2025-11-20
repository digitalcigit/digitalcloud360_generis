"""
Base Provider Interfaces for Multi-Provider Architecture

Abstract base classes for LLM, Search, and Image generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum


class ProviderType(str, Enum):
    """Types de providers disponibles"""
    LLM = "llm"
    SEARCH = "search"
    IMAGE = "image"


class BaseLLMProvider(ABC):
    """
    Interface abstraite pour les fournisseurs LLM
    
    Implémentations prévues:
    - OpenAI (GPT-4, GPT-4o-mini)
    - Anthropic (Claude 3 Opus, Sonnet, Haiku)
    - Deepseek
    - Google Gemini
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Génère une réponse textuelle
        
        Args:
            prompt: Le prompt utilisateur
            system_message: Message système optionnel
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            
        Returns:
            str: Texte généré
        """
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une réponse structurée (JSON)
        
        Args:
            prompt: Le prompt utilisateur
            response_schema: Schéma de réponse attendu
            system_message: Message système optionnel
            
        Returns:
            Dict: Réponse structurée
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie la disponibilité du provider"""
        pass


class BaseSearchProvider(ABC):
    """
    Interface abstraite pour les fournisseurs de recherche web
    
    Implémentations prévues:
    - Tavily (spécialisé recherche)
    - Kimi/Moonshot (LLM avec accès web natif)
    - Perplexity (alternative)
    """
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Effectue une recherche web
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
            search_depth: Profondeur de recherche (basic/advanced)
            include_domains: Domaines à inclure
            exclude_domains: Domaines à exclure
            
        Returns:
            Dict contenant:
                - results: Liste des résultats
                - query: Requête originale
                - search_metadata: Métadonnées de recherche
        """
        pass
    
    @abstractmethod
    async def analyze_market(
        self,
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyse de marché spécialisée pour Genesis AI
        
        Args:
            business_context: Contexte business (secteur, localisation, etc.)
            
        Returns:
            Dict contenant:
                - market_size: Taille du marché
                - competitors: Liste des concurrents
                - opportunities: Opportunités identifiées
                - pricing_insights: Insights tarifaires
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie la disponibilité du provider"""
        pass


class BaseImageProvider(ABC):
    """
    Interface abstraite pour les fournisseurs de génération d'images
    
    Implémentations prévues:
    - OpenAI DALL-E 3
    - Google Gemini Imagen
    - Stable Diffusion
    - LogoAI (legacy)
    - Midjourney (si API disponible)
    """
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate_logo(
        self,
        business_name: str,
        industry: str,
        style: str = "modern",
        color_scheme: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère un logo pour une entreprise
        
        Args:
            business_name: Nom de l'entreprise
            industry: Secteur d'activité
            style: Style visuel souhaité
            color_scheme: Palette de couleurs
            
        Returns:
            Dict contenant:
                - image_url: URL de l'image générée
                - image_data: Données base64 (optionnel)
                - prompt_used: Prompt utilisé
                - metadata: Métadonnées de génération
        """
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une image générique
        
        Args:
            prompt: Description de l'image
            size: Taille de l'image
            quality: Qualité de génération
            
        Returns:
            Dict contenant:
                - image_url: URL de l'image
                - image_data: Données base64 (optionnel)
                - metadata: Métadonnées
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie la disponibilité du provider"""
        pass
