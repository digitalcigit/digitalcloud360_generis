"""Custom exceptions for Genesis AI Service"""

from typing import Any, Dict, Optional


class GenesisAIException(Exception):
    """Base exception for Genesis AI with structured error details"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        error_code: str = "GENESIS_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class AgentException(GenesisAIException):
    """Exception levée par les agents"""
    def __init__(self, message: str = "Agent error", **kwargs):
        super().__init__(
            message=message,
            status_code=kwargs.get("status_code", 500),
            error_code=kwargs.get("error_code", "GENESIS_AGENT_ERROR"),
            details=kwargs.get("details")
        )


class IntegrationException(GenesisAIException):
    """Exception levée lors d'erreurs d'intégration externe"""
    def __init__(self, message: str = "Integration error", **kwargs):
        super().__init__(
            message=message,
            status_code=kwargs.get("status_code", 503),
            error_code=kwargs.get("error_code", "GENESIS_INTEGRATION_ERROR"),
            details=kwargs.get("details")
        )


class OrchestratorException(GenesisAIException):
    """Exception levée par l'orchestrateur"""
    def __init__(self, message: str = "Orchestrator error", **kwargs):
        super().__init__(
            message=message,
            status_code=kwargs.get("status_code", 500),
            error_code=kwargs.get("error_code", "GENESIS_ORCHESTRATOR_ERROR"),
            details=kwargs.get("details")
        )