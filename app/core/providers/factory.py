"""
Provider Factory

Crée dynamiquement les instances de providers selon le plan d'abonnement.
Pattern Factory pour flexibilité et extensibilité.
"""

from typing import Dict, Any, Optional
import structlog

from .base import BaseLLMProvider, BaseSearchProvider, BaseImageProvider
from .config import ProviderConfig, SubscriptionPlan
from .mock import MockLLMProvider, MockSearchProvider, MockImageProvider
from .deepseek import DeepseekProvider

logger = structlog.get_logger(__name__)


class ProviderFactory:
    """
    Factory pour créer les instances de providers AI
    
    Usage:
        factory = ProviderFactory()
        llm = factory.create_llm_provider(plan="genesis_pro")
        search = factory.create_search_provider(plan="genesis_pro")
        image = factory.create_image_provider(plan="genesis_pro")
    """
    
    # Registry des providers disponibles
    _llm_providers: Dict[str, type] = {
        "mock": MockLLMProvider,
        "deepseek": DeepseekProvider,
        # Implémentations futures:
        # "openai": OpenAIProvider,
        # "anthropic": AnthropicProvider,
        # "gemini": GeminiProvider,
    }
    
    _search_providers: Dict[str, type] = {
        "mock": MockSearchProvider,
        # Implémentations futures:
        # "tavily": TavilyProvider,
        # "kimi": KimiProvider,
    }
    
    _image_providers: Dict[str, type] = {
        "mock": MockImageProvider,
        # Implémentations futures:
        # "dalle-3": DallE3Provider,
        # "dalle-mini": DallE2Provider,
        # "gemini": GeminiImageProvider,
    }
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize factory avec les clés API
        
        Args:
            api_keys: Dict des clés API par provider
                Exemple: {
                    "openai": "sk-...",
                    "anthropic": "sk-ant-...",
                    "tavily": "tvly-...",
                }
        """
        self.api_keys = api_keys or {}
    
    def create_llm_provider(
        self,
        plan: str = SubscriptionPlan.TRIAL,
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Crée une instance de LLM provider selon le plan
        
        Args:
            plan: Plan d'abonnement
            override_provider: Provider spécifique à forcer (pour tests)
            override_model: Modèle spécifique à forcer
            **kwargs: Arguments additionnels pour le provider
            
        Returns:
            Instance du LLM provider
        """
        provider_name = override_provider or ProviderConfig.get_provider_for_plan(plan, "llm_provider")
        model = override_model or ProviderConfig.get_model_for_plan(plan)
        
        provider_class = self._llm_providers.get(provider_name)
        if not provider_class:
            logger.warning(
                f"Provider LLM '{provider_name}' non disponible, fallback vers mock",
                plan=plan,
                requested_provider=provider_name
            )
            provider_class = MockLLMProvider
            provider_name = "mock"
        
        api_key = self.api_keys.get(provider_name, "mock-key")
        provider_config = ProviderConfig.get_provider_config(provider_name)
        
        logger.info(
            "Création LLM provider",
            provider=provider_name,
            model=model,
            plan=plan
        )
        
        return provider_class(
            api_key=api_key,
            model=model,
            **{**provider_config, **kwargs}
        )
    
    def create_search_provider(
        self,
        plan: str = SubscriptionPlan.TRIAL,
        override_provider: Optional[str] = None,
        **kwargs
    ) -> BaseSearchProvider:
        """
        Crée une instance de Search provider selon le plan
        
        Args:
            plan: Plan d'abonnement
            override_provider: Provider spécifique à forcer
            **kwargs: Arguments additionnels
            
        Returns:
            Instance du Search provider
        """
        provider_name = override_provider or ProviderConfig.get_provider_for_plan(plan, "search_provider")
        
        provider_class = self._search_providers.get(provider_name)
        if not provider_class:
            logger.warning(
                f"Provider Search '{provider_name}' non disponible, fallback vers mock",
                plan=plan,
                requested_provider=provider_name
            )
            provider_class = MockSearchProvider
            provider_name = "mock"
        
        api_key = self.api_keys.get(provider_name, "mock-key")
        provider_config = ProviderConfig.get_provider_config(provider_name)
        
        logger.info(
            "Création Search provider",
            provider=provider_name,
            plan=plan
        )
        
        return provider_class(
            api_key=api_key,
            **{**provider_config, **kwargs}
        )
    
    def create_image_provider(
        self,
        plan: str = SubscriptionPlan.TRIAL,
        override_provider: Optional[str] = None,
        **kwargs
    ) -> BaseImageProvider:
        """
        Crée une instance de Image provider selon le plan
        
        Args:
            plan: Plan d'abonnement
            override_provider: Provider spécifique à forcer
            **kwargs: Arguments additionnels
            
        Returns:
            Instance du Image provider
        """
        provider_name = override_provider or ProviderConfig.get_provider_for_plan(plan, "image_provider")
        
        provider_class = self._image_providers.get(provider_name)
        if not provider_class:
            logger.warning(
                f"Provider Image '{provider_name}' non disponible, fallback vers mock",
                plan=plan,
                requested_provider=provider_name
            )
            provider_class = MockImageProvider
            provider_name = "mock"
        
        api_key = self.api_keys.get(provider_name, "mock-key")
        provider_config = ProviderConfig.get_provider_config(provider_name)
        
        logger.info(
            "Création Image provider",
            provider=provider_name,
            plan=plan
        )
        
        return provider_class(
            api_key=api_key,
            **{**provider_config, **kwargs}
        )
    
    @classmethod
    def register_llm_provider(cls, name: str, provider_class: type):
        """Enregistre un nouveau LLM provider"""
        cls._llm_providers[name] = provider_class
        logger.info(f"LLM Provider '{name}' enregistré")
    
    @classmethod
    def register_search_provider(cls, name: str, provider_class: type):
        """Enregistre un nouveau Search provider"""
        cls._search_providers[name] = provider_class
        logger.info(f"Search Provider '{name}' enregistré")
    
    @classmethod
    def register_image_provider(cls, name: str, provider_class: type):
        """Enregistre un nouveau Image provider"""
        cls._image_providers[name] = provider_class
        logger.info(f"Image Provider '{name}' enregistré")
