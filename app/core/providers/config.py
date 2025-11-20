"""
Provider Configuration and Plan Mappings

Defines which AI providers are used for each subscription plan.
Optimizes for cost/quality balance based on user tier.
"""

from typing import Dict, Any
from enum import Enum


class SubscriptionPlan(str, Enum):
    """Plans d'abonnement Genesis AI"""
    TRIAL = "trial"
    BASIC = "genesis_basic"
    PRO = "genesis_pro"
    ENTERPRISE = "genesis_enterprise"


class ProviderConfig:
    """Configuration des providers AI par plan"""
    
    # Plans tarifaires avec providers optimisés
    PLAN_PROVIDER_MAPPING: Dict[str, Dict[str, str]] = {
        # Plan Essai (3 sessions gratuites)
        SubscriptionPlan.TRIAL: {
            "llm_provider": "mock",  # Mock pour essai
            "llm_model": "mock-gpt",
            "search_provider": "mock",
            "image_provider": "mock"
        },
        
        # Plan Basic - Économique (10 sessions/mois)
        SubscriptionPlan.BASIC: {
            "llm_provider": "deepseek",  # ~70% moins cher qu'OpenAI
            "llm_model": "deepseek-chat",
            "search_provider": "kimi",  # Accès web natif, long contexte
            "image_provider": "dalle-mini"  # Version économique
        },
        
        # Plan Pro - Équilibré (50 sessions/mois)
        SubscriptionPlan.PRO: {
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",  # Bon rapport qualité/prix
            "search_provider": "tavily",  # Spécialisé recherche
            "image_provider": "dalle-3"  # Haute qualité
        },
        
        # Plan Enterprise - Premium (illimité)
        SubscriptionPlan.ENTERPRISE: {
            "llm_provider": "anthropic",
            "llm_model": "claude-3-opus-20240229",  # Top qualité
            "search_provider": "tavily",
            "search_config": {"depth": "advanced"},
            "image_provider": "dalle-3",
            "image_config": {"quality": "hd"}
        }
    }
    
    # Configuration détaillée par provider
    PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
        # LLM Providers
        "openai": {
            "api_base": "https://api.openai.com/v1",
            "models": {
                "gpt-4o": {"max_tokens": 4096, "cost_per_1k": 0.03},
                "gpt-4o-mini": {"max_tokens": 16384, "cost_per_1k": 0.00015},
                "gpt-4-turbo": {"max_tokens": 4096, "cost_per_1k": 0.01}
            },
            "timeout": 30,
            "retry_attempts": 3
        },
        
        "anthropic": {
            "api_base": "https://api.anthropic.com/v1",
            "models": {
                "claude-3-opus-20240229": {"max_tokens": 4096, "cost_per_1k": 0.015},
                "claude-3-sonnet-20240229": {"max_tokens": 4096, "cost_per_1k": 0.003},
                "claude-3-haiku-20240307": {"max_tokens": 4096, "cost_per_1k": 0.00025}
            },
            "timeout": 30,
            "retry_attempts": 3
        },
        
        "deepseek": {
            "api_base": "https://api.deepseek.com/v1",
            "models": {
                "deepseek-chat": {"max_tokens": 4096, "cost_per_1k": 0.0001},
                "deepseek-coder": {"max_tokens": 4096, "cost_per_1k": 0.0001}
            },
            "timeout": 30,
            "retry_attempts": 3
        },
        
        "gemini": {
            "api_base": "https://generativelanguage.googleapis.com/v1",
            "models": {
                "gemini-pro": {"max_tokens": 2048, "cost_per_1k": 0.0005},
                "gemini-pro-vision": {"max_tokens": 2048, "cost_per_1k": 0.002}
            },
            "timeout": 30,
            "retry_attempts": 3
        },
        
        # Search Providers
        "tavily": {
            "api_base": "https://api.tavily.com",
            "search_depths": ["basic", "advanced"],
            "max_results_limit": 20,
            "timeout": 15
        },
        
        "kimi": {
            "api_base": "https://api.moonshot.cn/v1",
            "model": "moonshot-v1-128k",  # 128K contexte
            "web_search_enabled": True,
            "timeout": 30
        },
        
        # Image Providers
        "dalle-3": {
            "api_base": "https://api.openai.com/v1",
            "sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "qualities": ["standard", "hd"],
            "cost_per_image": {"standard": 0.04, "hd": 0.08}
        },
        
        "dalle-mini": {
            "api_base": "https://api.openai.com/v1",
            "model": "dall-e-2",
            "sizes": ["256x256", "512x512", "1024x1024"],
            "cost_per_image": 0.02
        },
        
        # Mock Provider (pour tests et développement)
        "mock": {
            "enabled": True,
            "simulate_latency": True,
            "latency_ms": 500
        }
    }
    
    @classmethod
    def get_provider_for_plan(cls, plan: str, provider_type: str) -> str:
        """
        Retourne le provider approprié pour un plan donné
        
        Args:
            plan: Plan d'abonnement (trial, basic, pro, enterprise)
            provider_type: Type de provider (llm_provider, search_provider, image_provider)
            
        Returns:
            Nom du provider à utiliser
        """
        plan_config = cls.PLAN_PROVIDER_MAPPING.get(plan, cls.PLAN_PROVIDER_MAPPING[SubscriptionPlan.TRIAL])
        return plan_config.get(provider_type, "mock")
    
    @classmethod
    def get_provider_config(cls, provider_name: str) -> Dict[str, Any]:
        """
        Retourne la configuration détaillée d'un provider
        
        Args:
            provider_name: Nom du provider
            
        Returns:
            Configuration du provider
        """
        return cls.PROVIDER_CONFIGS.get(provider_name, {})
    
    @classmethod
    def get_model_for_plan(cls, plan: str) -> str:
        """
        Retourne le modèle LLM approprié pour un plan
        
        Args:
            plan: Plan d'abonnement
            
        Returns:
            Nom du modèle LLM
        """
        plan_config = cls.PLAN_PROVIDER_MAPPING.get(plan, cls.PLAN_PROVIDER_MAPPING[SubscriptionPlan.TRIAL])
        return plan_config.get("llm_model", "mock-gpt")


# Export pour faciliter l'import
PLAN_PROVIDER_MAPPING = ProviderConfig.PLAN_PROVIDER_MAPPING
