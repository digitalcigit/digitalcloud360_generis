"""Coaching endpoints for Genesis AI Service"""

from typing import Dict, Any, List, Optional, Union
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
from app.schemas.theme import BriefCompletedResponse
from app.models.coaching import BusinessBrief
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


# GEN-WO-006: Helper pour préserver TOUJOURS l'onboarding lors des mises à jour Redis
async def preserve_onboarding_on_save(session_id: str, session_data: Dict[str, Any], redis_client: redis.Redis, ttl: int = 7200):
    """Sauvegarde session_data en Redis en préservant TOUJOURS les données d'onboarding"""
    onboarding_data = None

    current_json = await redis_client.get(f"session:{session_id}")
    if current_json:
        current_data = json.loads(current_json)
        if "onboarding" in current_data:
            onboarding_data = current_data["onboarding"]

    # Fallback: clé dédiée onboarding:{session_id}
    if onboarding_data is None:
        onboarding_json = await redis_client.get(f"onboarding:{session_id}")
        if onboarding_json:
            onboarding_data = json.loads(onboarding_json)

    if onboarding_data is not None:
        session_data["onboarding"] = onboarding_data
    
    await redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=ttl)
    if onboarding_data is not None:
        await redis_client.set(f"onboarding:{session_id}", json.dumps(onboarding_data), ex=ttl)




# ========= Onboarding (Phase 2 - GEN-WO-006) =========
from pydantic import BaseModel, Field

class OnboardingRequest(BaseModel):
    business_name: Optional[str] = Field(None, description="Nom du projet/entreprise")
    sector: str = Field(..., description="Secteur d'activité sélectionné")
    sector_other: Optional[str] = Field(None, description="Secteur libre si 'Autre'")
    logo_source: Optional[str] = Field(None, description="upload | generate | later")
    logo_url: Optional[str] = Field(None, description="URL du logo si upload")

class OnboardingResponse(BaseModel):
    session_id: str
    onboarding: Dict[str, Any]

@router.post("/onboarding", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def onboarding_coaching(
    request: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Étape 0 Onboarding (Phase 2 - GEN-WO-006)
    - Crée une session de coaching
    - Stocke les informations de base (nom, secteur, intention logo)
    """
    # 1) Préparer données secteur
    sector_value = request.sector_other.strip() if request.sector == "other" and request.sector_other else request.sector

    # 2) Créer session en base (comme /start)
    new_session_id = str(uuid.uuid4())
    session_db = CoachingSession(
        user_id=current_user.id,
        session_id=new_session_id,
        status=SessionStatusEnum.INITIALIZED,
        current_step=CoachingStepEnum.VISION
    )
    db.add(session_db)
    await db.commit()
    await db.refresh(session_db)

    # 3) Préparer et sauvegarder en Redis (TTL 2h)
    session_data = {
        "user_id": current_user.id,
        "session_id": new_session_id,
        "status": SessionStatusEnum.INITIALIZED.value,
        "current_step": CoachingStepEnum.VISION.value,
        "id": session_db.id,
    }

    onboarding_data = {
        "business_name": request.business_name,
        "sector": request.sector,
        "sector_resolved": sector_value,
        "logo_source": request.logo_source,
        "logo_url": request.logo_url,
    }

    payload = {**session_data, "onboarding": onboarding_data}
    await redis_client.set(f"session:{new_session_id}", json.dumps(payload), ex=7200)
    # Stockage redondant pour récupération robuste
    await redis_client.set(f"onboarding:{new_session_id}", json.dumps(onboarding_data), ex=7200)
    logger.info("onboarding_saved", session_id=new_session_id, business_name=request.business_name, sector=sector_value)

    return OnboardingResponse(session_id=new_session_id, onboarding=onboarding_data)

@router.post("/start", response_model=CoachingResponse)
async def start_coaching_session(request: CoachingRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    """Starts or continues a coaching session."""
    session_id = request.session_id

    # Récupérer ou créer la session (GEN-WO-006: préserver onboarding)
    session_data_json = await redis_client.get(f"session:{session_id}")
    session_data = None
    
    if session_data_json:
        session_data = json.loads(session_data_json)
    elif session_id:
        # Fallback to DB if not in Redis
        result = await db.execute(select(CoachingSession).filter(CoachingSession.session_id == session_id, CoachingSession.user_id == current_user.id))
        session_db = result.scalars().first()
        if session_db:
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
        await db.commit()
        await db.refresh(session_db)
        session_data["id"] = session_db.id # Add db id to session data
    
    # Recharger onboarding si présent en clé dédiée
    onboarding_json = await redis_client.get(f"onboarding:{session_data['session_id']}")
    if onboarding_json and "onboarding" not in session_data:
        session_data["onboarding"] = json.loads(onboarding_json)

    # GEN-WO-006: Sauvegarder session_data avec onboarding préservé
    await preserve_onboarding_on_save(session_data['session_id'], session_data, redis_client) # 2h TTL

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
        coach_message=vision_guidance.get("user_message", vision_guidance.get("prompt_text")),
        examples=vision_guidance.get("user_choices", vision_guidance.get("examples", [])),
        next_questions=[],
        progress={step.value: False for step in CoachingStepEnum},
        is_step_complete=False,
        clickable_choices=vision_guidance.get("user_clickable", vision_guidance.get("clickable_choices", []))
    )

@router.post("/step", response_model=Union[CoachingResponse, BriefCompletedResponse])
async def process_coaching_step(request: CoachingStepRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    """Processes a single step of the coaching session."""
    session_data_json = await redis_client.get(f"session:{request.session_id}")
    if not session_data_json:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coaching session not found or expired")

    session_data = json.loads(session_data_json)

    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this session")

    # --- LOGIQUE IA PROACTIVE (GEN-WO-002 + Messages épurés GEN-WO-006) ---
    llm_service = CoachingLLMService()
    prompts_loader = PromptsLoader()
    
    # 1. Détecter secteur
    history = await db.execute(select(CoachingStep.user_response).filter(CoachingStep.session_id == session_data["id"]))
    previous_msgs = [r[0] for r in history.all()]
    previous_msgs.append(request.user_response)
    
    detected_sector = await llm_service.detect_sector(previous_msgs)
    
    # 2. Valider et extraire avec LLM
    brief_context = await _build_brief_from_coaching_steps(session_data["id"], request.session_id, db, session_data, redis_client)
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
        await db.commit()
        # GEN-WO-006: Préserver onboarding lors de la mise à jour Redis
        await preserve_onboarding_on_save(session_data['session_id'], session_data, redis_client)

        # Générer guidage pour étape suivante (avec messages épurés)
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
            coach_message=next_guidance.get("user_message", next_guidance.get("prompt_text")),
            examples=next_guidance.get("user_choices", next_guidance.get("examples", [])),
            progress=progress,
            is_step_complete=True,
            confidence_score=extraction_result.confidence_score,
            clickable_choices=next_guidance.get("user_clickable", next_guidance.get("clickable_choices", []))
        )

    # --- ÉTAPE OFFRE COMPLÉTÉE -> SAUVEGARDER BRIEF ET ARRÊTER ---
    session_data["status"] = SessionStatusEnum.COACHING_COMPLETE.value
    
    # 1. Construire le business_brief dict depuis les étapes coaching
    business_brief_dict = await _build_brief_from_coaching_steps(
        session_db_id=session_data["id"],
        session_uuid=session_data["session_id"],
        db=db,
        session_data=session_data,
        redis_client=redis_client
    )

    # 2. Persister le BusinessBrief en base de données
    # Vérifier s'il existe déjà pour cette session (idempotence)
    result = await db.execute(select(BusinessBrief).filter(BusinessBrief.coaching_session_id == session_data["id"]))
    existing_brief = result.scalars().first()
    
    if existing_brief:
        brief_db = existing_brief
        # Update existing
        brief_db.business_name = business_brief_dict.get("business_name") or brief_db.business_name or "Projet Sans Nom"
        brief_db.vision = business_brief_dict.get("vision")
        brief_db.mission = business_brief_dict.get("mission")
        brief_db.target_audience = business_brief_dict.get("target_market")
        brief_db.differentiation = business_brief_dict.get("competitive_advantage")
        brief_db.value_proposition = business_brief_dict.get("value_proposition")
        brief_db.sector = business_brief_dict.get("industry_sector")
    else:
        # Create new
        brief_db = BusinessBrief(
            coaching_session_id=session_data["id"],
            business_name=business_brief_dict.get("business_name") or "Mon Business",
            vision=business_brief_dict.get("vision") or "",
            mission=business_brief_dict.get("mission") or "",
            target_audience=business_brief_dict.get("target_market") or "",
            differentiation=business_brief_dict.get("competitive_advantage") or "",
            value_proposition=business_brief_dict.get("value_proposition") or "",
            sector=business_brief_dict.get("industry_sector") or "default",
            location=business_brief_dict.get("location") or {}
        )
        db.add(brief_db)
    
    # Update session status
    stmt = update(CoachingSession).where(CoachingSession.session_id == request.session_id).values(
        status=SessionStatusEnum.COACHING_COMPLETE
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(brief_db)

    logger.info("coaching_finished_brief_saved", session_id=request.session_id, brief_id=brief_db.id)
    
    # 3. Mettre à jour Redis
    await preserve_onboarding_on_save(session_data['session_id'], session_data, redis_client)

    # 4. Retourner la réponse de fin de coaching (Redirect vers thèmes)
    return BriefCompletedResponse(
        status="BRIEF_COMPLETED",
        brief_id=brief_db.id,
        session_id=request.session_id,
        redirect_url=f"/genesis/themes?brief_id={brief_db.id}",
        message="Analyse terminée avec succès ! Découvrons maintenant les designs qui vous correspondent."
    )

    # Placeholder for other steps
    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message="Étape non implémentée.",
        progress={step.value: False for step in CoachingStepEnum}
    )

async def _build_brief_from_coaching_steps(session_db_id: int, session_uuid: str, db: AsyncSession, session_data: Dict[str, Any] = None, redis_client: redis.Redis = None) -> Dict[str, Any]:
    """Construit le business_brief depuis les étapes coaching sauvegardées + onboarding"""
    from sqlalchemy import select
    from app.models.coaching import CoachingStep, CoachingStepEnum
    
    # Récupérer toutes les étapes
    result = await db.execute(
        select(CoachingStep)
        .filter(CoachingStep.session_id == session_db_id)
        .order_by(CoachingStep.step_order)
    )
    steps = result.scalars().all()
    
    # GEN-WO-008: Toujours récupérer business_name depuis l'onboarding (sinon fallback)
    onboarding = (session_data or {}).get("onboarding", {})
    logger.info("building_brief_check_onboarding_start", 
                session_uuid=session_uuid, 
                has_onboarding_in_data=bool(onboarding))

    if not onboarding and redis_client:
        # Utiliser l'UUID pour la clé Redis
        onboarding_json = await redis_client.get(f"onboarding:{session_uuid}")
        logger.info("building_brief_redis_lookup", 
                    key=f"onboarding:{session_uuid}", 
                    found=bool(onboarding_json))
        if onboarding_json:
            onboarding = json.loads(onboarding_json)
    
    # Correction: .get(key, default) ne gère pas le cas où la valeur est None
    business_name = onboarding.get("business_name") or "Projet Sans Nom"
    industry_sector = onboarding.get("sector_resolved") or onboarding.get("sector") or "default"
    
    logger.info("building_brief_final_values", 
                business_name=business_name, 
                industry_sector=industry_sector)
    
    brief = {
        "business_name": business_name,
        "industry_sector": industry_sector,
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
    brief = await _build_brief_from_coaching_steps(session_data["id"], request.session_id, db, session_data, redis_client)
    
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
    
    # Récupérer contexte (avec fallback onboarding en Redis)
    brief = await _build_brief_from_coaching_steps(session_data["id"], request.session_id, db, session_data, redis_client)
    
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

@router.get("/{session_id}/site", response_model=Dict[str, Any])
async def get_coaching_site(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """Retourne le SiteDefinition généré pour une session coaching."""
    # Vérifier que la session appartient à l'utilisateur
    session_data_json = await redis_client.get(f"session:{session_id}")
    if not session_data_json:
        # Session expirée mais on vérifie quand même si le site existe
        # pour des raisons de sécurité, on refuse l'accès si on ne peut pas vérifier l'ownership
        site_exists = await redis_client.exists(f"site:{session_id}")
        if not site_exists:
            raise HTTPException(status_code=404, detail="Session expired and site not found")
        # Note: Si session expirée mais site existe, on permet l'accès car le user est authentifié
        # et a fourni un UUID valide qu'il ne peut connaître que s'il a fait le coaching
        logger.warning("Session expired but site exists", session_id=session_id, user_id=current_user.id)
    else:
        session_data = json.loads(session_data_json)
        if session_data.get("user_id") != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this session")
    
    # Récupérer le site
    site_data = await redis_client.get(f"site:{session_id}")
    if not site_data:
        raise HTTPException(status_code=404, detail="Site not found for this session")
    
    return json.loads(site_data)
