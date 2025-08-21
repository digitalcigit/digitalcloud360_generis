import structlog
from app.core.integrations.openai import OpenAIClient  # Assumes an OpenAI client exists
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class ContentAgent:
    """
    Agent spécialisé dans la génération de contenu textuel pour le site web.
    """
    def __init__(self):
        self.openai_client = OpenAIClient()
        logger.info("ContentAgent initialized.")

    async def run(self, business_brief: dict, market_research: dict) -> dict:
        """
        Génère le contenu textuel principal du site web.

        Args:
            business_brief: Le brief de l'entreprise fourni par le client.
            market_research: Les résultats de l'analyse de marché.

        Returns:
            Un dictionnaire contenant les textes générés pour le site.
        """
        try:
            logger.info("Generating website content...", business_brief=business_brief)
            
            prompt = self._build_prompt(business_brief, market_research)
            
            generated_text = await self.openai_client.generate_text(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7
            )
            
            logger.info("Website content generated successfully.")
            
            return self._format_output(generated_text)

        except Exception as e:
            logger.error("Error during content agent execution", error=str(e))
            raise AgentException(
                "CONTENT_AGENT_ERROR",
                "Failed to generate website content.",
                details=str(e)
            )

    def _build_prompt(self, business_brief: dict, market_research: dict) -> str:
        """Construit le prompt pour le modèle de langage."""
        return f"""
        Vous êtes un expert en copywriting pour les startups africaines.
        Rédigez le contenu pour le site web d'une entreprise avec la description suivante:
        
        **Entreprise:** {business_brief.get('company_name', 'N/A')}
        **Description:** {business_brief.get('company_description', 'N/A')}
        **Services/Produits:** {business_brief.get('services', 'N/A')}
        **Public Cible:** {business_brief.get('target_audience', 'N/A')}
        **Ton de Voix:** {business_brief.get('tone_of_voice', 'professionnel et accessible')}
        
        **Analyse de Marché:**
        {market_research.get('market_research', 'N/A')}
        
        **Analyse des Concurrents:**
        {market_research.get('competitor_analysis', 'N/A')}
        
        **Instructions:**
        1.  **Page d'Accueil:** Rédigez un titre accrocheur, un sous-titre, et une brève section "À propos de nous".
        2.  **Page Services:** Décrivez les principaux services/produits offerts.
        3.  **Page Contact:** Rédigez un appel à l'action pour prendre contact.
        
        Structurez votre réponse en JSON.
        """

    def _format_output(self, generated_text: str) -> dict:
        """Formate la sortie texte en un dictionnaire structuré."""
        # This assumes the model returns a JSON string.
        # In a real implementation, you would add robust JSON parsing and validation.
        import json
        try:
            return json.loads(generated_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM output as JSON. Returning raw text.")
            return {"raw_text": generated_text}