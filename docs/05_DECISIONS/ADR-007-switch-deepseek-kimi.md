# ADR-007 : Switch du Provider LLM de DeepSeek vers Kimi K2

**Date :** 22 décembre 2025  
**Statut :** ✅ Accepté et Implémenté  
**Décideurs :** Product Owner, Tech Lead Genesis AI  
**Tags :** `llm-provider`, `performance`, `kimi`, `deepseek`, `timeout`

---

## Contexte

Lors des tests de génération de sites web via le flow coaching Genesis AI, nous avons rencontré des **timeouts récurrents** avec le provider LLM DeepSeek, particulièrement lors de l'orchestration LangGraph qui coordonne 5 sub-agents pour générer :

- Contenu multilingue (FR + langues locales africaines)
- Recherche de marché et analyse concurrentielle
- Métadonnées SEO
- Logo et assets visuels
- Template et structure de site

**Symptômes observés :**
- Timeout fréquents (>60s) sur l'endpoint `/api/v1/coaching/step` étape finale
- Échecs d'orchestration LangGraph avec DeepSeek
- Contexte insuffisant pour prompts complexes multi-agents

---

## Décision

**Nous passons de DeepSeek à Kimi K2 (Moonshot AI) comme provider LLM par défaut pour le plan BASIC.**

### Choix du modèle : `moonshot-v1-128k`

**Raisons :**
1. **Contexte étendu :** 128K tokens vs limites plus strictes DeepSeek
2. **Performance :** API stable et rapide (testé à 43s pour génération complète)
3. **Support multilingue :** Meilleur support langues africaines (Wolof, Swahili, etc.)
4. **Coût :** Compétitif pour usage BASIC plan

---

## Conséquences

### Positives ✅

1. **Résolution timeouts**
   - Génération site complète : **43 secondes** (vs timeout avec DeepSeek)
   - Orchestration LangGraph 5 agents : 100% succès
   - Zéro timeout observé pendant tests E2E

2. **Amélioration qualité**
   - Meilleure cohérence contenu multilingue
   - Recherche concurrentielle plus approfondie
   - SEO mieux optimisé

3. **Architecture flexible**
   - Configuration modèles via `.env` implémentée
   - Overrides par plan possibles
   - Switch provider facile sans rebuild code

### Négatives ⚠️

1. **Dépendance externe**
   - Ajout d'un nouveau provider tiers (Moonshot AI)
   - Clé API supplémentaire à gérer

2. **Coûts**
   - À monitorer selon usage réel (tokens consommés)

### Risques Atténués 🛡️

- **Fallback :** Configuration maintient DeepSeek disponible
- **Rollback :** Modification simple dans `.env` ou `config.py`
- **Monitoring :** Logs structurés pour tracking performance

---

## Détails d'Implémentation

### Fichiers Modifiés

#### 1. `app/core/providers/factory.py`
```python
_llm_providers: Dict[str, type] = {
    "mock": MockLLMProvider,
    "deepseek": DeepseekProvider,
    "kimi": KimiLLMProvider,  # ← Ajout registration
}
```

**Bug corrigé :** `KimiLLMProvider` était importé mais **pas enregistré** dans le dictionnaire, causant fallback vers Mock.

#### 2. `app/core/providers/config.py`
```python
@classmethod
def _get_plan_mapping(cls) -> Dict[str, Dict[str, str]]:
    from app.config.settings import settings  # Import local évite circular
    return {
        SubscriptionPlan.BASIC: {
            "llm_provider": "kimi",  # ← DeepSeek → Kimi
            "llm_model": settings.PLAN_BASIC_LLM_MODEL or settings.KIMI_MODEL,
            "search_provider": "kimi",
            "image_provider": "dalle-mini"
        },
        # ...
    }
```

**Changements clés :**
- Mapping dynamique via `_get_plan_mapping()` au lieu de constante statique
- Lecture modèles depuis `settings` pour flexibilité `.env`
- Import `settings` déplacé dans fonction (évite import circulaire)

**Bug corrigé :** Conflit paramètre `model` - retiré de `PROVIDER_CONFIGS["kimi"]` car passé explicitement par factory.

#### 3. `app/config/settings.py`
```python
# Modèles par défaut pour chaque provider
KIMI_MODEL: str = "moonshot-v1-128k"
DEEPSEEK_MODEL: str = "deepseek-chat"
OPENAI_MODEL: str = "gpt-4o"
ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

# Overrides optionnels par plan
PLAN_BASIC_LLM_MODEL: Optional[str] = None
PLAN_PRO_LLM_MODEL: Optional[str] = None
PLAN_ENTERPRISE_LLM_MODEL: Optional[str] = None
```

#### 4. Services Nettoyés
- `app/services/coaching_llm_service.py` : Retiré `override_provider="deepseek"`
- `app/core/deep_agents/sub_agents/research.py` : Retiré override
- `app/core/deep_agents/sub_agents/content.py` : Retiré override

---

## Configuration Requise

### Variables `.env`

```bash
# OBLIGATOIRE : Clé API Kimi
KIMI_API_KEY=sk-votre_cle_moonshot_ici
KIMI_BASE_URL=https://api.moonshot.ai

# Modèle par défaut (optionnel - défaut: moonshot-v1-128k)
KIMI_MODEL=moonshot-v1-128k

# Override pour plan BASIC (optionnel)
PLAN_BASIC_LLM_MODEL=
```

**Où obtenir la clé :** https://platform.moonshot.cn/console/api-keys

---

## Résultats de Validation

### Test E2E Complet

**Scénario :** Coaching 5 étapes → Génération site restaurant thiéboudienne

**Métriques :**
```
✅ Étape Vision : 3s (Kimi)
✅ Étape Mission : 3s (Kimi)
✅ Étape Clientèle : 3s (Kimi)
✅ Étape Différenciation : 5s (Kimi - 2 clarifications)
✅ Étape Offre : 4s (Kimi)
✅ Génération site orchestrée : 43s
   - Research Agent : 2035 tokens
   - Content Agent FR : 871 tokens
   - Content Agent WO : 1494 tokens
   - SEO Agent : 879 tokens (DeepSeek)
   - Template Agent : Instant
✅ Total : ~61 secondes (vs timeout DeepSeek)
```

**Logs Validation :**
```
[info] KimiLLMProvider initialized base_url=https://api.moonshot.ai model=moonshot-v1-128k
HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
[info] Kimi generate success tokens_used=2035
[info] LangGraph orchestration completed successfully confidence=1.0 successful_agents=5/5
[info] Site definition generated pages_count=1 sections=5
```

---

## Procédure de Rollback

### Option 1 : Via `.env` (Rapide)

```bash
# Forcer DeepSeek pour plan BASIC
PLAN_BASIC_LLM_MODEL=deepseek-chat
```

Puis : `docker-compose restart genesis-api`

### Option 2 : Via `config.py` (Permanent)

Modifier `app/core/providers/config.py` ligne 45 :
```python
SubscriptionPlan.BASIC: {
    "llm_provider": "deepseek",  # ← kimi → deepseek
    "llm_model": settings.PLAN_BASIC_LLM_MODEL or settings.DEEPSEEK_MODEL,
    # ...
}
```

---

## Documentation Associée

- **Guide Utilisateur :** `docs/02_GUIDES/GUIDE_CONFIGURATION_MODELES_LLM.md`
- **Code Provider Kimi :** `app/core/providers/kimi_llm.py`
- **Factory Pattern :** `app/core/providers/factory.py`

---

## Références

- **API Kimi (Moonshot AI) :** https://platform.moonshot.cn/docs
- **Modèles disponibles :** moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- **Issue Jira :** GEN-XXX (si applicable)

---

## Notes Techniques

### Pattern Architectural

Cette décision introduit un pattern de **configuration dynamique des modèles** réutilisable pour futures évolutions :

1. **Séparation concerns :** Config (settings.py) ↔ Mapping (config.py) ↔ Instanciation (factory.py)
2. **Extensibilité :** Ajout nouveau provider = 3 fichiers touchés seulement
3. **Testabilité :** Overrides `.env` pour tests sans rebuild
4. **Observabilité :** Logs structurés trackent provider/model utilisés

### Leçons Apprises

1. **Vérifier registres :** Toujours confirmer que classe importée est bien enregistrée dans dictionnaire factory
2. **Éviter duplications params :** Ne pas définir `model` à la fois dans config dict ET paramètre explicite
3. **Import circulaires :** Import `settings` dans fonctions si nécessaire (pas top-level dans config.py)
4. **Contexte 128K indispensable :** Pour orchestrations multi-agents complexes avec génération contenu riche

---

**Approuvé par :** Product Owner  
**Implémenté par :** Tech Lead Genesis AI (via Cascade)  
**Date de déploiement :** 22 décembre 2025
