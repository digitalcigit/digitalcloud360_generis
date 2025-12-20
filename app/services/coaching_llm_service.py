"""
CoachingLLMService - Extraction et validation LLM des réponses coaching
"""

import json
import structlog
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator

from app.core.providers.factory import ProviderFactory
from app.core.providers.base import BaseLLMProvider
from app.services.prompts_loader import PromptsLoader

logger = structlog.get_logger(__name__)

class LLMExtractionResult(BaseModel):
    """Schéma de validation pour les sorties LLM d'extraction"""
    extracted_data: Dict[str, Any] = Field(..., description="Données structurées extraites")
    is_valid: bool = Field(..., description="Si la réponse est suffisante")
    confidence_score: float = Field(..., description="Score de confiance 0-1")
    clarification_needed: bool = Field(..., description="Si besoin de clarifier")
    clarification_question: Optional[str] = Field(None, description="Question si clarification_needed")
    reformulated_response: str = Field(..., description="Version professionnelle reformulée")
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            return 0.5  # Fallback safe
        return v

class CoachingLLMService:
    """Service LLM pour extraction et validation réponses coaching"""
    
    def __init__(self):
        from app.config.settings import settings
        
        self.provider_factory = ProviderFactory(api_keys=settings.get_provider_api_keys())
        # Utilisation de Deepseek par défaut pour le coaching comme spécifié dans GEN-WO-002
        self.llm_provider: BaseLLMProvider = self.provider_factory.create_llm_provider(
            plan="genesis_basic",
            override_provider="deepseek",
            override_model="deepseek-chat"
        )
        self.prompts_loader = PromptsLoader()
        
        logger.info("CoachingLLMService initialized with Deepseek provider")
    
    async def extract_and_validate(
        self,
        step: str,
        user_response: str,
        sector: str = "default",
        context: Dict[str, Any] = None
    ) -> LLMExtractionResult:
        """
        Extrait et valide la réponse utilisateur pour une étape coaching.
        """
        
        extraction_prompt = f"""
EXTRACTION RÉPONSE COACHING - ÉTAPE {step.upper()}

RÉPONSE UTILISATEUR:
"{user_response}"

SECTEUR DÉTECTÉ: {sector}
CONTEXTE PRÉCÉDENT: {json.dumps(context or {}, ensure_ascii=False)}

TÂCHE:
1. Extraire les informations clés de la réponse
2. Évaluer si la réponse est suffisamment précise
3. Reformuler de manière professionnelle si valide
4. Proposer question de clarification si trop vague

FORMAT JSON STRICT:
{{
    "extracted_data": {{
        "key_points": ["point clé 1", "point clé 2"],
        "business_name": "nom entreprise si mentionné ou null",
        "sector_detected": "secteur détecté ou null",
        "location": {{"city": "", "country": ""}} ou null,
        "specific_details": ["détail spécifique 1"]
    }},
    "is_valid": true/false,
    "confidence_score": 0.0-1.0,
    "clarification_needed": true/false,
    "clarification_question": "question si needed ou null",
    "reformulated_response": "version professionnelle reformulée"
}}

CRITÈRES VALIDATION ÉTAPE {step.upper()}:
{self._get_validation_criteria(step)}

GÉNÉRER EXTRACTION (RÉPONDRE UNIQUEMENT EN JSON VALIDE):
"""
        
        system_message = """Tu es un expert en analyse de discours entrepreneurial. 
Tu extrais les informations clés des réponses d'entrepreneurs africains avec bienveillance.
Tu détectes les réponses vagues et proposes des questions de clarification adaptées.
RÉPONDS TOUJOURS EN JSON VALIDE."""
        
        try:
            logger.info("requesting_llm_extraction", step=step, sector=sector)
            
            response = await self.llm_provider.generate_structured(
                prompt=extraction_prompt,
                system_message=system_message,
                response_schema=LLMExtractionResult.model_json_schema(),
                temperature=0.3,
                max_tokens=1000
            )
            
            # Validation via Pydantic
            result = LLMExtractionResult(**response)
            
            logger.info(
                "llm_extraction_completed",
                step=step,
                is_valid=result.is_valid,
                confidence=result.confidence_score,
                clarification=result.clarification_needed
            )
            
            return result
            
        except Exception as e:
            logger.error("llm_extraction_failed", error=str(e), step=step)
            # Fallback safe
            return LLMExtractionResult(
                extracted_data={"raw_response": user_response},
                is_valid=True,
                confidence_score=0.5,
                clarification_needed=False,
                clarification_question=None,
                reformulated_response=user_response
            )
    
    async def detect_sector(self, user_messages: List[str]) -> str:
        """Détecte le secteur d'activité depuis les messages utilisateur"""
        
        combined_text = " ".join(user_messages)
        
        detection_prompt = f"""
Analyse ce texte et détecte le secteur d'activité principal:

"{combined_text}"

SECTEURS POSSIBLES:
- restaurant (restauration, food, cuisine, repas)
- technology (tech, digital, logiciel, app)
- health (santé, médical, bien-être)
- education (formation, école, cours)
- ecommerce (boutique, vente, commerce)
- salon (coiffure, beauté, esthétique)
- artisanat (artisan, fabrication, création manuelle)
- transport (livraison, taxi, logistique)
- agriculture (ferme, culture, élevage)
- services (consulting, prestation, service)
- default (si non identifiable)

RÉPONDS UNIQUEMENT AVEC LE NOM DU SECTEUR (un seul mot en minuscules):
"""
        
        try:
            response = await self.llm_provider.generate(
                prompt=detection_prompt,
                system_message="Tu es un classificateur de secteurs business. Réponds avec un seul mot.",
                temperature=0.1,
                max_tokens=20
            )
            
            sector = response.strip().lower()
            valid_sectors = ["restaurant", "technology", "health", "education", 
                           "ecommerce", "salon", "artisanat", "transport", 
                           "agriculture", "services", "default"]
            
            if sector not in valid_sectors:
                sector = "default"
                
            logger.info("sector_detected", sector=sector)
            return sector
            
        except Exception as e:
            logger.error("sector_detection_failed", error=str(e))
            return "default"
    
    def _get_validation_criteria(self, step: str) -> str:
        """Retourne les critères de validation pour une étape"""
        criteria = {
            "vision": "- Vision claire et inspirante\n- Impact communautaire identifié\n- Projection futur réaliste",
            "mission": "- Action concrète claire\n- Bénéfice client explicite\n- Méthode distinctive",
            "clientele": "- Segment client défini\n- Problèmes clients compris\n- Accessibilité clientèle",
            "differentiation": "- Avantage concurrentiel clair\n- Différenciation défendable\n- Valeur perçue",
            "offre": "- Offre compréhensible\n- Bénéfices explicites\n- Cohérence globale"
        }
        return criteria.get(step, criteria["vision"])

    async def get_socratic_help(self, step: str, brief: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """Génère une aide socratique (questions + indices)"""
        
        prompt = f"""
AIDE SOCRATIQUE COACHING - ÉTAPE {step.upper()}
SECTEUR: {sector}
BRIEF ACTUEL: {json.dumps(brief, ensure_ascii=False)}

TÂCHE:
Génère 2-3 questions socratiques pour aider l'entrepreneur à avancer sur cette étape.
Chaque question doit avoir un petit indice de contexte.

FORMAT JSON:
{{
    "questions": [
        {{"question": "...", "context_hint": "..."}}
    ],
    "suggestion": "Conseil global du coach"
}}
"""
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                system_message="Tu es le Coach IA Genesis spécialisé en maïeutique socratique.",
                response_schema={
                    "type": "object",
                    "properties": {
                        "questions": {"type": "array", "items": {"type": "object", "properties": {"question": {"type": "string"}, "context_hint": {"type": "string"}}}},
                        "suggestion": {"type": "string"}
                    }
                }
            )
            return response
        except Exception as e:
            logger.error("socratic_help_failed", error=str(e))
            return {"questions": [], "suggestion": "Essayez de décrire votre projet plus simplement."}

    async def reformulate(self, text: str, step: str) -> Dict[str, Any]:
        """Reformule un texte de manière professionnelle"""
        
        prompt = f"""
REFORMULATION PROFESSIONNELLE - ÉTAPE {step.upper()}
TEXTE ORIGINAL: "{text}"

TÂCHE:
1. Reformuler ce texte pour le rendre plus percutant et professionnel (style Genesis AI).
2. Vérifier si la reformulation est nettement meilleure.
3. Proposer 2 petites suggestions d'amélioration supplémentaires.

FORMAT JSON:
{{
    "original_text": "{text}",
    "reformulated_text": "...",
    "is_better": true,
    "suggestions": ["...", "..."]
}}
"""
        try:
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                system_message="Tu es l'Expert Contenu de Genesis AI.",
                response_schema={
                    "type": "object",
                    "properties": {
                        "original_text": {"type": "string"},
                        "reformulated_text": {"type": "string"},
                        "is_better": {"type": "boolean"},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                }
            )
            return response
        except Exception as e:
            logger.error("reformulation_failed", error=str(e))
            return {"original_text": text, "reformulated_text": text, "is_better": False, "suggestions": []}

    async def generate_proposals(self, step: str, brief: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """Génère 3 propositions de réponses pour l'étape en cours"""
        
        prompt = f"""
GÉNÉRATION DE PROPOSITIONS - ÉTAPE {step.upper()}
SECTEUR: {sector}
CONTEXTE: {json.dumps(brief, ensure_ascii=False)}

TÂCHE:
Génère 3 propositions de réponses complètes et inspirantes pour cette étape.
Chaque proposition doit avoir un titre et une justification.

FORMAT JSON:
{{
    "proposals": [
        {{"id": "p1", "title": "...", "content": "...", "justification": "..."}}
    ],
    "coach_advice": "Conseil pour choisir"
}}
"""
        try:
            # Retry logic for handling flaky Deepseek responses or JSON truncation
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await self.llm_provider.generate_structured(
                        prompt=prompt,
                        system_message="Tu es le Coach Créatif Genesis AI.",
                        response_schema={
                            "type": "object",
                            "properties": {
                                "proposals": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}, "justification": {"type": "string"}}}},
                                "coach_advice": {"type": "string"}
                            }
                        }
                    )
                    return response
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed, re-raise to catch block below
                        raise e
                    logger.warning("proposals_generation_retry", attempt=attempt+1, error=str(e))
                    continue

        except Exception as e:
            logger.error("proposals_generation_failed", error=str(e))
            return {"proposals": [], "coach_advice": "Veuillez réessayer plus tard."}
