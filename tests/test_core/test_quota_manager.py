"""
Tests pour QuotaManager - P0.5
Validation logique quotas cohérente selon plan tarifaire
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.quota import (
    QuotaManager,
    QuotaExceededException,
    SubscriptionPlan,
    QuotaLimits
)

pytestmark = pytest.mark.asyncio


class TestQuotaLimits:
    """Tests configuration limites quotas"""
    
    def test_trial_limits(self):
        """Test limites plan Trial"""
        limits = QuotaLimits.get_limit(SubscriptionPlan.TRIAL)
        
        assert limits["max_sessions_per_month"] == 3
        assert limits["max_sessions_total"] == 3
        assert "basic_coaching" in limits["features"]
    
    def test_basic_limits(self):
        """Test limites plan Basic"""
        limits = QuotaLimits.get_limit(SubscriptionPlan.BASIC)
        
        assert limits["max_sessions_per_month"] == 10
        assert limits["max_sessions_total"] is None  # Illimité
        assert "market_research" in limits["features"]
    
    def test_pro_limits(self):
        """Test limites plan Pro"""
        limits = QuotaLimits.get_limit(SubscriptionPlan.PRO)
        
        assert limits["max_sessions_per_month"] == 50
        assert limits["max_sessions_total"] is None
        assert "logo_generation" in limits["features"]
    
    def test_enterprise_limits(self):
        """Test limites plan Enterprise (illimité)"""
        limits = QuotaLimits.get_limit(SubscriptionPlan.ENTERPRISE)
        
        assert limits["max_sessions_per_month"] is None  # Illimité
        assert limits["max_sessions_total"] is None
        assert limits["features"] == ["all"]


class TestQuotaManager:
    """Tests QuotaManager - vérification et incrémentation quotas"""
    
    async def test_check_quota_trial_within_limit(self):
        """Test vérification quota Trial - dans la limite"""
        # Mock DC360 API client
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.return_value = {
            "plan": SubscriptionPlan.TRIAL,
            "genesis_sessions_used": 1,
            "quota_reset_date": "2025-12-01T00:00:00Z"
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        result = await quota_manager.check_quota(user_id=123)
        
        assert result["can_start_session"] is True
        assert result["current_usage"] == 1
        assert result["max_monthly_sessions"] == 3
        assert result["plan"] == SubscriptionPlan.TRIAL
    
    async def test_check_quota_trial_exceeded(self):
        """Test vérification quota Trial - dépassé"""
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.return_value = {
            "plan": SubscriptionPlan.TRIAL,
            "genesis_sessions_used": 3,  # Limite atteinte
            "quota_reset_date": "2025-12-01T00:00:00Z"
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        with pytest.raises(QuotaExceededException) as exc_info:
            await quota_manager.check_quota(user_id=123)
        
        # Vérifier détails exception
        assert exc_info.value.status_code == 403
        assert exc_info.value.error_code == "GENESIS_QUOTA_EXCEEDED"
        assert exc_info.value.details["current_usage"] == 3
        assert exc_info.value.details["max_allowed"] == 3
        assert exc_info.value.details["plan"] == SubscriptionPlan.TRIAL
    
    async def test_check_quota_basic_within_limit(self):
        """Test vérification quota Basic - dans la limite"""
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.return_value = {
            "plan": SubscriptionPlan.BASIC,
            "genesis_sessions_used": 5,
            "quota_reset_date": "2025-12-01T00:00:00Z"
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        result = await quota_manager.check_quota(user_id=456)
        
        assert result["can_start_session"] is True
        assert result["current_usage"] == 5
        assert result["max_monthly_sessions"] == 10
    
    async def test_check_quota_enterprise_unlimited(self):
        """Test vérification quota Enterprise - illimité"""
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.return_value = {
            "plan": SubscriptionPlan.ENTERPRISE,
            "genesis_sessions_used": 1000,  # Usage élevé mais illimité
            "quota_reset_date": "2025-12-01T00:00:00Z"
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        result = await quota_manager.check_quota(user_id=789)
        
        assert result["can_start_session"] is True
        assert result["current_usage"] == 1000
        assert result["max_monthly_sessions"] is None  # Illimité
    
    async def test_check_quota_api_error_fallback(self):
        """Test fallback si erreur API DC360"""
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.side_effect = Exception("DC360 API down")
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        result = await quota_manager.check_quota(user_id=999)
        
        # Fallback mode: autoriser la session avec warning
        assert result["can_start_session"] is True
        assert result["fallback_mode"] is True
    
    async def test_increment_usage_success(self):
        """Test incrémentation usage après session réussie"""
        mock_dc360 = AsyncMock()
        mock_dc360.increment_genesis_usage.return_value = {
            "genesis_sessions_used": 6,
            "max_monthly_sessions": 10
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        result = await quota_manager.increment_usage(user_id=456, session_id="brief_abc123")
        
        assert result["new_usage"] == 6
        assert result["max_allowed"] == 10
        assert result["session_id"] == "brief_abc123"
        
        # Vérifier appel API
        mock_dc360.increment_genesis_usage.assert_called_once_with(456, "brief_abc123")
    
    async def test_increment_usage_api_error(self):
        """Test incrémentation avec erreur API (ne doit pas bloquer)"""
        mock_dc360 = AsyncMock()
        mock_dc360.increment_genesis_usage.side_effect = Exception("DC360 API error")
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        # Ne doit PAS lever exception (best-effort)
        result = await quota_manager.increment_usage(user_id=456, session_id="brief_xyz")
        
        assert result["new_usage"] is None
        assert "error" in result
    
    async def test_get_quota_status(self):
        """Test récupération statut quota pour affichage frontend"""
        mock_dc360 = AsyncMock()
        mock_dc360.get_user_subscription.return_value = {
            "plan": SubscriptionPlan.PRO,
            "genesis_sessions_used": 30,
            "quota_reset_date": "2025-12-01T00:00:00Z"
        }
        
        quota_manager = QuotaManager(dc360_client=mock_dc360)
        
        status = await quota_manager.get_quota_status(user_id=456)
        
        assert status["user_id"] == 456
        assert status["plan"] == SubscriptionPlan.PRO
        assert status["current_usage"] == 30
        assert status["max_monthly_sessions"] == 50
        assert status["remaining"] == 20  # 50 - 30
        assert status["percentage_used"] == 60.0  # (30/50) * 100
    
    async def test_quota_exceeded_exception_details(self):
        """Test détails exception QuotaExceededException"""
        exc = QuotaExceededException(
            message="Quota dépassé",
            current_usage=10,
            max_allowed=10,
            plan=SubscriptionPlan.BASIC,
            reset_date="2025-12-01T00:00:00Z"
        )
        
        assert exc.status_code == 403
        assert exc.error_code == "GENESIS_QUOTA_EXCEEDED"
        assert exc.message == "Quota dépassé"
        assert exc.details["current_usage"] == 10
        assert exc.details["max_allowed"] == 10
        assert exc.details["plan"] == SubscriptionPlan.BASIC
        assert exc.details["reset_date"] == "2025-12-01T00:00:00Z"
        assert "upgrade_url" in exc.details
