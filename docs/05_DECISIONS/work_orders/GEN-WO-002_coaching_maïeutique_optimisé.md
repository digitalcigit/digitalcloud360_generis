---
title: "Work Order GEN-WO-002: Coaching Maïeutique 5 Étapes - Niveau Argent (Coach IA Proactif)"
type: work_order
priority: P0 - CRITIQUE
status: approved
created: 2025-12-19
updated: 2025-12-19
supersedes: GEN-WO-001
tech_lead: Cascade (Tech Lead Genesis)
assignee: Senior Dev IA
estimated_effort: 8-10 jours (Niveau Argent avec IA proactive)
niveau_ia: Argent (Coach IA Proactif)
contribution_ia: ~80%
tags: ["coaching", "maïeutique", "5-étapes", "langgraph", "deepseek", "ia-proactive", "aide-formulation"]
---

# 🎯 WORK ORDER GEN-WO-002 - NIVEAU ARGENT
## Coaching Maïeutique 5 Étapes - Coach IA Proactif

**Ce Work Order remplace GEN-WO-001** en tirant parti de l'analyse profonde des acquis existants.

> **NIVEAU ARGENT VALIDÉ PAR PO (19/12/2025)**
> L'IA ne sera pas un simple juge qui analyse les réponses, mais un **coach actif qui aide à formuler**.
> Notre cible: entrepreneurs africains qui n'ont souvent jamais formalisé leur vision/mission.

---

## 1. CONTEXTE STRATÉGIQUE

### 1.1 Décisions PO (19/12/2025)

| Question | Réponse PO |
|----------|------------|
| Priorité business | Expérience coaching maïeutique **COMPLÈTE** |
| Coaching 5 étapes | **INDISPENSABLE** - Cœur différenciateur |
| Personnalisation site | Contenu LLM **COMPLET** personnalisé |
| Niveau IA | **ARGENT** - Coach proactif qui aide à formuler |
| Temps génération | **Accepté** - La valeur produite justifie l'attente |
| Cible utilisateur | Entrepreneurs africains, souvent première formalisation vision/mission |

### 1.2 Philosophie Niveau Argent

> *"C'est souvent une colle pour certains entrepreneurs"* - PO
>
> L'entrepreneur sénégalais qui lance son restaurant n'a probablement jamais écrit de "vision statement".
> Lui demander "Quelle est votre vision?" sans aide, c'est comme demander à quelqu'un de nager sans lui avoir appris.
>
> **L'IA doit être un facilitateur actif, pas juste un validateur.**

### 1.3 Analyse des Acquis (Économie ~65% du temps)

L'audit du code existant révèle que **la majorité des briques sont déjà implémentées** mais **non connectées**:

| Composant | Status | Lignes | Action |
|-----------|--------|--------|--------|
| `RedisVirtualFileSystem` | ✅ Complet | 204 | Aucune |
| `ProviderFactory` (multi-LLM) | ✅ Complet | 222 | Aucune |
| `ContentSubAgent` | ✅ Complet | 631 | Connecter au Transformer |
| `ResearchSubAgent` | ✅ Complet | 554 | Aucune |
| `coaching.py` endpoint | ⚠️ Bug | 328 | Corriger variable |
| `PROMPTS_COACHING_METHODOLOGIE.py` | ✅ Asset | 530 | Charger dans coaching |
| `BriefToSiteTransformer` | ⚠️ Incomplet | 364 | Mapper content_generation |
| Modèles DB Coaching | ✅ Complet | 122 | Aucune |

---

## 2. OBJECTIF & CRITÈRES DE SUCCÈS

### 2.1 Objectif Principal

Activer le **flux coaching maïeutique 5 étapes complet** avec un **Coach IA Proactif** (Niveau Argent) qui aide activement l'entrepreneur à formuler ses réponses, pas juste à les valider.

### 2.2 Definition of Done - Niveau Argent

#### Fonctionnalités Core (Sprint 1)
- [ ] Flow coaching 5 étapes fonctionnel: Vision → Mission → Clientèle → Différenciation → Offre
- [ ] Prompts sectoriels chargés depuis `PROMPTS_COACHING_METHODOLOGIE.py`
- [ ] Extraction LLM intelligente des réponses utilisateur
- [ ] Questions de clarification si réponse vague
- [ ] Contenu généré par ContentSubAgent utilisé dans le site final
- [ ] Couleurs et thème adaptés au secteur détecté

#### Fonctionnalités Niveau Argent (Sprint 2) ⭐ NOUVEAU
- [ ] **Bouton "Aide-moi à formuler"** → Questions socratiques guidées par l'IA
- [ ] **Choix cliquables** → Pistes thématiques pour chaque étape
- [ ] **Reformulation temps réel** → Texte brut transformé en version professionnelle live
- [ ] **Mode "Je ne sais pas"** → IA génère proposition complète à valider/modifier

#### Validation Finale
- [ ] Test E2E validé: "Restaurant Teranga Dakar" → Site personnalisé complet
- [ ] Test UX: Entrepreneur sans formation peut compléter le flow sans blocage

---

## 3. ARCHITECTURE CIBLE - NIVEAU ARGENT

### 3.1 Flow Global Coach IA Proactif

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FLUX COACHING MAÏEUTIQUE - NIVEAU ARGENT                        │
│                    (Coach IA Proactif)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  POST /coaching/start                                                        │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ ÉTAPE VISION (exemple - même pattern pour toutes les étapes)            ││
│  │                                                                          ││
│  │  ┌────────────────────────────────────────────────────────────────────┐ ││
│  │  │ Coach IA: "Parlons de votre VISION..."                             │ ││
│  │  │                                                                     │ ││
│  │  │ 💡 Pour vous aider, répondez à cette question simple:              │ ││
│  │  │    'Dans 5 ans, si votre business est un succès total,             │ ││
│  │  │     à quoi ressemble-t-il?'                                        │ ││
│  │  │                                                                     │ ││
│  │  │ 🎯 Ou choisissez une piste pour démarrer:                          │ ││
│  │  │    [Devenir une référence locale]                                  │ ││
│  │  │    [Transformer mon secteur]                                       │ ││
│  │  │    [Créer de l'emploi dans ma communauté]                          │ ││
│  │  │                                                                     │ ││
│  │  │ [💡 Aide-moi à formuler ma vision]  ← NOUVEAU NIVEAU ARGENT        │ ││
│  │  │ [❓ Je ne sais pas]                  ← NOUVEAU NIVEAU ARGENT        │ ││
│  │  └────────────────────────────────────────────────────────────────────┘ ││
│  │       │                                                                  ││
│  │       ├──► Utilisateur tape texte libre                                 ││
│  │       │         │                                                        ││
│  │       │         ▼                                                        ││
│  │       │    ┌─────────────────────────────────────────────────────────┐  ││
│  │       │    │ Reformulation temps réel (pendant frappe)               │  ││
│  │       │    │ "je veux faire le meilleur thieb"                       │  ││
│  │       │    │         ↓                                               │  ││
│  │       │    │ ✨ "Devenir LA référence du Thieboudienne authentique   │  ││
│  │       │    │     à Dakar, reconnu pour la qualité..."                │  ││
│  │       │    └─────────────────────────────────────────────────────────┘  ││
│  │       │                                                                  ││
│  │       ├──► Utilisateur clique "Aide-moi"                                ││
│  │       │         │                                                        ││
│  │       │         ▼                                                        ││
│  │       │    ┌─────────────────────────────────────────────────────────┐  ││
│  │       │    │ Questions Socratiques Guidées:                          │  ││
│  │       │    │ 1. "Qu'est-ce qui vous a poussé à créer ce business?"   │  ││
│  │       │    │    [Passion] [Opportunité] [Besoin famille] [Autre]     │  ││
│  │       │    │ 2. "Dans 5 ans, qu'est-ce qui a changé?"                │  ││
│  │       │    │    [Plusieurs employés] [Connu en ville] [Expansion]    │  ││
│  │       │    │ 3. "Quel impact sur votre communauté?"                  │  ││
│  │       │    │    [Emplois] [Qualité accessible] [Innovation]          │  ││
│  │       │    │                                                         │  ││
│  │       │    │ → IA génère vision basée sur réponses                   │  ││
│  │       │    └─────────────────────────────────────────────────────────┘  ││
│  │       │                                                                  ││
│  │       └──► Utilisateur clique "Je ne sais pas"                          ││
│  │                 │                                                        ││
│  │                 ▼                                                        ││
│  │            ┌─────────────────────────────────────────────────────────┐  ││
│  │            │ IA génère 3 propositions complètes:                     │  ││
│  │            │                                                         │  ││
│  │            │ Option A: "Devenir le restaurant familial de référence  │  ││
│  │            │            à Dakar pour la cuisine sénégalaise..."      │  ││
│  │            │                                                         │  ││
│  │            │ Option B: "Créer un lieu de partage où les familles     │  ││
│  │            │            dakaroises redécouvrent les saveurs..."      │  ││
│  │            │                                                         │  ││
│  │            │ Option C: "Préserver et transmettre les recettes        │  ││
│  │            │            traditionnelles sénégalaises..."             │  ││
│  │            │                                                         │  ││
│  │            │ [Choisir A] [Choisir B] [Choisir C] [Modifier]          │  ││
│  │            └─────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  [Même pattern pour: MISSION → CLIENTÈLE → DIFFÉRENCIATION → OFFRE]         │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              LangGraphOrchestrator.run()                             │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ Research │  │ Content  │  │   Logo   │  │   SEO    │ (parallèle)│    │
│  │  │ SubAgent │  │ SubAgent │  │  Agent   │  │  Agent   │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ BriefToSiteTransformer.transform()                                   │    │
│  │   - Utilise content_generation.homepage.hero_section                 │    │
│  │   - Applique couleurs sectorielles                                   │    │
│  │   - Génère SiteDefinition complet                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Frontend: Site Preview avec contenu personnalisé                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. TÂCHES DÉTAILLÉES

### SPRINT 1: Corrections & Connexions (3-4 jours)

---

#### TÂCHE 1.1: Corriger bug `coaching.py` (0.5 jour)

**Fichier**: `app/api/v1/coaching.py`

**Problème**: À partir de la ligne 157, le code utilise `session.current_step` au lieu de `session_data["current_step"]`.

**Correction requise**:

```python
# Ligne 157 - AVANT (bug)
elif session.current_step == CoachingStepEnum.MISSION:

# Ligne 157 - APRÈS (corrigé)
elif session_data["current_step"] == CoachingStepEnum.MISSION.value:
```

**Appliquer la même correction aux lignes**: 157, 200, 244, 289

**Test de validation**:
```bash
curl -X POST http://localhost:8002/api/v1/coaching/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
# Doit retourner session_id + message vision
```

---

#### TÂCHE 1.2: Créer `PromptsLoader` (0.5 jour)

**Nouveau fichier**: `app/services/prompts_loader.py`

**Objectif**: Charger les prompts depuis `PROMPTS_COACHING_METHODOLOGIE.py` au lieu des messages hardcodés.

```python
"""
PromptsLoader - Chargement prompts coaching depuis fichier spec
"""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)

# Import des prompts depuis la spec technique
# Note: Ces constantes seront copiées depuis docs/genesis-ai-technical-specification/
COACH_SYSTEM_PROMPT = """
Tu es le Coach IA Genesis, expert en entrepreneuriat africain avec 15 ans d'expérience.
...
"""

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
    # ... autres étapes
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
        sector: str,
        user_name: str = "",
        validated_previous: str = "",
        location: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Retourne le prompt formaté pour une étape donnée.
        
        Args:
            step: Étape coaching (vision, mission, clientele, differentiation, offre)
            sector: Secteur business détecté
            user_name: Prénom utilisateur
            validated_previous: Réponse validée étape précédente
            location: Localisation {city, country}
            
        Returns:
            Dict avec prompt_text, examples, validation_criteria
        """
        step_config = self.prompts.get(step, self.prompts["vision"])
        
        # Récupérer exemples sectoriels
        sector_examples = step_config["examples_by_sector"].get(
            sector.lower(), 
            step_config["examples_by_sector"].get("default", [])
        )
        
        # Formater le prompt avec variables
        prompt_text = step_config["prompt_template"].format(
            user_name=user_name or "cher entrepreneur",
            sector=sector,
            location=location or {"city": "", "country": "Afrique"},
            validated_previous=validated_previous,
            sector_examples="\n".join([f"• {ex}" for ex in sector_examples[:3]])
        )
        
        return {
            "prompt_text": prompt_text,
            "examples": sector_examples[:5],
            "validation_criteria": step_config["validation_criteria"],
            "system_prompt": self.system_prompt
        }
    
    def get_reformulation_prompt(self, step: str, vague_response: str) -> str:
        """Retourne un prompt de reformulation pour réponse vague"""
        return f"""
        La réponse suivante pour l'étape {step} est trop vague:
        "{vague_response}"
        
        Génère une question de clarification bienveillante pour aider 
        l'entrepreneur à préciser sa pensée.
        """
```

**Action**: Copier les constantes depuis `docs/genesis-ai-technical-specification/PROMPTS_COACHING_METHODOLOGIE.py`

---

#### TÂCHE 1.3: Créer `CoachingLLMService` (1 jour)

**Nouveau fichier**: `app/services/coaching_llm_service.py`

**Objectif**: Extraction intelligente et reformulation via Deepseek.

```python
"""
CoachingLLMService - Extraction et validation LLM des réponses coaching
"""

import json
import structlog
from typing import Dict, Any, Optional, List

from app.core.providers.factory import ProviderFactory
from app.core.providers.base import BaseLLMProvider
from app.services.prompts_loader import PromptsLoader

logger = structlog.get_logger(__name__)


class CoachingLLMService:
    """Service LLM pour extraction et validation réponses coaching"""
    
    def __init__(self):
        from app.config.settings import settings
        
        self.provider_factory = ProviderFactory(api_keys=settings.get_provider_api_keys())
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
    ) -> Dict[str, Any]:
        """
        Extrait et valide la réponse utilisateur pour une étape coaching.
        
        Args:
            step: Étape coaching actuelle
            user_response: Réponse brute utilisateur
            sector: Secteur détecté
            context: Contexte accumulé des étapes précédentes
            
        Returns:
            Dict avec:
                - extracted_data: Données structurées extraites
                - is_valid: True si réponse suffisante
                - confidence_score: Score confiance 0-1
                - clarification_needed: True si besoin clarification
                - clarification_question: Question si needed
                - reformulated_response: Version reformulée professionnelle
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
    "reformulated_response": "version professionnelle reformulée",
    "validation_notes": "notes sur ce qui manque ou est bien"
}}

CRITÈRES VALIDATION ÉTAPE {step.upper()}:
{self._get_validation_criteria(step)}

GÉNÉRER EXTRACTION:
"""
        
        system_message = """Tu es un expert en analyse de discours entrepreneurial. 
Tu extrais les informations clés des réponses d'entrepreneurs africains avec bienveillance.
Tu détectes les réponses vagues et proposes des questions de clarification adaptées.
RÉPONDS TOUJOURS EN JSON VALIDE."""
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=extraction_prompt,
                system_message=system_message,
                response_schema={
                    "extracted_data": "object",
                    "is_valid": "boolean",
                    "confidence_score": "number",
                    "clarification_needed": "boolean",
                    "clarification_question": "string",
                    "reformulated_response": "string"
                },
                temperature=0.3,
                max_tokens=1000
            )
            
            logger.info(
                "Extraction completed",
                step=step,
                is_valid=response.get("is_valid"),
                confidence=response.get("confidence_score")
            )
            
            return response
            
        except Exception as e:
            logger.error("Extraction failed", error=str(e))
            # Fallback: accepter la réponse telle quelle
            return {
                "extracted_data": {"raw_response": user_response},
                "is_valid": True,
                "confidence_score": 0.5,
                "clarification_needed": False,
                "clarification_question": None,
                "reformulated_response": user_response,
                "fallback_mode": True
            }
    
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

RÉPONDS UNIQUEMENT AVEC LE NOM DU SECTEUR (un seul mot):
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
                
            logger.info("Sector detected", sector=sector)
            return sector
            
        except Exception as e:
            logger.error("Sector detection failed", error=str(e))
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
```

---

#### TÂCHE 1.4: Connecter ContentSubAgent → Transformer (0.5 jour)

**Fichier**: `app/services/transformer.py`

**Problème**: Le contenu généré par ContentSubAgent (`content_generation.homepage.hero_section`) n'est pas utilisé.

**Modification `_map_hero_section`** (lignes ~123-143):

```python
def _map_hero_section(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, Any]:
    """Génère la section Hero en utilisant le contenu LLM généré"""
    
    # PRIORITÉ 1: Contenu généré par ContentSubAgent
    if brief.content_generation and isinstance(brief.content_generation, dict):
        homepage = brief.content_generation.get("homepage", {})
        hero = homepage.get("hero_section", {})
        
        if hero and isinstance(hero, dict):
            return {
                "id": "hero",
                "type": "hero",
                "content": {
                    "title": hero.get("title") or brief.business_name,
                    "subtitle": hero.get("subtitle") or brief.mission[:120] if brief.mission else "",
                    "description": hero.get("hero_paragraph") or brief.differentiation[:200] if brief.differentiation else None,
                    "image": self._extract_hero_image(brief),
                    "cta": {
                        "text": hero.get("primary_cta") or sector_config.get("cta_text", "Nous contacter"),
                        "link": "#contact",
                        "variant": "primary"
                    },
                    "alignment": "center",
                    "overlay": False
                }
            }
    
    # FALLBACK: Ancienne logique (valeurs brutes du brief)
    cta_text = sector_config.get("cta_text", "Nous contacter")
    return {
        "id": "hero",
        "type": "hero",
        "content": {
            "title": brief.value_proposition or brief.business_name,
            "subtitle": brief.mission[:120] if brief.mission else "",
            "description": brief.differentiation[:200] if brief.differentiation else None,
            "image": self._extract_hero_image(brief),
            "cta": {
                "text": cta_text,
                "link": "#contact",
                "variant": "primary"
            },
            "alignment": "center",
            "overlay": False
        }
    }
```

**Même pattern pour**: `_map_about_section`, `_map_services_section`, `_map_contact_section`

---

#### TÂCHE 1.5: Intégrer Coaching → LangGraph (0.5 jour)

**Fichier**: `app/api/v1/coaching.py`

**Modification**: Après l'étape OFFRE (ligne ~289-319), déclencher l'orchestrateur.

```python
elif session_data["current_step"] == CoachingStepEnum.OFFRE.value:
    # Save the user's response for the OFFRE step
    offre_step = CoachingStep(
        session_id=session_data["id"],
        step_name=CoachingStepEnum.OFFRE,
        step_order=5,
        user_response=request.user_response,
        coach_message="Coaching terminé - Génération site en cours..."
    )
    db.add(offre_step)
    
    # Mark coaching as complete
    session_data["status"] = SessionStatusEnum.COACHING_COMPLETE.value
    
    # ============ NOUVEAU: Trigger LangGraph Orchestrator ============
    from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
    from app.services.transformer import BriefToSiteTransformer
    
    # Construire le business_brief depuis les étapes coaching
    business_brief = await _build_brief_from_coaching_steps(
        session_id=session_data["id"],
        db=db
    )
    
    # Exécuter orchestrateur
    orchestrator = LangGraphOrchestrator()
    orchestration_result = await orchestrator.run({
        "user_id": current_user.id,
        "brief_id": session_data["session_id"],
        "business_brief": business_brief
    })
    
    # Transformer en SiteDefinition
    transformer = BriefToSiteTransformer()
    
    # Créer un objet brief enrichi avec résultats orchestration
    enriched_brief = BusinessBriefData(
        business_name=business_brief.get("business_name", "Mon Business"),
        sector=business_brief.get("industry_sector", "default"),
        vision=business_brief.get("vision", ""),
        mission=business_brief.get("mission", ""),
        target_audience=business_brief.get("target_market", ""),
        differentiation=business_brief.get("competitive_advantage", ""),
        value_proposition=business_brief.get("value_proposition", ""),
        location=business_brief.get("location", {}),
        content_generation=orchestration_result.get("content_generation", {}),
        logo_creation=orchestration_result.get("logo_creation", {}),
        seo_optimization=orchestration_result.get("seo_optimization", {})
    )
    
    site_definition = transformer.transform(enriched_brief)
    
    # Sauvegarder en Redis
    await redis_client.set(
        f"site:{session_data['session_id']}", 
        json.dumps(site_definition), 
        ex=86400  # 24h
    )
    
    session_data["status"] = SessionStatusEnum.COMPLETED.value
    await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)
    
    # Retourner réponse finale avec site_data
    return CoachingResponse(
        session_id=session_data["session_id"],
        current_step=CoachingStepEnum.OFFRE.value,
        coach_message="🎉 Félicitations ! Votre session de coaching est terminée. Votre site personnalisé a été généré !",
        examples=[],
        next_questions=[],
        progress={step.value: True for step in CoachingStepEnum},
        is_step_complete=True,
        site_data=site_definition  # Nouveau champ à ajouter au schema
    )
```

**Fonction helper à ajouter**:

```python
async def _build_brief_from_coaching_steps(session_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Construit le business_brief depuis les étapes coaching sauvegardées"""
    
    # Récupérer toutes les étapes
    result = await db.execute(
        select(CoachingStep)
        .filter(CoachingStep.session_id == session_id)
        .order_by(CoachingStep.step_order)
    )
    steps = result.scalars().all()
    
    brief = {
        "business_name": "",
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
```

---

### SPRINT 2: Fonctionnalités Niveau Argent - Coach IA Proactif (4-5 jours)

> **OBJECTIF SPRINT 2**: Transformer l'IA de "validateur" en "facilitateur actif"
> L'entrepreneur africain qui n'a jamais formalisé sa vision doit pouvoir compléter le flow sans blocage.

---

#### TÂCHE 2.1: Intégrer CoachingLLMService dans endpoint (1 jour)

**Fichier**: `app/api/v1/coaching.py`

**Modification**: Utiliser `CoachingLLMService` pour extraction et clarification.

```python
from app.services.coaching_llm_service import CoachingLLMService
from app.services.prompts_loader import PromptsLoader

# Initialiser services
coaching_llm = CoachingLLMService()
prompts_loader = PromptsLoader()

@router.post("/step", response_model=CoachingResponse)
async def process_coaching_step(request: CoachingStepRequest, ...):
    # ... récupération session_data ...
    
    current_step = session_data["current_step"]
    
    # Extraction et validation LLM
    extraction = await coaching_llm.extract_and_validate(
        step=current_step,
        user_response=request.user_response,
        sector=session_data.get("detected_sector", "default"),
        context=session_data.get("accumulated_context", {})
    )
    
    # Si clarification nécessaire
    if extraction["clarification_needed"]:
        return CoachingResponse(
            session_id=session_data["session_id"],
            current_step=current_step,
            coach_message=extraction["clarification_question"],
            examples=prompts_loader.get_step_prompt(current_step, sector)["examples"],
            confidence_score=extraction["confidence_score"],
            is_step_complete=False
        )
    
    # Sinon, sauvegarder et passer à l'étape suivante
    # ... suite du code ...
```

---

#### TÂCHE 2.2: Ajouter secteurs manquants (0.5 jour)

**Fichier**: `app/services/sector_mappings.py`

**Ajouter**:

```python
SECTOR_MAPPINGS["salon"] = {
    "default_colors": {
        "primary": "#EC4899",    # Pink
        "secondary": "#8B5CF6",  # Purple
    },
    "default_icons": ["scissors", "sparkles", "heart", "star", "droplet", "crown"],
    "section_order": ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
    "cta_text": "Prendre rendez-vous",
    "about_title": "Notre Savoir-Faire",
}

SECTOR_MAPPINGS["artisanat"] = {
    "default_colors": {
        "primary": "#D97706",    # Amber
        "secondary": "#92400E",  # Brown
    },
    "default_icons": ["hammer", "palette", "gem", "hand", "brush", "scissors"],
    "section_order": ["hero", "about", "gallery", "services", "contact", "footer"],
    "cta_text": "Découvrir nos créations",
    "about_title": "L'Art de Nos Mains",
}

SECTOR_MAPPINGS["transport"] = {
    "default_colors": {
        "primary": "#0891B2",    # Cyan
        "secondary": "#0D9488",  # Teal
    },
    "default_icons": ["truck", "map-pin", "clock", "package", "route", "navigation"],
    "section_order": ["hero", "services", "features", "about", "contact", "footer"],
    "cta_text": "Demander un devis",
    "about_title": "Votre Partenaire Mobilité",
}
```

---

#### TÂCHE 2.3: Bouton "Aide-moi à formuler" + Questions Socratiques (1 jour) ⭐ NIVEAU ARGENT

**Fichiers**: `app/api/v1/coaching.py`, `app/services/coaching_llm_service.py`, `app/schemas/coaching.py`

**Objectif**: Quand l'utilisateur est bloqué, proposer des questions simples guidées par l'IA.

**Nouveau endpoint**: `POST /api/v1/coaching/help`

```python
class CoachingHelpRequest(BaseModel):
    """Requête pour obtenir de l'aide à la formulation"""
    session_id: str
    step: str  # vision, mission, clientele, differentiation, offre

class SocraticQuestion(BaseModel):
    """Question socratique avec choix"""
    question: str
    choices: List[str]
    allows_custom: bool = True

class CoachingHelpResponse(BaseModel):
    """Réponse avec questions guidées"""
    questions: List[SocraticQuestion]
    intro_message: str


@router.post("/help", response_model=CoachingHelpResponse)
async def get_formulation_help(request: CoachingHelpRequest, ...):
    """Génère des questions socratiques pour aider l'utilisateur à formuler sa réponse"""
    
    # Questions pré-définies par étape + personnalisation LLM
    socratic_questions = await coaching_llm.generate_socratic_questions(
        step=request.step,
        sector=session_data.get("detected_sector", "default"),
        context=session_data.get("accumulated_context", {})
    )
    
    return CoachingHelpResponse(
        intro_message=f"Pas de souci ! Répondons ensemble à quelques questions simples...",
        questions=socratic_questions
    )
```

**Dans `CoachingLLMService`**, ajouter:

```python
async def generate_socratic_questions(
    self, 
    step: str, 
    sector: str,
    context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Génère des questions socratiques adaptées au contexte"""
    
    base_questions = {
        "vision": [
            {
                "question": "Qu'est-ce qui vous a poussé à créer ce business ?",
                "choices": ["Ma passion personnelle", "Une opportunité vue", "Un besoin pour ma famille", "Autre"]
            },
            {
                "question": "Dans 5 ans, votre business est un succès. Qu'est-ce qui a changé ?",
                "choices": ["J'ai plusieurs employés", "Je suis connu dans ma ville", "J'ai ouvert d'autres points", "Autre"]
            },
            {
                "question": "Quel impact voulez-vous avoir sur votre communauté ?",
                "choices": ["Créer des emplois", "Offrir qualité accessible", "Innover dans mon secteur", "Autre"]
            }
        ],
        "mission": [
            {
                "question": "Quel problème principal résolvez-vous pour vos clients ?",
                "choices": ["Gagner du temps", "Économiser de l'argent", "Se sentir bien/beau", "Autre"]
            },
            {
                "question": "Comment vos clients se sentent après avoir utilisé votre service ?",
                "choices": ["Satisfaits", "Soulagés", "Fiers", "Heureux", "Autre"]
            }
        ],
        # ... autres étapes
    }
    
    # Personnalisation LLM si secteur connu
    if sector != "default":
        prompt = f"""
        Génère 3 questions simples pour aider un entrepreneur du secteur {sector}
        à formuler sa {step}. Format: question + 4 choix de réponse.
        Contexte précédent: {context}
        """
        # ... appel LLM ...
    
    return base_questions.get(step, base_questions["vision"])


async def generate_response_from_socratic(
    self,
    step: str,
    answers: List[Dict[str, str]],  # [{"question": "...", "answer": "..."}]
    sector: str
) -> Dict[str, Any]:
    """Génère une réponse structurée à partir des réponses aux questions socratiques"""
    
    prompt = f"""
    Basé sur ces réponses à des questions de coaching pour l'étape {step}:
    {json.dumps(answers, ensure_ascii=False)}
    
    Secteur: {sector}
    
    Génère une {step} professionnelle et inspirante pour cet entrepreneur africain.
    La formulation doit être claire, concise et refléter les réponses données.
    
    Format: JSON avec "generated_response" et "confidence_score"
    """
    
    return await self.llm_provider.generate_structured(...)
```

---

#### TÂCHE 2.4: Choix Cliquables par Étape (0.5 jour) ⭐ NIVEAU ARGENT

**Fichiers**: `app/services/prompts_loader.py`, `app/schemas/coaching.py`

**Objectif**: Proposer des pistes thématiques cliquables pour démarrer.

**Modifier `PromptsLoader`**:

```python
CLICKABLE_CHOICES = {
    "vision": [
        {"id": "reference", "label": "Devenir une référence locale", "icon": "🏆"},
        {"id": "transform", "label": "Transformer mon secteur", "icon": "🚀"},
        {"id": "employ", "label": "Créer de l'emploi dans ma communauté", "icon": "👥"},
        {"id": "heritage", "label": "Transmettre un savoir-faire", "icon": "🎓"},
        {"id": "custom", "label": "Écrire ma propre réponse...", "icon": "✏️"}
    ],
    "mission": [
        {"id": "quality", "label": "Offrir la meilleure qualité", "icon": "⭐"},
        {"id": "accessible", "label": "Rendre accessible à tous", "icon": "🤝"},
        {"id": "innovate", "label": "Innover et moderniser", "icon": "💡"},
        {"id": "serve", "label": "Servir avec excellence", "icon": "🎯"},
        {"id": "custom", "label": "Écrire ma propre réponse...", "icon": "✏️"}
    ],
    "clientele": [
        {"id": "families", "label": "Les familles", "icon": "👨‍👩‍👧‍👦"},
        {"id": "professionals", "label": "Les professionnels", "icon": "💼"},
        {"id": "youth", "label": "Les jeunes", "icon": "🎓"},
        {"id": "women", "label": "Les femmes", "icon": "👩"},
        {"id": "custom", "label": "Autre clientèle...", "icon": "✏️"}
    ],
    "differentiation": [
        {"id": "expertise", "label": "Mon expertise unique", "icon": "🎯"},
        {"id": "service", "label": "Mon service client exceptionnel", "icon": "💎"},
        {"id": "price", "label": "Mon rapport qualité/prix", "icon": "💰"},
        {"id": "local", "label": "Ma connaissance locale", "icon": "📍"},
        {"id": "custom", "label": "Autre avantage...", "icon": "✏️"}
    ],
    "offre": [
        {"id": "main", "label": "Un produit/service principal", "icon": "🎁"},
        {"id": "packages", "label": "Des formules/packages", "icon": "📦"},
        {"id": "subscription", "label": "Des abonnements", "icon": "🔄"},
        {"id": "custom", "label": "Décrire mon offre...", "icon": "✏️"}
    ]
}

def get_clickable_choices(self, step: str) -> List[Dict[str, str]]:
    """Retourne les choix cliquables pour une étape"""
    return CLICKABLE_CHOICES.get(step, CLICKABLE_CHOICES["vision"])
```

**Modifier `CoachingResponse`** dans schemas:

```python
class ClickableChoice(BaseModel):
    id: str
    label: str
    icon: str

class CoachingResponse(BaseModel):
    # ... champs existants ...
    clickable_choices: List[ClickableChoice] = Field(
        default_factory=list, 
        description="Pistes thématiques cliquables"
    )
```

---

#### TÂCHE 2.5: Reformulation Temps Réel (1 jour) ⭐ NIVEAU ARGENT

**Fichiers**: `app/api/v1/coaching.py`, `app/services/coaching_llm_service.py`

**Objectif**: Pendant que l'utilisateur tape, afficher une version professionnelle reformulée.

**Nouveau endpoint**: `POST /api/v1/coaching/reformulate`

```python
class ReformulateRequest(BaseModel):
    session_id: str
    step: str
    raw_text: str  # Texte brut en cours de frappe
    
class ReformulateResponse(BaseModel):
    reformulated_text: str
    confidence: float
    suggestions: List[str] = []  # Suggestions d'amélioration


@router.post("/reformulate", response_model=ReformulateResponse)
async def reformulate_live(request: ReformulateRequest, ...):
    """Reformule le texte brut en version professionnelle (appelé pendant frappe)"""
    
    # Throttling: ne pas appeler trop souvent (frontend gère debounce 500ms)
    if len(request.raw_text) < 20:
        return ReformulateResponse(
            reformulated_text=request.raw_text,
            confidence=0.0,
            suggestions=["Continuez à écrire pour obtenir une reformulation..."]
        )
    
    reformulation = await coaching_llm.reformulate_live(
        step=request.step,
        raw_text=request.raw_text,
        sector=session_data.get("detected_sector", "default")
    )
    
    return ReformulateResponse(**reformulation)
```

**Dans `CoachingLLMService`**:

```python
async def reformulate_live(
    self,
    step: str,
    raw_text: str,
    sector: str
) -> Dict[str, Any]:
    """Reformule le texte brut en version professionnelle"""
    
    prompt = f"""
    REFORMULATION PROFESSIONNELLE - Étape {step.upper()}
    
    Texte brut de l'entrepreneur: "{raw_text}"
    Secteur: {sector}
    
    Transforme ce texte en une formulation professionnelle et inspirante,
    adaptée au contexte entrepreneurial africain.
    
    Règles:
    - Garde l'essence et les idées de l'original
    - Améliore la clarté et l'impact
    - Reste authentique (pas de jargon corporate occidental)
    - Maximum 2-3 phrases
    
    Format JSON:
    {{
        "reformulated_text": "version professionnelle",
        "confidence": 0.0-1.0,
        "suggestions": ["suggestion amélioration si pertinent"]
    }}
    """
    
    return await self.llm_provider.generate_structured(
        prompt=prompt,
        temperature=0.4,
        max_tokens=300
    )
```

---

#### TÂCHE 2.6: Mode "Je ne sais pas" (0.5 jour) ⭐ NIVEAU ARGENT

**Fichiers**: `app/api/v1/coaching.py`, `app/services/coaching_llm_service.py`

**Objectif**: Si l'utilisateur est complètement bloqué, l'IA génère 3 propositions complètes.

**Nouveau endpoint**: `POST /api/v1/coaching/generate-proposals`

```python
class GenerateProposalsRequest(BaseModel):
    session_id: str
    step: str

class Proposal(BaseModel):
    id: str  # "A", "B", "C"
    text: str
    style: str  # "ambitieux", "pragmatique", "communautaire"

class GenerateProposalsResponse(BaseModel):
    intro_message: str
    proposals: List[Proposal]


@router.post("/generate-proposals", response_model=GenerateProposalsResponse)
async def generate_proposals(request: GenerateProposalsRequest, ...):
    """Génère 3 propositions complètes quand l'utilisateur est bloqué"""
    
    proposals = await coaching_llm.generate_complete_proposals(
        step=request.step,
        sector=session_data.get("detected_sector", "default"),
        context=session_data.get("accumulated_context", {}),
        location=session_data.get("location", {"country": "Sénégal", "city": "Dakar"})
    )
    
    return GenerateProposalsResponse(
        intro_message="Pas de problème ! Voici 3 propositions basées sur votre profil. Choisissez celle qui vous parle le plus, ou modifiez-la :",
        proposals=proposals
    )
```

**Dans `CoachingLLMService`**:

```python
async def generate_complete_proposals(
    self,
    step: str,
    sector: str,
    context: Dict[str, Any],
    location: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Génère 3 propositions complètes pour une étape"""
    
    prompt = f"""
    GÉNÉRATION DE PROPOSITIONS - Étape {step.upper()}
    
    Secteur: {sector}
    Localisation: {location.get('city', 'Dakar')}, {location.get('country', 'Sénégal')}
    Contexte précédent: {json.dumps(context, ensure_ascii=False)}
    
    Génère 3 propositions de {step} différentes pour cet entrepreneur africain:
    
    - Option A (Ambitieux): Vision large, impact fort
    - Option B (Pragmatique): Réaliste, concret, atteignable
    - Option C (Communautaire): Centré sur l'impact social/local
    
    Chaque proposition doit être:
    - Complète et prête à être utilisée
    - Adaptée au contexte africain
    - Claire et inspirante
    - 2-3 phrases maximum
    
    Format JSON:
    {{
        "proposals": [
            {{"id": "A", "text": "...", "style": "ambitieux"}},
            {{"id": "B", "text": "...", "style": "pragmatique"}},
            {{"id": "C", "text": "...", "style": "communautaire"}}
        ]
    }}
    """
    
    result = await self.llm_provider.generate_structured(
        prompt=prompt,
        temperature=0.7,  # Plus créatif pour diversité
        max_tokens=800
    )
    
    return result.get("proposals", [])
```

---

#### TÂCHE 2.7: Tests E2E Niveau Argent (0.5-1 jour)

**Nouveau fichier**: `tests/test_e2e/test_coaching_flow.py`

```python
"""Tests E2E du flux coaching complet"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_coaching_flow_restaurant():
    """Test complet: Restaurant Teranga → Site personnalisé"""
    
    async with AsyncClient(base_url="http://localhost:8002") as client:
        # Authentification
        # ... login ...
        
        # 1. Démarrer session coaching
        response = await client.post("/api/v1/coaching/start", headers=headers)
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        assert response.json()["current_step"] == "vision"
        
        # 2. Étape VISION
        response = await client.post("/api/v1/coaching/step", json={
            "session_id": session_id,
            "user_response": "Je veux créer le restaurant Teranga à Dakar pour faire découvrir la cuisine sénégalaise authentique avec une touche moderne"
        }, headers=headers)
        assert response.json()["current_step"] == "mission"
        
        # 3. Étape MISSION
        response = await client.post("/api/v1/coaching/step", json={
            "session_id": session_id,
            "user_response": "Nourrir les familles dakaroises avec des plats traditionnels préparés avec amour et des produits frais locaux"
        }, headers=headers)
        assert response.json()["current_step"] == "clientele"
        
        # 4. Étape CLIENTÈLE
        response = await client.post("/api/v1/coaching/step", json={
            "session_id": session_id,
            "user_response": "Familles classes moyennes, professionnels pour le déjeuner, couples jeunes le week-end"
        }, headers=headers)
        assert response.json()["current_step"] == "differentiation"
        
        # 5. Étape DIFFÉRENCIATION
        response = await client.post("/api/v1/coaching/step", json={
            "session_id": session_id,
            "user_response": "Notre Thieboudienne royal préparé par ma grand-mère, recette familiale de 3 générations"
        }, headers=headers)
        assert response.json()["current_step"] == "offre"
        
        # 6. Étape OFFRE (finale)
        response = await client.post("/api/v1/coaching/step", json={
            "session_id": session_id,
            "user_response": "Déjeuner à 3500 FCFA, dîner à 5000 FCFA, formules familiales, traiteur pour événements"
        }, headers=headers)
        
        # Vérifications finales
        assert response.json()["is_step_complete"] == True
        assert "site_data" in response.json()
        
        site_data = response.json()["site_data"]
        
        # Le site doit avoir le bon nom
        assert site_data["metadata"]["title"] == "Teranga"
        
        # Les couleurs doivent être celles du secteur restaurant
        assert site_data["theme"]["colors"]["primary"] == "#EF4444"  # Rouge restaurant
        
        # Le contenu hero doit être personnalisé (pas générique)
        hero = site_data["pages"][0]["sections"][0]["content"]
        assert "Teranga" in hero["title"] or "cuisine" in hero["title"].lower()
```

---

## 5. FICHIERS À MODIFIER/CRÉER

### Sprint 1 - Core

| Action | Fichier | Priorité |
|--------|---------|----------|
| **CORRIGER** | `app/api/v1/coaching.py` | P0 |
| **CRÉER** | `app/services/prompts_loader.py` | P0 |
| **CRÉER** | `app/services/coaching_llm_service.py` | P0 |
| **MODIFIER** | `app/services/transformer.py` | P0 |
| **MODIFIER** | `app/schemas/coaching.py` | P0 (ajouter site_data, clickable_choices) |
| **MODIFIER** | `app/services/sector_mappings.py` | P1 |

### Sprint 2 - Niveau Argent ⭐

| Action | Fichier | Priorité | Nouveaux Endpoints |
|--------|---------|----------|-------------------|
| **MODIFIER** | `app/api/v1/coaching.py` | P0 | `/help`, `/reformulate`, `/generate-proposals` |
| **MODIFIER** | `app/services/coaching_llm_service.py` | P0 | Nouvelles méthodes IA |
| **MODIFIER** | `app/schemas/coaching.py` | P0 | Nouveaux schemas (Proposal, SocraticQuestion, etc.) |
| **CRÉER** | `tests/test_e2e/test_coaching_flow.py` | P1 | Tests flow complet |
| **CRÉER** | `tests/test_e2e/test_coaching_niveau_argent.py` | P1 | Tests fonctionnalités IA |

---

## 6. DÉPENDANCES ENTRE TÂCHES

```
SPRINT 1 (Core)
═══════════════════════════════════════════════════════════════════════════════

TÂCHE 1.1 (bug fix) ─────────────────────────────────────┐
                                                          │
TÂCHE 1.2 (PromptsLoader) ───┐                           │
                              ├──► TÂCHE 2.1 (intégration)│
TÂCHE 1.3 (CoachingLLMService)┘                          │
                                                          │
TÂCHE 1.4 (Transformer) ─────────────────────────────────┤
                                                          │
TÂCHE 1.5 (Coaching→LangGraph) ──────────────────────────┘

TÂCHE 2.2 (secteurs) ──► Indépendante

SPRINT 2 (Niveau Argent) ⭐
═══════════════════════════════════════════════════════════════════════════════

                        ┌──► TÂCHE 2.3 (Aide-moi + Socratique)
                        │
SPRINT 1 COMPLET ───────┼──► TÂCHE 2.4 (Choix cliquables)
                        │
                        ├──► TÂCHE 2.5 (Reformulation temps réel)
                        │
                        └──► TÂCHE 2.6 (Je ne sais pas)
                                      │
                                      ▼
                              TÂCHE 2.7 (Tests E2E Niveau Argent)
```

---

## 7. TIMELINE SPRINT - NIVEAU ARGENT (8-10 jours)

### Sprint 1: Core (4 jours)

| Jour | Tâches | Livrable |
|------|--------|----------|
| **J1** | 1.1 + 1.2 | Bug fix coaching.py + PromptsLoader |
| **J2** | 1.3 | CoachingLLMService complet |
| **J3** | 1.4 + 1.5 | Transformer connecté + Coaching→LangGraph |
| **J4** | 2.1 + 2.2 | Intégration LLM + Secteurs |

### Sprint 2: Niveau Argent (4-5 jours) ⭐

| Jour | Tâches | Livrable |
|------|--------|----------|
| **J5** | 2.3 | Bouton "Aide-moi" + Questions socratiques |
| **J6** | 2.4 + 2.5 | Choix cliquables + Reformulation temps réel |
| **J7** | 2.6 | Mode "Je ne sais pas" + 3 propositions |
| **J8** | 2.7 | Tests E2E Niveau Argent |
| **J9-10** | Buffer | Polish, debug, optimisation UX |

---

## 8. VALIDATION

### 8.1 Test de Validation Minimal

```bash
# 1. Démarrer services
docker-compose up -d

# 2. Test coaching start
curl -X POST http://localhost:8002/api/v1/coaching/start \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Vérifier que current_step = "vision"
# 4. Soumettre réponses pour chaque étape
# 5. Vérifier site_data dans réponse finale
```

### 8.2 Critères Succès E2E

| Critère | Attendu |
|---------|---------|
| Nom entreprise | "Teranga" extrait et affiché |
| Secteur | "restaurant" détecté automatiquement |
| Couleurs | Rouge/Amber (secteur restaurant) |
| Contenu hero | Personnalisé (pas générique) |
| Flow 5 étapes | Complet sans erreur |

---

## 9. RISQUES ET MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API Deepseek indisponible | Faible | Élevé | Fallback: accepter réponse brute |
| Extraction LLM imprécise | Moyenne | Moyen | Validation humaine optionnelle |
| Temps dépassé | Faible | Moyen | Buffer J6-7 intégré |

---

## 10. NOTES TECHNIQUES

### 10.1 Imports à ajouter

```python
# Dans coaching.py
from app.services.coaching_llm_service import CoachingLLMService
from app.services.prompts_loader import PromptsLoader
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData
```

### 10.2 Schema Coaching à modifier

```python
# Dans app/schemas/coaching.py - Ajouter champ site_data
class CoachingResponse(BaseModel):
    # ... champs existants ...
    site_data: Optional[Dict[str, Any]] = Field(None, description="Site généré si coaching terminé")
```

---

*Work Order rédigé par: Cascade (Tech Lead Genesis)*  
*Date: 19 Décembre 2025*  
*Basé sur: Analyse profonde acquis existants*  
*Supersedes: GEN-WO-001*
