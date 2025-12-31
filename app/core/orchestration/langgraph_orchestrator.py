import structlog
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator

# Nouveaux sub-agents Sprint 2
from app.core.deep_agents.sub_agents.research import ResearchSubAgent
from app.core.deep_agents.sub_agents.content import ContentSubAgent

# Anciens agents (legacy - gardés temporairement)
from app.core.agents.logo import LogoAgent
from app.core.agents.seo import SeoAgent
from app.core.agents.template import TemplateAgent

from app.utils.exceptions import OrchestratorException

logger = structlog.get_logger(__name__)

# Define the state for the graph
class AgentState(TypedDict):
    """État orchestrateur LangGraph pour business brief generation"""
    user_id: int
    brief_id: str
    business_brief: Dict[str, Any]  # Format aligné DC360
    
    # Résultats sub-agents
    market_research: Dict[str, Any]
    content_generation: Dict[str, Any]
    logo_creation: Dict[str, Any]
    seo_optimization: Dict[str, Any]
    template_selection: Dict[str, Any]
    
    # Metadata
    selected_theme_id: Optional[int]
    selected_theme_slug: Optional[str]
    overall_confidence: float
    is_ready_for_website: bool
    error: Optional[str]

class LangGraphOrchestrator:
    """
    Orchestrateur basé sur LangGraph pour coordonner les sub-agents.
    
    Sprint 2: Utilise les nouveaux sub-agents (ResearchSubAgent, ContentSubAgent)
    avec architecture multi-provider.
    """
    def __init__(self):
        # Nouveaux sub-agents Sprint 2 (multi-provider)
        self.research_agent = ResearchSubAgent()
        self.content_agent = ContentSubAgent()
        
        # Anciens agents legacy (gardés temporairement)
        self.logo_agent = LogoAgent()
        self.seo_agent = SeoAgent()
        self.template_agent = TemplateAgent()
        
        self.graph = self._build_graph()
        logger.info("LangGraphOrchestrator initialized with all agents.")

    def _build_graph(self):
        """Construit le graphe d'exécution des agents."""
        workflow = StateGraph(AgentState)

        # Add nodes for each agent
        workflow.add_node("research", self.run_research_agent)
        workflow.add_node("content", self.run_content_agent)
        workflow.add_node("logo", self.run_logo_agent)
        workflow.add_node("seo", self.run_seo_agent)
        workflow.add_node("template", self.run_template_agent)

        # Define the execution flow: Sequential to ensure all agents execute
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "logo")
        workflow.add_edge("logo", "seo")
        workflow.add_edge("seo", "template")
        workflow.add_edge("template", END)

        # Compile the graph
        return workflow.compile()

    async def run_research_agent(self, state: AgentState) -> AgentState:
        """
        Exécute ResearchSubAgent avec nouveau format DC360.
        
        Transforme business_brief -> business_context pour analyze_market.
        """
        logger.info("Executing Research Sub-Agent (Sprint 2 - multi-provider)")
        
        brief = state['business_brief']
        
        # Préparer business_context pour ResearchSubAgent
        business_context = {
            'business_name': brief.get('business_name', 'Entreprise'),
            'industry_sector': brief.get('industry_sector', 'Services'),
            'location': brief.get('location', {}),
            'target_market': brief.get('target_market', ''),
            'vision': brief.get('vision', ''),
            'mission': brief.get('mission', ''),
            'competitive_advantage': brief.get('competitive_advantage', ''),
            'services': brief.get('services', [])
        }
        
        try:
            # Appel nouveau sub-agent
            result = await self.research_agent.analyze_market(business_context)
            logger.info(
                "Research completed",
                competitors_found=len(result.get('main_competitors', [])),
                opportunities_found=len(result.get('market_opportunities', []))
            )
            return {"market_research": result}
        except Exception as e:
            logger.error("Research agent failed", error=str(e))
            # Fallback gracieux
            return {
                "market_research": {
                    'error': str(e),
                    'fallback_mode': True,
                    'market_size_estimation': {},
                    'main_competitors': [],
                    'market_opportunities': []
                }
            }

    async def run_content_agent(self, state: AgentState) -> AgentState:
        """
        Exécute ContentSubAgent avec nouveau format DC360.
        
        Génère contenu site web complet multilingue.
        """
        logger.info("Executing Content Sub-Agent (Sprint 2 - multi-provider)")
        
        try:
            # Appel nouveau sub-agent (format déjà aligné DC360)
            result = await self.content_agent.generate_website_content(state['business_brief'])
            logger.info(
                "Content generated",
                sections=len([k for k in result.keys() if k not in ['languages_generated', 'content_strategy', 'generation_metadata']]),
                languages=result.get('languages_generated', ['fr'])
            )
            return {"content_generation": result}
        except Exception as e:
            logger.error("Content agent failed", error=str(e))
            # Fallback gracieux
            return {
                "content_generation": {
                    'error': str(e),
                    'fallback_mode': True,
                    'homepage': {},
                    'about': {},
                    'services': {},
                    'contact': {}
                }
            }

    async def run_logo_agent(self, state: AgentState) -> AgentState:
        """
        Exécute LogoAgent avec DALL-E 3 (Sprint 3 refactored).
        """
        logger.info("Executing Logo Agent (DALL-E 3)")
        
        brief = state['business_brief']
        try:
            result = await self.logo_agent.run(
                company_name=brief.get('business_name', 'Mon Business'),
                industry=brief.get('industry_sector', 'Services'),
                style='modern',  # Style par défaut, sera adapté par agent selon industrie
                company_slogan=brief.get('slogan', brief.get('vision', '')),
                use_cache=True
            )
            return {"logo_creation": result}
        except Exception as e:
            logger.error("Logo agent failed", error=str(e))
            return {
                "logo_creation": {
                    'error': str(e),
                    'fallback_mode': True,
                    'logo_url': 'https://placehold.co/400x400/3B82F6/FFFFFF/png?text=Logo'
                }
            }

    async def run_seo_agent(self, state: AgentState) -> AgentState:
        """
        Exécute SeoAgent avec Deepseek LLM (Sprint 3 refactored).
        """
        logger.info("Executing SEO Agent (Deepseek LLM)")
        
        brief = state['business_brief']
        try:
            # Construire description business complète
            business_description = f"{brief.get('vision', '')} {brief.get('mission', '')}".strip()
            if not business_description:
                business_description = brief.get('description', 'Professional business services')
            
            result = await self.seo_agent.run(
                business_name=brief.get('business_name', 'Mon Business'),
                business_description=business_description,
                industry_sector=brief.get('industry_sector', 'Services'),
                target_location=brief.get('location'),  # Dict avec country, city
                unique_value_proposition=brief.get('competitive_advantage')
            )
            return {"seo_optimization": result}
        except Exception as e:
            logger.error("SEO agent failed", error=str(e))
            return {
                "seo_optimization": {
                    'error': str(e),
                    'fallback_mode': True,
                    'primary_keywords': [brief.get('industry_sector', 'business')],
                    'meta_title': brief.get('business_name', 'Business'),
                    'meta_description': business_description[:150] if business_description else 'Professional services'
                }
            }

    async def run_template_agent(self, state: AgentState) -> AgentState:
        """
        Exécute TemplateAgent legacy (à migrer Sprint 2+).
        """
        logger.info("Executing Template Agent (legacy)")
        
        brief = state['business_brief']
        try:
            # Adapter format pour agent legacy
            business_type = brief.get('industry_sector', 'general')
            result = await self.template_agent.run(
                business_type=business_type,
                theme_id=state.get('selected_theme_id'),
                theme_slug=state.get('selected_theme_slug')
            )
            return {"template_selection": result}
        except Exception as e:
            logger.error("Template agent failed", error=str(e))
            return {
                "template_selection": {
                    'error': str(e),
                    'fallback_mode': True
                }
            }

    async def run(self, orchestration_input: Dict[str, Any]):
        """
        Exécute le graphe d'orchestration.
        
        Args:
            orchestration_input: Dict contenant:
                - user_id: ID utilisateur
                - brief_id: ID brief généré
                - business_brief: Brief business format DC360
                - coaching_session_id: ID session coaching (optionnel)
                
        Returns:
            État final avec résultats tous sub-agents
        """
        logger.info(
            "Starting LangGraph orchestration (Sprint 2 - nouveaux sub-agents)...",
            user_id=orchestration_input.get('user_id'),
            brief_id=orchestration_input.get('brief_id'),
            business_name=orchestration_input.get('business_brief', {}).get('business_name')
        )
        
        try:
            # État initial aligné DC360
            initial_state = {
                "user_id": orchestration_input.get('user_id'),
                "brief_id": orchestration_input.get('brief_id'),
                "business_brief": orchestration_input.get('business_brief', {}),
                "market_research": {},
                "content_generation": {},
                "logo_creation": {},
                "seo_optimization": {},
                "template_selection": {},
                "selected_theme_id": orchestration_input.get('selected_theme_id'),
                "selected_theme_slug": orchestration_input.get('selected_theme_slug'),
                "overall_confidence": 0.0,
                "is_ready_for_website": False,
                "error": None
            }
            
            # Exécution workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Calcul confiance globale basé sur succès sub-agents
            agent_results = [
                final_state.get('market_research', {}),
                final_state.get('content_generation', {}),
                final_state.get('logo_creation', {}),
                final_state.get('seo_optimization', {}),
                final_state.get('template_selection', {})
            ]
            
            successful_agents = sum(
                1 for result in agent_results 
                if result and not result.get('error') and not result.get('fallback_mode')
            )
            total_agents = len(agent_results)
            
            final_state['overall_confidence'] = successful_agents / total_agents if total_agents > 0 else 0.0
            final_state['is_ready_for_website'] = successful_agents >= 3  # Au moins 3/5 agents réussis
            
            logger.info(
                "LangGraph orchestration completed successfully",
                brief_id=final_state.get('brief_id'),
                confidence=final_state['overall_confidence'],
                ready_for_website=final_state['is_ready_for_website'],
                successful_agents=f"{successful_agents}/{total_agents}"
            )
            
            return final_state
            
        except Exception as e:
            logger.error("Error during LangGraph orchestration", error=str(e), exc_info=True)
            raise OrchestratorException(
                message="Failed to execute the agentic workflow",
                details={"error": str(e)}
            )