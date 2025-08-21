import structlog
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

from app.core.agents.research import ResearchAgent
from app.core.agents.content import ContentAgent
from app.core.agents.logo import LogoAgent
from app.core.agents.seo import SeoAgent
from app.core.agents.template import TemplateAgent
from app.utils.exceptions import OrchestratorException

logger = structlog.get_logger(__name__)

# Define the state for the graph
class AgentState(TypedDict):
    business_brief: dict
    research_data: dict
    content: dict
    logo: dict
    seo_data: dict
    template: dict
    error: str = None

class LangGraphOrchestrator:
    """
    Orchestrateur basé sur LangGraph pour coordonner les sub-agents.
    """
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
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

        # Define the execution flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("research", "logo")
        workflow.add_edge("research", "seo")
        workflow.add_edge("research", "template")
        
        # All parallel tasks lead to the end
        workflow.add_edge("content", END)
        workflow.add_edge("logo", END)
        workflow.add_edge("seo", END)
        workflow.add_edge("template", END)

        # Compile the graph
        return workflow.compile()

    async def run_research_agent(self, state: AgentState) -> AgentState:
        logger.info("Executing Research Agent")
        brief = state['business_brief']
        result = await self.research_agent.run(brief['company_description'], brief['market_focus'])
        return {"research_data": result}

    async def run_content_agent(self, state: AgentState) -> AgentState:
        logger.info("Executing Content Agent")
        result = await self.content_agent.run(state['business_brief'], state['research_data'])
        return {"content": result}

    async def run_logo_agent(self, state: AgentState) -> AgentState:
        logger.info("Executing Logo Agent")
        brief = state['business_brief']
        result = await self.logo_agent.run(brief['company_name'], brief.get('slogan'))
        return {"logo": result}

    async def run_seo_agent(self, state: AgentState) -> AgentState:
        logger.info("Executing SEO Agent")
        brief = state['business_brief']
        result = await self.seo_agent.run(brief['company_description'], brief['market_focus'])
        return {"seo_data": result}

    async def run_template_agent(self, state: AgentState) -> AgentState:
        logger.info("Executing Template Agent")
        brief = state['business_brief']
        result = await self.template_agent.run(brief['business_type'])
        return {"template": result}

    async def run(self, business_brief: dict):
        """Exécute le graphe d'orchestration."""
        logger.info("Starting LangGraph orchestration...", initial_brief=business_brief)
        try:
            initial_state = {"business_brief": business_brief}
            final_state = await self.graph.ainvoke(initial_state)
            logger.info("LangGraph orchestration completed successfully.")
            return final_state
        except Exception as e:
            logger.error("Error during LangGraph orchestration", error=str(e))
            raise OrchestratorException(
                "ORCHESTRATION_ERROR",
                "Failed to execute the agentic workflow.",
                details=str(e)
            )