"""
Quota Management Service
Gère les quotas de sessions coaching selon les plans tarifaires DigitalCloud360.

Source de vérité : DigitalCloud360 API
Plans : Trial (3), Basic (10/mois), Pro (50/mois), Enterprise (illimité)
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import structlog

from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.utils.exceptions import GenesisAIException


logger = structlog.get_logger()


class SubscriptionPlan(str, Enum):
    """Plans tarifaires DigitalCloud360"""
    TRIAL = "trial"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class QuotaLimits:
    """Limites de quotas par plan"""
    LIMITS = {
        SubscriptionPlan.TRIAL: {
            "max_sessions_per_month": 3,
            "max_sessions_total": 3,
            "features": ["basic_coaching", "basic_brief"]
        },
        SubscriptionPlan.BASIC: {
            "max_sessions_per_month": 10,
            "max_sessions_total": None,  # Illimité
            "features": ["coaching", "business_brief", "market_research"]
        },
        SubscriptionPlan.PRO: {
            "max_sessions_per_month": 50,
            "max_sessions_total": None,
            "features": ["coaching", "business_brief", "market_research", "logo_generation", "seo_optimization"]
        },
        SubscriptionPlan.ENTERPRISE: {
            "max_sessions_per_month": None,  # Illimité
            "max_sessions_total": None,
            "features": ["all"]
        }
    }

    @classmethod
    def get_limit(cls, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Récupère les limites pour un plan donné"""
        return cls.LIMITS.get(plan, cls.LIMITS[SubscriptionPlan.TRIAL])


class QuotaExceededException(GenesisAIException):
    """Exception levée quand le quota est dépassé"""
    def __init__(
        self,
        message: str,
        current_usage: int,
        max_allowed: int,
        plan: str,
        reset_date: Optional[str] = None
    ):
        super().__init__(
            status_code=403,
            error_code="GENESIS_QUOTA_EXCEEDED",
            message=message,
            details={
                "current_usage": current_usage,
                "max_allowed": max_allowed,
                "plan": plan,
                "reset_date": reset_date,
                "upgrade_url": "https://digitalcloud360.ci/upgrade"
            }
        )


class QuotaManager:
    """
    Gestionnaire de quotas pour Genesis AI.
    
    Responsabilités:
    - Vérifier les quotas avant autorisation session
    - Incrémenter l'usage après session réussie
    - Synchroniser avec DigitalCloud360 API
    """
    
    def __init__(self, dc360_client: Optional[DigitalCloud360APIClient] = None):
        """
        Initialize QuotaManager.
        
        Args:
            dc360_client: Client DigitalCloud360 API (optionnel pour tests)
        """
        self.dc360_client = dc360_client or DigitalCloud360APIClient()
        self.logger = logger.bind(service="QuotaManager")
    
    async def check_quota(self, user_id: int) -> Dict[str, Any]:
        """
        Vérifie si l'utilisateur peut démarrer une nouvelle session.
        
        Args:
            user_id: ID utilisateur DigitalCloud360
            
        Returns:
            Dict contenant:
                - can_start_session: bool
                - current_usage: int
                - max_monthly_sessions: int | None
                - plan: str
                - reset_date: str (ISO format)
                
        Raises:
            QuotaExceededException: Si le quota est dépassé
        """
        self.logger.info("Checking quota", user_id=user_id)
        
        try:
            # 1. Récupérer abonnement + usage depuis DC360 API
            subscription_data = await self.dc360_client.get_user_subscription(user_id)
            
            plan = subscription_data.get("plan", SubscriptionPlan.TRIAL)
            current_usage = subscription_data.get("genesis_sessions_used", 0)
            reset_date = subscription_data.get("quota_reset_date")  # ISO format
            
            # 2. Récupérer limites pour ce plan
            limits = QuotaLimits.get_limit(plan)
            max_sessions = limits["max_sessions_per_month"]
            
            # 3. Vérifier si quota dépassé
            if max_sessions is not None and current_usage >= max_sessions:
                self.logger.warning(
                    "Quota exceeded",
                    user_id=user_id,
                    plan=plan,
                    current_usage=current_usage,
                    max_allowed=max_sessions
                )
                
                raise QuotaExceededException(
                    message=f"Quota mensuel dépassé pour le plan {plan.upper()}. "
                            f"Vous avez utilisé {current_usage}/{max_sessions} sessions. "
                            f"Mettez à niveau votre plan ou attendez le {reset_date}.",
                    current_usage=current_usage,
                    max_allowed=max_sessions,
                    plan=plan,
                    reset_date=reset_date
                )
            
            # 4. Quota OK
            self.logger.info(
                "Quota check passed",
                user_id=user_id,
                plan=plan,
                usage=f"{current_usage}/{max_sessions or 'unlimited'}"
            )
            
            return {
                "can_start_session": True,
                "current_usage": current_usage,
                "max_monthly_sessions": max_sessions,
                "plan": plan,
                "reset_date": reset_date,
                "features_available": limits["features"]
            }
            
        except QuotaExceededException:
            raise
        except Exception as e:
            self.logger.error("Failed to check quota", error=str(e), user_id=user_id)
            
            # Fallback: en cas d'erreur API DC360, autoriser avec warning
            # (évite de bloquer utilisateurs si DC360 down)
            self.logger.warning("Quota check fallback: allowing session", user_id=user_id)
            return {
                "can_start_session": True,
                "current_usage": 0,
                "max_monthly_sessions": None,
                "plan": "unknown",
                "reset_date": None,
                "fallback_mode": True
            }
    
    async def increment_usage(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """
        Incrémente le compteur d'usage après session réussie.
        
        Args:
            user_id: ID utilisateur
            session_id: ID session coaching/brief généré
            
        Returns:
            Dict avec new_usage, max_allowed
        """
        self.logger.info("Incrementing usage", user_id=user_id, session_id=session_id)
        
        try:
            # Appeler DC360 API pour incrémenter
            result = await self.dc360_client.increment_genesis_usage(user_id, session_id)
            
            new_usage = result.get("genesis_sessions_used", 0)
            max_sessions = result.get("max_monthly_sessions")
            
            self.logger.info(
                "Usage incremented",
                user_id=user_id,
                new_usage=new_usage,
                max_sessions=max_sessions
            )
            
            return {
                "new_usage": new_usage,
                "max_allowed": max_sessions,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(
                "Failed to increment usage",
                error=str(e),
                user_id=user_id,
                session_id=session_id
            )
            # Ne pas bloquer si incrémentation échoue (comptabilisation best-effort)
            return {
                "new_usage": None,
                "max_allowed": None,
                "error": str(e)
            }
    
    async def get_quota_status(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère le statut quota actuel (sans vérification stricte).
        
        Utilisé pour affichage frontend.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dict avec usage actuel, limites, plan
        """
        self.logger.info("Getting quota status", user_id=user_id)
        
        try:
            subscription_data = await self.dc360_client.get_user_subscription(user_id)
            
            plan = subscription_data.get("plan", SubscriptionPlan.TRIAL)
            current_usage = subscription_data.get("genesis_sessions_used", 0)
            limits = QuotaLimits.get_limit(plan)
            max_sessions = limits["max_sessions_per_month"]
            
            return {
                "user_id": user_id,
                "plan": plan,
                "current_usage": current_usage,
                "max_monthly_sessions": max_sessions,
                "remaining": max_sessions - current_usage if max_sessions else None,
                "reset_date": subscription_data.get("quota_reset_date"),
                "percentage_used": (current_usage / max_sessions * 100) if max_sessions else 0
            }
            
        except Exception as e:
            self.logger.error("Failed to get quota status", error=str(e), user_id=user_id)
            return {
                "user_id": user_id,
                "plan": "unknown",
                "current_usage": 0,
                "max_monthly_sessions": None,
                "error": str(e)
            }
