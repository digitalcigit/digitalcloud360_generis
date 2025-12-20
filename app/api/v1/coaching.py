"""Coaching endpoints for Genesis AI Service"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import structlog
import uuid
import json
import redis.asyncio as redis

from app.config.database import get_db
from app.api.v1.dependencies import get_redis_client
from app.models.user import User
from app.models.coaching import CoachingSession, CoachingStep, CoachingStepEnum, SessionStatusEnum
from app.schemas.coaching import (
    CoachingRequest, 
    CoachingStepRequest, 
    CoachingResponse,
    CoachingHelpResponse,
    ReformulateRequest,
    ReformulateResponse,
    GenerateProposalsResponse
)
from app.services.user_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

# Imports for Site Generation (GEN-WO-002)
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData
from app.services.coaching_llm_service import CoachingLLMService
from app.services.prompts_loader import PromptsLoader

router = APIRouter()
logger = structlog.get_logger()

@router.post("/start", response_model=CoachingResponse)
async def start_coaching_session(request: CoachingRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    """Starts or continues a coaching session."""
    session_id = request.session_id
    session_data = None

    if session_id:
        session_data_json = await redis_client.get(f"session:{session_id}")
        if session_data_json:
            session_data = json.loads(session_data_json)
        else:
            # Fallback to DB if not in Redis
            result = await db.execute(select(CoachingSession).filter(CoachingSession.session_id == session_id, CoachingSession.user_id == current_user.id))
            session_db = result.scalars().first()
            if not session_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coaching session not found")
            session_data = {
                "user_id": session_db.user_id,
                "session_id": session_db.session_id,
                "status": session_db.status.value,
                "current_step": session_db.current_step.value,
                "id": session_db.id
            }
    
    if not session_data:
        new_session_id = str(uuid.uuid4())
        session_data = {
            "user_id": current_user.id,
            "session_id": new_session_id,
            "status": SessionStatusEnum.INITIALIZED.value,
            "current_step": CoachingStepEnum.VISION.value
        }
        # Also save to DB for long term
        session_db = CoachingSession(
            user_id=current_user.id,
            session_id=new_session_id,
            status=SessionStatusEnum.INITIALIZED,
            current_step=CoachingStepEnum.VISION
        )
        db.add(session_db)
        await db.flush()
        await db.refresh(session_db)
        session_data["id"] = session_db.id # Add db id to session data

    await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200) # 2h TTL

    # Load first step guidance (VISION)
    prompts_loader = PromptsLoader()
    vision_guidance = prompts_loader.get_step_prompt(
        step=CoachingStepEnum.VISION.value,
        sector="default", # Initial
        user_name=current_user.name or "Entrepreneur"
    )

    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message=vision_guidance["prompt_text"],
        examples=vision_guidance["examples"],
        next_questions=[],
        progress={step.value: False for step in CoachingStepEnum},
        is_step_complete=False,
        clickable_choices=vision_guidance.get("clickable_choices", [])
    )

    # Placeholder for other steps
    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message="Étape non implémentée.",
        progress={step.value: False for step in CoachingStepEnum}
    )

@router.post("/step", response_model=CoachingResponse)
async def process_coaching_step(request: CoachingStepRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    """Processes a single step of the coaching session."""
    session_data_json = await redis_client.get(f"session:{request.session_id}")
    if not session_data_json:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coaching session not found or expired")

    session_data = json.loads(session_data_json)

    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this session")

    # --- LOGIQUE IA PROACTIVE (GEN-WO-002) ---
    llm_service = CoachingLLMService()
    prompts_loader = PromptsLoader()
    
    # 1. Détecter secteur
    history = await db.execute(select(CoachingStep.user_response).filter(CoachingStep.session_id == session_data["id"]))
    previous_msgs = [r[0] for r in history.all()]
    previous_msgs.append(request.user_response)
    
    detected_sector = await llm_service.detect_sector(previous_msgs)
    
    # 2. Valider et extraire avec LLM
    brief_context = await _build_brief_from_coaching_steps(session_data["id"], db)
    extraction_result = await llm_service.extract_and_validate(
        step=session_data["current_step"],
        user_response=request.user_response,
        sector=detected_sector,
        context=brief_context
    )
    
    # 3. Traitement selon validation
    if not extraction_result.is_valid:
        # Rester sur la même étape car réponse insuffisante
        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=extraction_result.clarification_question or "Pouvez-vous préciser votre pensée ?",
            examples=[],
            next_questions=[],
            progress={step.value: False for step in CoachingStepEnum},
            is_step_complete=False,
            confidence_score=extraction_result.confidence_score
        )

    # Si valide, on sauvegarde et on passe à l'étape suivante
    current_step_enum = CoachingStepEnum(session_data["current_step"])
    
    # Sauvegarde SQL record
    new_step_record = CoachingStep(
        session_id=session_data["id"],
        step_name=current_step_enum,
        step_order=len(previous_msgs),
        user_response=request.user_response,
        coach_message=extraction_result.reformulated_response
    )
    db.add(new_step_record)

    # Déterminer étape suivante
    steps_order = [
        CoachingStepEnum.VISION, 
        CoachingStepEnum.MISSION, 
        CoachingStepEnum.CLIENTELE, 
        CoachingStepEnum.DIFFERENTIATION, 
        CoachingStepEnum.OFFRE
    ]
    current_idx = steps_order.index(current_step_enum)
    
    if current_idx < len(steps_order) - 1:
        # Pas encore la fin
        next_step = steps_order[current_idx + 1]
        session_data["current_step"] = next_step.value
        
        # Update session in DB
        stmt = update(CoachingSession).where(CoachingSession.session_id == request.session_id).values(
            current_step=session_data["current_step"]
        )
        await db.execute(stmt)
        await db.flush()
        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        # Générer guidage pour étape suivante
        next_guidance = prompts_loader.get_step_prompt(
            step=session_data["current_step"],
            sector=detected_sector,
            user_name=current_user.name or "Entrepreneur",
            validated_previous=extraction_result.reformulated_response
        )

        progress = {step.value: False for step in CoachingStepEnum}
        for i in range(current_idx + 2): # +2 because index starts at 0 and we want to show current as partial
            if i < len(steps_order):
                progress[steps_order[i].value] = (i <= current_idx)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=next_guidance["prompt_text"],
            examples=next_guidance["examples"],
            progress=progress,
            is_step_complete=True,
            confidence_score=extraction_result.confidence_score,
            clickable_choices=next_guidance.get("clickable_choices", [])
        )

    # --- ÉTAPE OFFRE COMPLÉTÉE -> DÉCLENCHER GÉNÉRATION SITE ---
    session_data["status"] = SessionStatusEnum.COMPLETED.value
    
    # Update session in DB
    stmt = update(CoachingSession).where(CoachingSession.session_id == request.session_id).values(status=SessionStatusEnum.COMPLETED)
    await db.execute(stmt)
    await db.flush()

    # ============ NOUVEAU: Trigger Site Generation (GEN-WO-002) ============
    logger.info("triggering_site_generation", session_id=request.session_id)
    
    # 1. Construire le business_brief depuis les étapes coaching
    business_brief_dict = await _build_brief_from_coaching_steps(
        session_id=session_data["id"],
        db=db
    )
    
    # 2. Exécuter l'orchestrateur LangGraph
    orchestrator = LangGraphOrchestrator()
    orchestration_result = await orchestrator.run({
        "user_id": current_user.id,
        "brief_id": request.session_id,
        "business_brief": business_brief_dict
    })
    
    # 3. Transformer en SiteDefinition
    transformer = BriefToSiteTransformer()
    
    # Créer un objet brief data enrichi
    enriched_brief = BusinessBriefData(
        business_name=business_brief_dict.get("business_name", "Mon Business"),
        sector=business_brief_dict.get("industry_sector", "default"),
        vision=business_brief_dict.get("vision", ""),
        mission=business_brief_dict.get("mission", ""),
        target_audience=business_brief_dict.get("target_market", ""),
        differentiation=business_brief_dict.get("competitive_advantage", ""),
        value_proposition=business_brief_dict.get("value_proposition", ""),
        location=business_brief_dict.get("location", {}),
        content_generation=orchestration_result.get("content_generation", {}),
        logo_creation=orchestration_result.get("logo_creation", {}),
        seo_optimization=orchestration_result.get("seo_optimization", {})
    )
    
    site_definition = transformer.transform(enriched_brief)
        
    # 4. Sauvegarder en Redis pour le frontend
    await redis_client.set(
        f"site:{request.session_id}", 
        json.dumps(site_definition), 
        ex=86400  # 24h
    )
    
    # Prepare the final response
    coach_message = "Félicitations ! Vous avez terminé votre session de coaching Genesis AI. Votre site personnalisé a été généré !"
    
    progress = {step.value: True for step in CoachingStepEnum}

    await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message=coach_message,
        examples=[],
        next_questions=[],
        progress=progress,
        is_step_complete=True,
        site_data=site_definition
    )

    # Placeholder for other steps
    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message="Étape non implémentée.",
        progress={step.value: False for step in CoachingStepEnum}
    )

async def _build_brief_from_coaching_steps(session_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Construit le business_brief depuis les étapes coaching sauvegardées"""
    from sqlalchemy import select
    from app.models.coaching import CoachingStep, CoachingStepEnum
    
    # Récupérer toutes les étapes
    result = await db.execute(
        select(CoachingStep)
        .filter(CoachingStep.session_id == session_id)
        .order_by(CoachingStep.step_order)
    )
    steps = result.scalars().all()
    
    brief = {
        "business_name": "Projet Sans Nom", # Fallback
        "industry_sector": "default",
        "vision": "",
        "mission": "",
        "target_market": "",
        "competitive_advantage": "",
        "value_proposition": "",
        "services": [],
        "location": {"country": "Sénégal", "city": "Dakar"}
    }
    
    for step in steps:
        if step.step_name == CoachingStepEnum.VISION:
            brief["vision"] = step.user_response
        elif step.step_name == CoachingStepEnum.MISSION:
            brief["mission"] = step.user_response
        elif step.step_name == CoachingStepEnum.CLIENTELE:
            brief["target_market"] = step.user_response
        elif step.step_name == CoachingStepEnum.DIFFERENTIATION:
            brief["competitive_advantage"] = step.user_response
        elif step.step_name == CoachingStepEnum.OFFRE:
            brief["value_proposition"] = step.user_response
            
    return brief

# --- SPRINT 2: NOUVEAUX ENDPOINTS NIVEAU ARGENT ---

@router.post("/help", response_model=CoachingHelpResponse)
async def get_coaching_help(
    request: CoachingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Génère des questions socratiques pour débloquer l'utilisateur"""
    session_data_json = await redis_client.get(f"session:{request.session_id}")
    if not session_data_json:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    session_data = json.loads(session_data_json)

    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this session")
    
    llm_service = CoachingLLMService()
    
    # Récupérer contexte
    brief = await _build_brief_from_coaching_steps(session_data["id"], db)
    
    help_result = await llm_service.get_socratic_help(
        step=session_data["current_step"],
        brief=brief,
        sector=brief.get("industry_sector", "default")
    )
    
    return CoachingHelpResponse(
        session_id=request.session_id,
        current_step=session_data["current_step"],
        socratic_questions=help_result["questions"],
        suggestion=help_result["suggestion"]
    )

@router.post("/reformulate", response_model=ReformulateResponse)
async def reformulate_text(
    request: ReformulateRequest,
    current_user: User = Depends(get_current_user)
):
    """Reformule en temps réel une réponse utilisateur"""
    # OPTIMISATION (GEN-WO-002): Short-circuit si texte trop court
    if len(request.text) < 30:
        return ReformulateResponse(
            original_text=request.text,
            reformulated_text=request.text,
            is_better=False,
            suggestions=["Continuez à écrire pour que je puisse vous aider à reformuler."]
        )
    
    llm_service = CoachingLLMService()
    result = await llm_service.reformulate(
        text=request.text,
        step=request.target_step.value if request.target_step else "vision"
    )
    
    return result

@router.post("/generate-proposals", response_model=GenerateProposalsResponse)
async def generate_proposals(
    request: CoachingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Mode 'Je ne sais pas' : génère 3 propositions basées sur le contexte"""
    session_data_json = await redis_client.get(f"session:{request.session_id}")
    if not session_data_json:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    session_data = json.loads(session_data_json)

    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this session")
    
    llm_service = CoachingLLMService()
    
    # Récupérer contexte
    brief = await _build_brief_from_coaching_steps(session_data["id"], db)
    
    proposals_data = await llm_service.generate_proposals(
        step=session_data["current_step"],
        brief=brief,
        sector=brief.get("industry_sector", "default")
    )
    
    return GenerateProposalsResponse(
        session_id=request.session_id,
        step=session_data["current_step"],
        proposals=proposals_data["proposals"],
        coach_advice=proposals_data["coach_advice"]
    )
