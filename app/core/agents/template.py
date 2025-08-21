import structlog
import random
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class TemplateAgent:
    """
    Agent spécialisé dans la sélection d'un template de site web.
    """
    def __init__(self):
        # Dans une implémentation réelle, cela pourrait charger des templates depuis une base de données ou un service.
        self.available_templates = [
            {"id": "modern_business_01", "name": "Modern Business"},
            {"id": "creative_portfolio_02", "name": "Creative Portfolio"},
            {"id": "ecommerce_sleek_03", "name": "Sleek E-commerce"},
            {"id": "service_booking_04", "name": "Service Booking Pro"}
        ]
        logger.info("TemplateAgent initialized.")

    async def run(self, business_type: str) -> dict:
        """
        Sélectionne un template de site web approprié.

        Args:
            business_type: Le type d'entreprise (ex: "e-commerce", "portfolio", "service").

        Returns:
            Un dictionnaire contenant les informations du template sélectionné.
        """
        try:
            logger.info("Selecting website template...", business_type=business_type)
            
            # Logique de sélection de template simplifiée
            # Dans une version avancée, on utiliserait un modèle de matching ou des règles plus complexes.
            selected_template = self._select_template(business_type)
            
            logger.info("Template selected successfully.", template=selected_template)
            
            return selected_template

        except Exception as e:
            logger.error("Error during template agent execution", error=str(e))
            raise AgentException(
                "TEMPLATE_AGENT_ERROR",
                "Failed to select a website template.",
                details=str(e)
            )

    def _select_template(self, business_type: str) -> dict:
        """Logique de sélection de template (placeholder)."""
        if "e-commerce" in business_type.lower():
            return self.available_templates[2] # Sleek E-commerce
        if "portfolio" in business_type.lower():
            return self.available_templates[1] # Creative Portfolio
        if "service" in business_type.lower():
            return self.available_templates[3] # Service Booking Pro
        
        # Par défaut, retourne un template business générique
        return self.available_templates[0] # Modern Business