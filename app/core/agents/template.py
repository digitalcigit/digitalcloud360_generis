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

    async def run(self, business_type: str, theme_id: int = None, theme_slug: str = None) -> dict:
        """
        Sélectionne un template de site web approprié ou utilise celui spécifié.

        Args:
            business_type: Le type d'entreprise (ex: "e-commerce", "portfolio", "service").
            theme_id: ID du thème sélectionné par l'utilisateur (optionnel).
            theme_slug: Slug du thème sélectionné par l'utilisateur (optionnel).

        Returns:
            Un dictionnaire contenant les informations du template sélectionné.
        """
        try:
            if theme_id and theme_slug:
                logger.info("Using pre-selected theme", theme_id=theme_id, theme_slug=theme_slug)
                return {"id": theme_slug, "theme_id": theme_id, "name": theme_slug.capitalize()}

            logger.info("Selecting website template...", business_type=business_type)
            
            # Logique de sélection de template simplifiée
            selected_template = self._select_template(business_type)
            
            logger.info("Template selected successfully.", template=selected_template)
            
            return selected_template

        except Exception as e:
            logger.error("Error during template agent execution", error=str(e))
            raise AgentException(
                message="Failed to select a website template.",
                error_code="TEMPLATE_AGENT_ERROR",
                details={"error": str(e)}
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