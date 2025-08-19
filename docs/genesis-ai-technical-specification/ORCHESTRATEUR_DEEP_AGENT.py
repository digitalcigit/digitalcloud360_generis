from langgraph import StateGraph, CompiledGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import asyncio
import json
from datetime import datetime
import structlog

from app.config.settings import settings
from app.core.deep_agents.sub_agents.research import ResearchSubAgent
from app.core.deep_agents.sub_agents.content import ContentSubAgent
from app.core.deep_agents.sub_agents.logo import LogoSubAgent
from app.core.deep_agents.sub_agents.seo import SEOSubAgent
from app.core.deep_agents.sub_agents.template import TemplateSubAgent
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.coaching.methodology import CoachingMethodology
from app.schemas.coaching import CoachingStep, BusinessBrief
from app.utils.exceptions import CoachingException, OrchestrationException

logger = structlog.get_logger()

class GenesisAIState(TypedDict):
    """État centralisé Deep Agent - Toutes interactions coaching"""
    session_id: str
    user_id: int
    user_profile: Dict[str, Any]
    current_step: str  # vision|mission|clientele|differentiation|offre|synthesis
    coaching_plan: List[str]
    business_brief: Dict[str, Any]
    sub_agents_results: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    coaching_confidence: float
    retry_count: int
    step_completion: Dict[str, bool]
    cultural_context: Dict[str, Any]
    sector_context: Dict[str, Any]

class GenesisDeepAgentOrchestrator:
    """Orchestrateur principal Deep Agent Genesis AI
    
    Coordonne 5 sous-agents spécialisés pour coaching entrepreneurial structurant
    avec architecture LangGraph pour raisonnement long terme et mémoire persistante.
    """
    
    def __init__(self):
        """Initialisation orchestrateur avec tous composants"""
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.7,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Virtual File System pour persistance session
        self.virtual_fs = RedisVirtualFileSystem()
        
        # Méthodologie coaching structurant
        self.coaching_methodology = CoachingMethodology()
        
        # Sub-Agents spécialisés
        self.sub_agents = {
            'research': ResearchSubAgent(),
            'content': ContentSubAgent(),
            'logo': LogoSubAgent(),
            'seo': SEOSubAgent(),
            'template': TemplateSubAgent()
        }
        
        # Construction workflow LangGraph
        self.workflow = self._build_coaching_workflow()
        
        logger.info("Genesis Deep Agent Orchestrator initialized")
    
    def _build_coaching_workflow(self) -> CompiledGraph:
        """Construction workflow LangGraph pour coaching entrepreneurial complet"""
        
        workflow = StateGraph(GenesisAIState)
        
        # NŒUDS COACHING SÉQUENTIELS (5 ÉTAPES)
        workflow.add_node("coaching_initialization", self._initialize_coaching_session)
        workflow.add_node("vision_coaching", self._coach_vision_step)
        workflow.add_node("mission_coaching", self._coach_mission_step)  
        workflow.add_node("clientele_coaching", self._coach_clientele_step)
        workflow.add_node("differentiation_coaching", self._coach_differentiation_step)
        workflow.add_node("offre_coaching", self._coach_offre_step)
        workflow.add_node("coaching_validation", self._validate_coaching_completion)
        
        # NŒUDS SUB-AGENTS (EXÉCUTION PARALLÈLE)
        workflow.add_node("research_agent", self._execute_research_agent)
        workflow.add_node("content_agent", self._execute_content_agent)
        workflow.add_node("logo_agent", self._execute_logo_agent)
        workflow.add_node("seo_agent", self._execute_seo_agent)
        workflow.add_node("template_agent", self._execute_template_agent)
        
        # NŒUDS SYNTHÈSE & FINALISATION
        workflow.add_node("parallel_orchestration", self._orchestrate_sub_agents)
        workflow.add_node("business_brief_synthesis", self._synthesize_business_brief)
        workflow.add_node("session_finalization", self._finalize_coaching_session)
        
        # ROUTAGE CONDITIONNEL INTELLIGENT
        
        # Point d'entrée
        workflow.set_entry_point("coaching_initialization")
        
        # Routage coaching séquentiel avec conditions
        workflow.add_conditional_edges(
            "coaching_initialization",
            self._route_coaching_step,
            {
                "vision": "vision_coaching",
                "mission": "mission_coaching",
                "clientele": "clientele_coaching", 
                "differentiation": "differentiation_coaching",
                "offre": "offre_coaching",
                "validation": "coaching_validation"
            }
        )
        
        # Routage après chaque étape coaching
        for step in ["vision", "mission", "clientele", "differentiation", "offre"]:
            workflow.add_conditional_edges(
                f"{step}_coaching",
                self._route_next_coaching_step,
                {
                    "next_step": self._get_next_coaching_node(step),
                    "retry_step": f"{step}_coaching",
                    "validation": "coaching_validation"
                }
            )
        
        # Routage vers sub-agents après validation
        workflow.add_conditional_edges(
            "coaching_validation",
            self._route_to_sub_agents,
            {
                "sub_agents": "parallel_orchestration",
                "retry_coaching": "vision_coaching"
            }
        )
        
        # Routage final
        workflow.add_edge("parallel_orchestration", "business_brief_synthesis")
        workflow.add_edge("business_brief_synthesis", "session_finalization")
        workflow.add_edge("session_finalization", END)
        
        return workflow.compile()
    
    async def start_coaching_session(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Point d'entrée principal orchestration coaching entrepreneurial"""
        
        logger.info(
            "Starting coaching session",
            user_id=user_data.get('user_id'),
            session_id=user_data.get('session_id')
        )
        
        # État initial Deep Agent
        initial_state = GenesisAIState(
            session_id=user_data['session_id'],
            user_id=user_data['user_id'],
            user_profile=user_data['user_profile'],
            current_step='vision',
            coaching_plan=self._generate_coaching_plan(user_data['user_profile']),
            business_brief={},
            sub_agents_results={},
            conversation_history=[],
            coaching_confidence=0.0,
            retry_count=0,
            step_completion={
                'vision': False,
                'mission': False, 
                'clientele': False,
                'differentiation': False,
                'offre': False
            },
            cultural_context=self._extract_cultural_context(user_data['user_profile']),
            sector_context={}
        )
        
        try:
            # Exécution workflow Deep Agent complet
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Persistance session finale
            await self.virtual_fs.save_coaching_session(
                session_id=final_state['session_id'],
                state=final_state
            )
            
            logger.info(
                "Coaching session completed successfully",
                session_id=final_state['session_id'],
                confidence=final_state['coaching_confidence']
            )
            
            return {
                'success': True,
                'session_id': final_state['session_id'],
                'business_brief': final_state['business_brief'],
                'coaching_confidence': final_state['coaching_confidence'],
                'sub_agents_results': final_state['sub_agents_results'],
                'conversation_summary': self._generate_conversation_summary(final_state)
            }
            
        except Exception as e:
            logger.error(
                "Coaching session failed", 
                error=str(e),
                session_id=user_data.get('session_id')
            )
            raise OrchestrationException(
                message="Échec orchestration session coaching",
                details={"error": str(e)}
            )
    
    async def _initialize_coaching_session(self, state: GenesisAIState) -> GenesisAIState:
        """Initialisation session coaching avec analyse profil utilisateur"""
        
        logger.info("Initializing coaching session", session_id=state['session_id'])
        
        # Analyse profil utilisateur pour personnalisation
        user_profile_analysis = await self._analyze_user_profile(state['user_profile'])
        
        # Détermination secteur d'activité si disponible
        if 'sector' in state['user_profile']:
            sector_context = await self.coaching_methodology.get_sector_context(
                state['user_profile']['sector']
            )
            state['sector_context'] = sector_context
        
        # Génération plan coaching personnalisé
        state['coaching_plan'] = await self._generate_personalized_coaching_plan(
            state['user_profile'],
            user_profile_analysis
        )
        
        # Message d'accueil coaching personnalisé
        welcome_message = await self._generate_welcome_message(state)
        state['conversation_history'].append({
            'role': 'assistant',
            'message': welcome_message,
            'timestamp': datetime.utcnow().isoformat(),
            'step': 'initialization'
        })
        
        return state
    
    # Méthodes coaching par étape
    async def _coach_vision_step(self, state: GenesisAIState) -> GenesisAIState:
        """Coaching étape Vision avec exemples sectoriels"""
        return await self._execute_coaching_step(state, 'vision')
    
    async def _coach_mission_step(self, state: GenesisAIState) -> GenesisAIState:
        """Coaching étape Mission avec reformulation intelligente"""
        return await self._execute_coaching_step(state, 'mission')
    
    async def _coach_clientele_step(self, state: GenesisAIState) -> GenesisAIState:
        """Coaching étape Clientèle cible avec personas"""
        return await self._execute_coaching_step(state, 'clientele')
    
    async def _coach_differentiation_step(self, state: GenesisAIState) -> GenesisAIState:
        """Coaching étape Différenciation concurrentielle"""
        return await self._execute_coaching_step(state, 'differentiation')
    
    async def _coach_offre_step(self, state: GenesisAIState) -> GenesisAIState:
        """Coaching étape Offre de valeur finale"""
        return await self._execute_coaching_step(state, 'offre')
    
    async def _execute_coaching_step(self, state: GenesisAIState, step: str) -> GenesisAIState:
        """Logique générique exécution étape coaching avec méthodologie"""
        
        logger.info(f"Executing {step} coaching step", session_id=state['session_id'])
        
        # Récupération méthodologie et exemples pour cette étape
        coaching_guidance = await self.coaching_methodology.get_step_guidance(
            step=step,
            sector_context=state['sector_context'],
            cultural_context=state['cultural_context'],
            user_profile=state['user_profile']
        )
        
        # Construction prompt coaching personnalisé
        coaching_prompt = await self._build_coaching_prompt(
            state=state,
            step=step,
            guidance=coaching_guidance
        )
        
        # Exécution coaching LLM
        coaching_response = await self.llm.ainvoke([
            SystemMessage(content=coaching_guidance['system_prompt']),
            HumanMessage(content=coaching_prompt)
        ])
        
        # Validation et structuration réponse
        structured_response = await self._validate_coaching_response(
            response=coaching_response.content,
            step=step,
            expected_format=coaching_guidance['expected_format']
        )
        
        # Mise à jour état
        state['business_brief'][step] = structured_response['content']
        state['step_completion'][step] = structured_response['is_complete']
        state['current_step'] = step
        
        # Ajout conversation history
        state['conversation_history'].append({
            'role': 'assistant',
            'message': structured_response['coach_message'],
            'timestamp': datetime.utcnow().isoformat(),
            'step': step,
            'confidence': structured_response['confidence']
        })
        
        return state
