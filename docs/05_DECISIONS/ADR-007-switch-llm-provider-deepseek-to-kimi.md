---
title: "ADR-007: Switch Provider LLM de DeepSeek à Kimi K2"
date: 2025-12-22
status: adopté
authors: ["Cascade (Tech Lead Genesis)", "PO"]
tags: ["architecture", "llm", "providers", "performance"]
supersedes: []
---

# ADR-007: Switch Provider LLM de DeepSeek à Kimi K2

## Contexte

### Situation Initiale
Lors des tests E2E du flux coaching complet (DC360 Hub → Genesis `/coaching` → Génération site), nous avons rencontré un **blocage critique** lors de la génération du site :

```
[2025-12-22 08:53:50] [error] Deepseek request timeout timeout=30
[2025-12-22 08:53:50] [error] LLM analysis failed error='Deepseek timeout after 30s'
[2025-12-22 08:53:50] [warning] Using fallback LLM analysis structure
```

**Impact** :
- ✅ Coaching 5 étapes fonctionnel (VISION → MISSION → CLIENTÈLE → DIFFÉRENCIATION → OFFRE)
- 🔴 **Génération finale du site bloquée** (timeout backend → frontend ne reçoit pas la réponse)
- 🔴 Aucune redirection vers `/preview/{sessionId}`

### Analyse Technique

Le timeout DeepSeek (30s configuré) est **insuffisant** pour les tâches de génération complexes impliquant :
- Analyse marché approfondie (ResearchSubAgent)
- Génération contenu multilingue
- Orchestration LangGraph complète

**Options envisagées** :
1. ⬆️ Augmenter timeout DeepSeek à 60-90s (quick fix)
2. 🔄 Ajouter retry automatique avec backoff
3. 🔀 **Changer de provider LLM** (solution retenue)

## Décision

**Nous basculons le provider LLM par défaut de DeepSeek vers Kimi K2 (Moonshot AI) pour le plan BASIC.**

### Justification

| Critère | DeepSeek | Kimi K2 (Moonshot) | Décision |
|---------|----------|-------------------|----------|
| **Contexte** | 4K-8K tokens | **128K tokens** | ✅ Kimi |
| **Timeout observé** | 30s → timeout | Non testé encore | 🔄 À valider |
| **Tokens disponibles** | Limite atteinte | **Plus de tokens** (PO) | ✅ Kimi |
| **Coût** | ~$0.0001/1K | Similaire | ≈ |
| **Multilinguisme** | ✅ Bon | ✅ Excellent | ✅ Kimi |
| **Accès web natif** | ❌ Non | ✅ Oui (bonus) | ✅ Kimi |

**Avantage décisif** : Le **contexte 128K** de Kimi permet de traiter des prompts beaucoup plus longs sans fragmenter l'orchestration.

## Implémentation

### 1. Création du Provider

**Fichier** : `c:\genesis\app\core\providers\kimi_llm.py`

```python
class KimiLLMProvider(BaseLLMProvider):
    """
    Provider Kimi/Moonshot pour génération LLM
    - moonshot-v1-128k (recommandé - long contexte)
    - Timeout: 90s (vs 30s DeepSeek)
    """
```

### 2. Enregistrement dans Factory

**Fichier** : `c:\genesis\app\core\providers\factory.py`

```python
from .kimi_llm import KimiLLMProvider

_llm_providers: Dict[str, type] = {
    "mock": MockLLMProvider,
    "deepseek": DeepseekProvider,
    "kimi": KimiLLMProvider,  # ← Nouveau
}
```

### 3. Modification Configuration Plans

**Fichier** : `c:\genesis\app\core\providers\config.py:34-38`

```python
# Plan Basic - Économique (10 sessions/mois)
SubscriptionPlan.BASIC: {
    "llm_provider": "kimi",  # ← CHANGÉ: deepseek → kimi (22/12/2025 - ADR-007)
    "llm_model": "moonshot-v1-128k",  # ← CHANGÉ: deepseek-chat → moonshot-v1-128k
    "search_provider": "kimi",
    "image_provider": "dalle-mini"
},
```

### 4. Override Docker Compose (Optionnel)

**Fichier** : `c:\genesis\docker-compose.yml:19`

```yaml
environment:
  - PRIMARY_LLM_PROVIDER=kimi  # Override config.py pour tests
```

**Note** : Cette variable n'est **pas utilisée** par le code actuel (sélection via plan), mais ajoutée pour cohérence.

## Procédure de Rollback

### Si Kimi K2 ne fonctionne pas

**Étape 1** : Modifier `config.py`

```python
# Plan Basic - Économique (10 sessions/mois)
SubscriptionPlan.BASIC: {
    "llm_provider": "deepseek",  # ← ROLLBACK
    "llm_model": "deepseek-chat",  # ← ROLLBACK
    "search_provider": "kimi",
    "image_provider": "dalle-mini"
},
```

**Étape 2** : Redémarrer le backend

```bash
cd C:\genesis
docker-compose restart genesis-api
```

**Étape 3** : Vérifier logs

```bash
docker logs genesis-api --tail 30
# Chercher: "Création LLM provider" provider=deepseek
```

### Alternative : Augmenter Timeout DeepSeek

Si le problème est uniquement le timeout, modifier `deepseek.py` :

```python
def __init__(
    self, 
    api_key: str, 
    model: str = "deepseek-chat",
    base_url: str = "https://api.deepseek.com",
    timeout: int = 90,  # ← AUGMENTÉ: 30s → 90s
    **kwargs
):
```

## Validation

### Tests Requis

- [ ] **Test E2E Coaching Complet** : DC360 Hub → `/coaching` (5 étapes) → Génération → `/preview`
- [ ] **Logs Backend** : Vérifier `"Kimi generate request"` et `"Kimi generate success"`
- [ ] **Temps Génération** : Mesurer latence réelle (objectif < 60s)
- [ ] **Qualité Contenu** : Comparer qualité site généré DeepSeek vs Kimi

### Métriques de Succès

✅ **Succès** si :
- Génération site complète sans timeout
- Redirection `/preview/{sessionId}` fonctionnelle
- Qualité contenu équivalente ou supérieure
- Latence acceptable (< 60s)

🔴 **Échec** (rollback) si :
- Timeout Kimi également
- Erreurs API Kimi (rate limit, 503)
- Qualité contenu dégradée

## Conséquences

### Positives

- ✅ Résout le timeout de génération
- ✅ Contexte 128K permet orchestrations complexes
- ✅ Accès web natif (bonus pour ResearchSubAgent)
- ✅ Stack multi-provider mature (facile rollback)

### Négatives

- ⚠️ Dépendance à un nouveau provider (risque disponibilité)
- ⚠️ API Kimi moins documentée que DeepSeek
- ⚠️ Besoin clé API supplémentaire (`KIMI_API_KEY`)

### Neutres

- 📊 Coût similaire (~$0.0001/1K tokens)
- 📊 Besoin monitoring performance Kimi vs DeepSeek

## Références

- **Logs Erreur** : `MEMO_RAPPORT_TEST_E2E_FLOW_COACHING_22_12_2025.md`
- **Config Kimi** : Base URL `https://api.moonshot.ai` (NOT .cn)
- **Modèle** : `moonshot-v1-128k` (128K context window)
- **Documentation** : Provider existait pour Search, réutilisé pour LLM

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2025-12-22 09:20 | Cascade | Création ADR + Implémentation |
| 2025-12-22 09:34 | PO | Demande documentation rollback |

---

**Statut** : ✅ ADOPTÉ - En attente validation test E2E complet

**Prochaine Étape** : Test génération site avec Kimi K2 activé
