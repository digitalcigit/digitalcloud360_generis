"""
PromptsLoader - Chargement prompts coaching depuis fichier spec technique
"""

from typing import Dict, Any
import structlog
from docs.genesis_ai_technical_specification.PROMPTS_COACHING_METHODOLOGIE import (
    COACH_SYSTEM_PROMPT,
    VISION_COACHING_PROMPT,
    VISION_EXAMPLES_BY_SECTOR,
    MISSION_COACHING_PROMPT,
    MISSION_EXAMPLES_BY_SECTOR,
    CLIENTELE_COACHING_PROMPT,
    CLIENTELE_EXAMPLES_BY_SECTOR,
    DIFFERENTIATION_COACHING_PROMPT,
    OFFRE_COACHING_PROMPT,
)
from app.services.prompts_user_messages import get_user_message

logger = structlog.get_logger(__name__)

COACHING_PROMPTS = {
    "vision": {
        "prompt_template": VISION_COACHING_PROMPT,
        "examples_by_sector": VISION_EXAMPLES_BY_SECTOR,
        "validation_criteria": ["vision_claire", "impact_identifie", "projection_realiste"]
    },
    "mission": {
        "prompt_template": MISSION_COACHING_PROMPT,
        "examples_by_sector": MISSION_EXAMPLES_BY_SECTOR,
        "validation_criteria": ["action_concrete", "benefice_client", "methode_distinctive"]
    },
    "clientele": {
        "prompt_template": CLIENTELE_COACHING_PROMPT,
        "examples_by_sector": CLIENTELE_EXAMPLES_BY_SECTOR,
        "validation_criteria": ["segment_client_defini", "problèmes_clients_compris", "besoins_spécifiques_identifiés"]
    },
    "differentiation": {
        "prompt_template": DIFFERENTIATION_COACHING_PROMPT,
        "examples_by_sector": {},  # Will use generic if empty
        "validation_criteria": ["avantage_concurrentiel_clair", "différenciation_défendable", "valeur_perçue_client"]
    },
    "offre": {
        "prompt_template": OFFRE_COACHING_PROMPT,
        "examples_by_sector": {},
        "validation_criteria": ["offre_claire_et_compréhensible", "bénéfices_clients_explicites", "cohérence_globale"]
    }
}

class PromptsLoader:
    """Chargeur de prompts coaching sectoriels"""
    
    def __init__(self):
        self.prompts = COACHING_PROMPTS
        self.system_prompt = COACH_SYSTEM_PROMPT
        logger.info("PromptsLoader initialized with 5 coaching steps")
    
    def get_step_prompt(
        self, 
        step: str, 
        sector: str = "default",
        user_name: str = "cher entrepreneur",
        validated_previous: str = "",
        location: Dict[str, str] = None,
        user_profile: str = "Entrepreneur", 
        experience_level: str = "Débutant"
        ) -> Dict[str, Any]:
        """
        Retourne le prompt formaté pour une étape donnée.
        """
        step_config = self.prompts.get(step, self.prompts["vision"])
        
        # Récupérer exemples sectoriels
        sector_examples_list = step_config["examples_by_sector"].get(
            sector.lower(), 
            step_config["examples_by_sector"].get("default", [])
        )
        
        # Formater le prompt avec variables (fallback sur strings vides pour éviter KeyError)
        prompt_text = step_config["prompt_template"].format(
            user_name=user_name,
            sector=sector,
            location=f"{location.get('city', '')}, {location.get('country', 'Afrique')}" if location else "Afrique",
            user_profile="Entrepreneur", # Default
            experience_level="Débutant", # Default
            validated_previous=validated_previous,
            validated_vision=validated_previous if step == "mission" else "",
            validated_mission=validated_previous if step == "clientele" else "",
            validated_clientele=validated_previous if step == "differentiation" else "",
            validated_differentiation=validated_previous if step == "offre" else "",
            sector_examples="\n".join([f"• {ex}" for ex in sector_examples_list[:3]]) if sector_examples_list else "",
            sector_mission_examples="\n".join([f"• {ex}" for ex in sector_examples_list[:3]]) if sector_examples_list else "",
            clientele_examples="\n".join([f"• {ex}" for ex in sector_examples_list[:3]]) if sector_examples_list else "",
            differentiation_examples="\n".join([f"• {ex}" for ex in sector_examples_list[:3]]) if sector_examples_list else "",
            offre_examples="\n".join([f"• {ex}" for ex in sector_examples_list[:3]]) if sector_examples_list else ""
        )
        
        # Formater les exemples en choix cliquables pour le frontend
        clickable_choices = [
            {"id": f"choice-{i}", "text": ex} 
            for i, ex in enumerate(sector_examples_list[:5])
        ]

        # Messages épurés pour l'utilisateur
        user_msg = get_user_message(step)
        user_choices = user_msg["choices"]
        user_clickable = [
            {"id": f"user-choice-{i}", "text": choice} for i, choice in enumerate(user_choices)
        ]

        return {
            "prompt_text": prompt_text,                 # Pour l'IA
            "examples": sector_examples_list[:5],       # Exemples sectoriels (optionnel)
            "validation_criteria": step_config["validation_criteria"],
            "system_prompt": self.system_prompt,
            "clickable_choices": clickable_choices,     # Ancien format
            "user_message": user_msg["user_message"],   # Texte épuré pour UI
            "user_choices": user_choices,               # Choix épurés pour UI
            "user_clickable": user_clickable,           # Choix cliquables UI
        }
