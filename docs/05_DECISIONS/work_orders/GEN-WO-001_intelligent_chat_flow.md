---
title: "Work Order GEN-WO-001: Implémentation Flux Chat Intelligent"
type: work_order
priority: P0 - CRITIQUE
status: draft
created: 2025-12-19
tech_lead: Cascade (Tech Lead Genesis)
assignee: Senior Dev IA
estimated_effort: 3-4 jours
tags: ["langgraph", "deepseek", "chat", "maïeutique", "extraction"]
---

# 🎯 WORK ORDER GEN-WO-001
## Implémentation du Flux Chat Intelligent Maïeutique

---

## 1. CONTEXTE ET PROBLÉMATIQUE

### 1.1 Situation Actuelle (Audit du 19/12/2025)

Le processus Genesis actuel présente des **défaillances critiques** identifiées lors de l'audit E2E :

| Composant | État Actuel | Impact Utilisateur |
|-----------|-------------|-------------------|
| `extract_business_context()` | Valeurs hardcodées | Nom affiché = "Entreprise" au lieu du vrai nom |
| Dialogue chat | Single-shot (1 message → site) | Aucune clarification, site générique |
| Contenu généré | DeepSeek génère mais non utilisé | Contenu répétitif, même texte partout |
| Transformer | Ignore `content_generation` | Site statique et "moche" |

### 1.2 Vision Produit (Rappel PO)

> "Genesis doit être un processus **intelligent et dynamique**. Le chat doit nous assister de bout en bout pour **clarifier notre idée d'entreprise** et à l'issue de la discussion générer un **site sur mesure et optimisé** (design, texte, etc.)"

---

## 2. OBJECTIFS DE CE WORK ORDER

### 2.1 Objectif Principal
Transformer le chat Genesis d'un processus single-shot statique en un **dialogue maïeutique intelligent** qui extrait progressivement les informations business et génère un site véritablement personnalisé.

### 2.2 Critères de Succès (Definition of Done)

- [ ] Le chat pose **minimum 3 questions de clarification** avant génération
- [ ] Le nom de l'entreprise est **correctement extrait** du message utilisateur
- [ ] Le secteur d'activité est **détecté automatiquement** 
- [ ] Les services sont **extraits et listés** dans le site
- [ ] Le contenu généré par DeepSeek est **visible dans le site final**
- [ ] Le design (couleurs) est **adapté au secteur**
- [ ] Test E2E validé avec scénario réel (ex: "Restaurant Teranga à Dakar")

---

## 3. SPÉCIFICATIONS TECHNIQUES

### 3.1 TÂCHE 1: Extraction Intelligente du Contexte Business

**Fichier à modifier**: `app/api/v1/chat.py`

**Fonction actuelle** (lignes 29-44):
```python
def extract_business_context(message: str) -> Dict[str, Any]:
    # TODO: Pour la Phase 2+, utiliser un LLM pour l'extraction
    return {
        "business_name": "Entreprise",  # ❌ HARDCODÉ
        "industry_sector": "default",   # ❌ HARDCODÉ
        ...
    }
```

**Implémentation requise**:
```python
async def extract_business_context(message: str, llm_provider: BaseLLMProvider) -> Dict[str, Any]:
    """
    Extraction intelligente via LLM (Deepseek).
    
    Utilise un prompt structuré pour extraire:
    - business_name: Nom exact de l'entreprise mentionné
    - industry_sector: Secteur d'activité détecté
    - services: Liste des services/produits mentionnés
    - location: Localisation si mentionnée
    - target_market: Clientèle cible si mentionnée
    - tone: Ton souhaité (formel, décontracté, etc.)
    """
    
    extraction_prompt = """
    Analyse ce message d'un entrepreneur et extrait les informations structurées.
    
    MESSAGE: {message}
    
    Réponds en JSON strict avec ces champs:
    {{
        "business_name": "Nom exact de l'entreprise ou null si non mentionné",
        "industry_sector": "Secteur parmi: restaurant, commerce, services, tech, santé, education, autre",
        "services": ["Service 1", "Service 2"],
        "location": {{"city": "", "country": ""}},
        "target_market": "Description clientèle cible",
        "detected_tone": "professionnel|décontracté|luxe|accessible",
        "missing_info": ["Liste des infos manquantes importantes"]
    }}
    """
    
    result = await llm_provider.generate_structured(
        prompt=extraction_prompt.format(message=message),
        response_schema={...},
        temperature=0.3  # Basse pour extraction précise
    )
    
    return result
```

**Tests requis**:
- Input: "Je veux créer un site pour mon restaurant Teranga à Dakar"
- Output attendu: `{"business_name": "Teranga", "industry_sector": "restaurant", "location": {"city": "Dakar", ...}}`

---

### 3.2 TÂCHE 2: Flux Conversationnel Multi-Tour

**Fichier à modifier**: `app/api/v1/chat.py`

**Logique actuelle** (ligne 64):
```python
is_site_request = "site" in request.message.lower() or len(request.message) > 20
if is_site_request:
    # Génère directement le site ❌
```

**Nouvelle logique requise**:

```python
# États de conversation
class ConversationState(Enum):
    INITIAL = "initial"           # Premier message
    CLARIFYING = "clarifying"     # Questions en cours
    READY_TO_GENERATE = "ready"   # Assez d'infos pour générer
    GENERATED = "generated"       # Site généré

async def chat_endpoint(request: ChatRequest, ...):
    # 1. Récupérer état conversation depuis Redis
    session = await redis_fs.get_conversation_state(user_id)
    
    # 2. Extraire contexte du nouveau message
    extracted = await extract_business_context(request.message, llm_provider)
    
    # 3. Merger avec contexte existant
    merged_context = merge_business_context(session.get("context", {}), extracted)
    
    # 4. Évaluer si assez d'infos pour générer
    missing_info = evaluate_completeness(merged_context)
    
    if missing_info:
        # Poser question de clarification
        question = generate_clarification_question(missing_info[0])
        await redis_fs.update_conversation_state(user_id, {
            "state": ConversationState.CLARIFYING,
            "context": merged_context,
            "questions_asked": session.get("questions_asked", 0) + 1
        })
        return ChatResponse(
            response=question,
            brief_generated=False,
            clarification_needed=True,
            missing_fields=missing_info
        )
    
    # 5. Assez d'infos → Générer le site
    # ... (code existant orchestrator)
```

**Questions de clarification à implémenter**:

| Info Manquante | Question Type |
|----------------|---------------|
| `business_name` | "Quel est le nom de votre entreprise ?" |
| `services` | "Quels services ou produits proposez-vous principalement ?" |
| `target_market` | "Qui sont vos clients cibles ?" |
| `location` | "Où êtes-vous situé ?" |
| `tone` | "Quel ton souhaitez-vous pour votre site ? (professionnel, décontracté, etc.)" |

**Règle**: Maximum **5 questions** avant de forcer la génération avec valeurs par défaut intelligentes.

---

### 3.3 TÂCHE 3: Connexion ContentSubAgent → Transformer

**Fichier à modifier**: `app/services/transformer.py`

**Problème actuel**: Le contenu riche généré par `ContentSubAgent` (homepage, about, services) n'est **PAS utilisé** par le transformer.

**Mapping requis**:

```python
def _map_hero_section(self, brief: BusinessBrief, sector_config: Dict) -> Dict[str, Any]:
    """Génère la section Hero en utilisant le contenu LLM généré"""
    
    # Priorité 1: Contenu généré par ContentSubAgent
    if brief.content_generation and isinstance(brief.content_generation, dict):
        homepage = brief.content_generation.get("homepage", {})
        hero = homepage.get("hero_section", {})
        
        if hero:
            return {
                "id": "hero",
                "type": "hero",
                "content": {
                    "title": hero.get("title") or brief.business_name,
                    "subtitle": hero.get("subtitle") or brief.mission,
                    "description": hero.get("hero_paragraph"),
                    "cta": {
                        "text": hero.get("primary_cta", "Nous contacter"),
                        "link": "#contact",
                        "variant": "primary"
                    },
                    "secondary_cta": hero.get("secondary_cta"),
                }
            }
    
    # Fallback: Ancienne logique
    return self._fallback_hero_section(brief, sector_config)
```

**Sections à connecter**:
- `content_generation.homepage.hero_section` → `_map_hero_section()`
- `content_generation.about.story` → `_map_about_section()`
- `content_generation.services.services` → `_map_services_section()`
- `content_generation.contact` → `_map_contact_section()`

---

### 3.4 TÂCHE 4: Adaptation Design par Secteur

**Fichier à modifier**: `app/services/sector_mappings.py`

**Ajouter palettes couleurs sectorielles**:

```python
SECTOR_THEMES = {
    "restaurant": {
        "primary": "#D97706",    # Orange chaud
        "secondary": "#92400E",  # Marron
        "accent": "#FCD34D",     # Jaune doré
        "background": "#FFFBEB"  # Crème
    },
    "tech": {
        "primary": "#3B82F6",    # Bleu tech
        "secondary": "#1E40AF",
        "accent": "#60A5FA",
        "background": "#F8FAFC"
    },
    "santé": {
        "primary": "#10B981",    # Vert santé
        "secondary": "#047857",
        "accent": "#34D399",
        "background": "#ECFDF5"
    },
    "commerce": {
        "primary": "#8B5CF6",    # Violet commerce
        "secondary": "#6D28D9",
        "accent": "#A78BFA",
        "background": "#F5F3FF"
    },
    # ... autres secteurs
}
```

---

## 4. ARCHITECTURE CIBLE

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUX CHAT INTELLIGENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Message ──► extract_business_context() ──► Contexte JSON   │
│        │                    │                         │          │
│        │                    ▼                         ▼          │
│        │         evaluate_completeness() ◄── Redis Session       │
│        │                    │                                    │
│        │         ┌─────────┴─────────┐                          │
│        │         ▼                   ▼                          │
│        │    [Incomplet]         [Complet]                       │
│        │         │                   │                          │
│        │         ▼                   ▼                          │
│        │   Question de        LangGraph                         │
│        │   clarification      Orchestrator                      │
│        │         │                   │                          │
│        │         │                   ▼                          │
│        │         │           ContentSubAgent                    │
│        │         │           (DeepSeek génère)                  │
│        │         │                   │                          │
│        │         │                   ▼                          │
│        │         │           Transformer                        │
│        │         │           (UTILISE le contenu)               │
│        │         │                   │                          │
│        └─────────┴───────────────────┴──► ChatResponse          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. FICHIERS À MODIFIER

| Fichier | Modifications | Priorité |
|---------|---------------|----------|
| `app/api/v1/chat.py` | Extraction LLM + Flux multi-tour | P0 |
| `app/services/transformer.py` | Utiliser content_generation | P0 |
| `app/schemas/chat.py` | Ajouter champs clarification | P1 |
| `app/services/sector_mappings.py` | Palettes couleurs secteur | P1 |
| `app/core/integrations/redis_fs.py` | Méthodes conversation state | P1 |

---

## 6. TESTS DE VALIDATION

### 6.1 Test E2E Scénario Réel

**Input utilisateur**: 
> "Je veux créer un site web pour mon restaurant sénégalais nommé 'Teranga' à Dakar. Nous servons des plats traditionnels avec une touche moderne. Notre spécialité est le Thieboudienne royal."

**Comportement attendu**:
1. Chat extrait: `business_name="Teranga"`, `sector="restaurant"`, `location.city="Dakar"`
2. Chat pose 1-2 questions: "Quels sont vos horaires d'ouverture ?" / "Avez-vous un numéro WhatsApp ?"
3. Génération avec contenu DeepSeek personnalisé
4. Site affiché avec:
   - Titre: "Teranga" (pas "Entreprise")
   - Couleurs chaudes (orange/marron)
   - Textes marketing adaptés restaurant africain
   - Section services avec "Thieboudienne royal"

### 6.2 Tests Unitaires

```python
# tests/test_api/test_chat_extraction.py

async def test_extract_business_name():
    result = await extract_business_context(
        "Je veux un site pour mon entreprise TechAfrique",
        mock_llm
    )
    assert result["business_name"] == "TechAfrique"

async def test_extract_sector_restaurant():
    result = await extract_business_context(
        "Mon restaurant Chez Fatou propose des plats sénégalais",
        mock_llm
    )
    assert result["industry_sector"] == "restaurant"
    assert result["business_name"] == "Chez Fatou"

async def test_missing_info_detection():
    result = await extract_business_context(
        "Je veux un site",  # Message trop vague
        mock_llm
    )
    assert "business_name" in result["missing_info"]
    assert "industry_sector" in result["missing_info"]
```

---

## 7. CONTRAINTES ET GUIDELINES

### 7.1 Contraintes Techniques
- **LLM Provider**: Utiliser Deepseek (primary) via `ProviderFactory`
- **Temperature**: 0.3 pour extraction (précision), 0.7 pour contenu (créativité)
- **Timeout**: Max 30s par appel LLM
- **Fallback**: Si extraction échoue, utiliser heuristiques simples (regex)

### 7.2 Guidelines Code
- Suivre patterns existants dans `app/core/deep_agents/`
- Logging structuré avec `structlog`
- Docstrings complètes pour fonctions publiques
- Type hints obligatoires
- Tests pour chaque nouvelle fonction

### 7.3 Sécurité
- Ne JAMAIS exposer les prompts LLM dans les réponses API
- Valider/sanitizer tous les inputs utilisateur
- Limiter taille messages (max 2000 chars)

---

## 8. LIVRABLES ATTENDUS

1. **Code modifié** avec commits atomiques et messages clairs
2. **Tests unitaires** pour nouvelles fonctions
3. **Test E2E** validant le scénario complet
4. **PR** avec description des changements

---

## 9. TIMELINE ESTIMÉE

| Jour | Tâche | Livrable |
|------|-------|----------|
| J1 | Tâche 1: Extraction intelligente | Fonction `extract_business_context` LLM |
| J2 | Tâche 2: Flux multi-tour | Conversation state + questions |
| J3 | Tâche 3: Connexion ContentSubAgent | Transformer utilise contenu |
| J3 | Tâche 4: Design secteur | Palettes couleurs |
| J4 | Tests + Polish + PR | Livrable final |

---

## 10. VALIDATION

**Tech Lead (Cascade)**: Ce work order sera validé par test E2E Chrome DevTools MCP après implémentation.

**Product Owner**: Validation finale du résultat visuel et de l'expérience utilisateur.

---

*Work Order rédigé par: Cascade (Principal Architect & Tech Lead)*
*Date: 19 Décembre 2025*
*Référence Audit: AUDIT-GENESIS-2025-12-19*
