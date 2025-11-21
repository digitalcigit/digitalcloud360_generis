"""
Sub-Agents Spécialisés Genesis AI

5 sous-agents autonomes pour génération business brief complet:
- ResearchSubAgent: Analyse marché et concurrence
- ContentSubAgent: Génération contenu multilingue
- LogoSubAgent: Création identité visuelle
- SEOSubAgent: Optimisation SEO
- TemplateSubAgent: Sélection templates web
"""

from app.core.deep_agents.sub_agents.research import ResearchSubAgent
from app.core.deep_agents.sub_agents.content import ContentSubAgent

__all__ = ["ResearchSubAgent", "ContentSubAgent"]
