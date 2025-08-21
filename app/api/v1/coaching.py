"""Coaching endpoints for Genesis AI Service"""

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
from app.schemas.coaching import CoachingRequest, CoachingStepRequest, CoachingResponse
from app.services.user_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

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

    if session_data["current_step"] == CoachingStepEnum.VISION.value:
        coach_message = "Bienvenue dans votre session de coaching Genesis AI. Commençons par définir la vision de votre entreprise. Quelle est l'ambition à long terme de votre projet ? Quel impact souhaitez-vous avoir ?"
        examples = [
            "Devenir le leader de la livraison de repas éco-responsables en Europe.",
            "Créer une plateforme d'éducation en ligne accessible à tous, partout dans le monde.",
            "Révolutionner le secteur de la mode avec des vêtements 100% recyclés et recyclables."
        ]
        next_questions = [
            "Quelle est la raison d'être de votre entreprise ?",
            "Quelles valeurs fondamentales guideront vos décisions ?"
        ]

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=examples,
            next_questions=next_questions,
            progress={step.value: False for step in CoachingStepEnum},
            is_step_complete=False
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

    # Logic to handle the response for the current step and transition to the next
    if session_data["current_step"] == CoachingStepEnum.VISION.value:
        # Save the user's response for the VISION step to DB
        vision_step = CoachingStep(
            session_id=session_data["id"],
            step_name=CoachingStepEnum.VISION,
            step_order=1,
            user_response=request.user_response,
            coach_message="Feedback pour la vision à implémenter."
        )
        db.add(vision_step)
        
        # Transition to the next step
        session_data["current_step"] = CoachingStepEnum.MISSION.value
        
        # Update session in DB
        stmt = update(CoachingSession).where(CoachingSession.session_id == request.session_id).values(current_step=CoachingStepEnum.MISSION)
        await db.execute(stmt)
        await db.flush()

        # Prepare the response for the MISSION step
        coach_message = "Excellente vision ! Maintenant, clarifions votre MISSION. Quelle est la raison d'être de votre entreprise ?"
        examples = [
            "Nourrir les familles avec une cuisine authentique.",
            "Révéler la beauté unique de chaque client.",
            "Faciliter l'accès à des produits de qualité."
        ]
        next_questions = [
            "Comment allez-vous servir vos clients au quotidien ?",
            "Quels sont vos engagements fondamentaux ?"
        ]
        
        progress = {step.value: False for step in CoachingStepEnum}
        progress[CoachingStepEnum.VISION] = True

        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=examples,
            next_questions=next_questions,
            progress=progress,
            is_step_complete=False
        )

    elif session.current_step == CoachingStepEnum.MISSION:
        # Save the user's response for the MISSION step
        mission_step = CoachingStep(
            session_id=session.id,
            step_name=CoachingStepEnum.MISSION,
            user_response=request.user_response,
            coach_feedback="Feedback pour la mission à implémenter."
        )
        db.add(mission_step)
        
        # Transition to the next step
        session.current_step = CoachingStepEnum.CLIENTELE
        await db.flush()
        await db.refresh(session)

        # Prepare the response for the CLIENTELE step
        coach_message = "Parfait ! Maintenant, parlons de vos CLIENTS. Qui voulez-vous servir en priorité ?"
        examples = [
            "Les femmes actives de 25-45 ans qui valorisent la beauté naturelle.",
            "Les jeunes étudiants qui cherchent des coiffures tendances et abordables.",
            "Les mères de famille qui souhaitent des moments de détente."
        ]
        next_questions = [
            "Quels sont leurs principaux problèmes au quotidien ?",
            "Où les trouvez-vous ? Comment pouvez-vous les atteindre ?"
        ]
        
        progress = {step.value: False for step in CoachingStepEnum}
        progress[CoachingStepEnum.VISION] = True
        progress[CoachingStepEnum.MISSION] = True

        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=examples,
            next_questions=next_questions,
            progress=progress,
            is_step_complete=False
        )

    elif session.current_step == CoachingStepEnum.CLIENTELE:
        # Save the user's response for the CLIENTELE step
        clientele_step = CoachingStep(
            session_id=session.id,
            step_name=CoachingStepEnum.CLIENTELE,
            user_response=request.user_response,
            coach_feedback="Feedback pour la clientèle à implémenter."
        )
        db.add(clientele_step)
        
        # Transition to the next step
        session.current_step = CoachingStepEnum.DIFFERENTIATION
        await db.flush()
        await db.refresh(session)

        # Prepare the response for the DIFFERENTIATION step
        coach_message = "Très bien. Comment vous différenciez-vous de la concurrence ? Quelle est votre proposition de valeur unique ?"
        examples = [
            "Nous sommes les seuls à proposer des produits 100% bio et faits main.",
            "Notre service client est disponible 24/7 avec une réponse garantie en moins de 5 minutes.",
            "Notre technologie de personnalisation de produits est brevetée."
        ]
        next_questions = [
            "Qu'est-ce que vos concurrents font bien ?",
            "Qu'est-ce que vous pouvez faire de mieux ou différemment ?"
        ]
        
        progress = {step.value: False for step in CoachingStepEnum}
        progress[CoachingStepEnum.VISION] = True
        progress[CoachingStepEnum.MISSION] = True
        progress[CoachingStepEnum.CLIENTELE] = True

        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=examples,
            next_questions=next_questions,
            progress=progress,
            is_step_complete=False
        )

    elif session.current_step == CoachingStepEnum.DIFFERENTIATION:
        # Save the user's response for the DIFFERENTIATION step
        diff_step = CoachingStep(
            session_id=session.id,
            step_name=CoachingStepEnum.DIFFERENTIATION,
            user_response=request.user_response,
            coach_feedback="Feedback pour la différenciation à implémenter."
        )
        db.add(diff_step)
        
        # Transition to the next step
        session.current_step = CoachingStepEnum.OFFRE
        await db.flush()
        await db.refresh(session)

        # Prepare the response for the OFFRE step
        coach_message = "Excellent point. Finalement, décrivons votre OFFRE. Quels produits ou services spécifiques proposez-vous ?"
        examples = [
            "Un abonnement mensuel à une box de produits de beauté bio.",
            "Des cours de cuisine en ligne avec un chef étoilé.",
            "Un service de personal shopping sur mesure."
        ]
        next_questions = [
            "Quels sont les tarifs de vos offres ?",
            "Comment vos clients peuvent-ils acheter vos produits ou services ?"
        ]
        
        progress = {step.value: False for step in CoachingStepEnum}
        progress[CoachingStepEnum.VISION] = True
        progress[CoachingStepEnum.MISSION] = True
        progress[CoachingStepEnum.CLIENTELE] = True
        progress[CoachingStepEnum.DIFFERENTIATION] = True

        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=examples,
            next_questions=next_questions,
            progress=progress,
            is_step_complete=False
        )

    elif session.current_step == CoachingStepEnum.OFFRE:
        # Save the user's response for the OFFRE step
        offre_step = CoachingStep(
            session_id=session.id,
            step_name=CoachingStepEnum.OFFRE,
            user_response=request.user_response,
            coach_feedback="Feedback pour l'offre à implémenter."
        )
        db.add(offre_step)
        
        # Mark the session as complete
        session.status = SessionStatusEnum.COMPLETED
        await db.flush()
        await db.refresh(session)

        # Prepare the final response
        coach_message = "Félicitations ! Vous avez terminé votre session de coaching Genesis AI. Votre business plan est maintenant bien défini."
        
        progress = {step.value: True for step in CoachingStepEnum}

        await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)

        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=session_data["current_step"],
            coach_message=coach_message,
            examples=[],
            next_questions=[],
            progress=progress,
            is_step_complete=True
        )

    # Placeholder for other steps
    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=session_data["current_step"],
        coach_message="Étape non implémentée.",
        progress={step.value: False for step in CoachingStepEnum}
    )
