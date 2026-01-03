---
title: "WO-009 - Finalisation & Stabilisation Phase 2"
tags: ["phase2", "seo", "template", "design", "tests", "kimi"]
status: "ready"
date: "2025-12-25"
priority: "P0 - Critique pour Phase 2"
estimated_effort: "8-11 jours"
assigned_to: "Dev Senior"
validated_by: "Tech Lead Genesis AI"
---

# WO-009 : Finalisation & Stabilisation Phase 2

**Créé par :** Tech Lead Genesis AI  
**Date :** 25/12/2025 10:15 UTC  
**Assigné à :** Dev Senior  
**Priorité :** 🔴 P0 - CRITIQUE  
**Complexité :** HAUTE  
**Temps Estimé :** 8-11 jours  

---

## 📋 Contexte Critique

### 🚨 RECTIFICATION MAJEURE : Phase 2 = 85% Complète

**Contrairement à la documentation `PHASE1-COMPLETION-REPORT.md`**, l'analyse approfondie révèle que **Phase 2 est déjà ~85% implémentée**.

**Ce qui EXISTE déjà (Production Ready) :**
- ✅ **LogoAgent** avec DALL-E 3 (236 lignes, cache Redis, fallback)
- ✅ **LangGraphOrchestrator** complet (308 lignes, 5 agents intégrés)
- ✅ **SiteRenderer Frontend** complet (tests Jest inclus)
- ✅ **API Business** fonctionnelle (`POST /brief/generate`, `GET /brief/{id}`)
- ✅ **API Sites** (`GET /{site_id}/preview`) - EXISTE dans `app/api/v1/sites.py`

**Ce qui nécessite CORRECTION (Gaps Réels) :**
1. ❌ **SeoAgent** utilise Tavily au lieu de Kimi search (décision passée non appliquée)
2. ❌ **TemplateAgent** logique basique → besoin thèmes IA élaborés
3. ❌ **Tests Backend** instables (401 errors, imports manquants)
4. ❌ **Profile Test Docker** absent

---

## 🎯 Objectifs Phase 2 (Finalisation)

**PAS d'implémentation from scratch**, mais **finalisation et stabilisation** :

1. Corriger SeoAgent pour utiliser Kimi search (déjà implémenté)
2. Refactorer TemplateAgent pour thèmes IA élaborés
3. Stabiliser tests backend (100% pass rate)
4. Créer profile test Docker
5. Documentation technique complète

---

## 📝 Tâches Détaillées

### 🔥 P0 - Critiques (Bloquants Phase 2)

#### Tâche 1 : Corriger SeoAgent - Remplacer Tavily par Kimi Search

**Priorité :** 🔴 CRITIQUE  
**Temps Estimé :** 2-3 heures  
**Fichier :** `app/core/agents/seo.py`

**Contexte :**
Une décision passée a été prise de remplacer Tavily par Moonshot Kimi2 search pour le SeoAgent. `KimiProvider` est **déjà implémenté** dans `app/core/providers/kimi.py` et utilisé par `ResearchSubAgent`. Cependant, `SeoAgent` utilise toujours `TavilyClient`.

**État Actuel (Ligne 22-25) :**
```python
from app.core.integrations.tavily import TavilyClient

class SeoAgent:
    def __init__(self):
        self.tavily_client = TavilyClient()  # ← À REMPLACER
        self.llm_provider = DeepseekProvider(...)
```

**Modification Requise :**
```python
from app.core.providers.kimi import KimiProvider
from app.config.settings import settings

class SeoAgent:
    def __init__(self):
        self.kimi_provider = KimiProvider(
            api_key=settings.KIMI_API_KEY,
            model="moonshot-v1-8k"  # Recommandé pour search
        )
        self.llm_provider = DeepseekProvider(
            api_key=settings.DEEPSEEK_API_KEY
        )
```

**Adapter la méthode `run()` (Ligne 72-74) :**
```python
# AVANT :
competitive_data = await self.tavily_client.search_market(
    query=search_query
)

# APRÈS :
competitive_data = await self.kimi_provider.search(
    query=search_query,
    max_results=10,
    search_depth="basic"
)
```

**Validation :**
- [ ] Import `KimiProvider` au lieu de `TavilyClient`
- [ ] Instancier `KimiProvider` avec `KIMI_API_KEY`
- [ ] Adapter appels `search()` avec nouvelle signature
- [ ] Tester génération SEO avec Kimi (vérifier qualité résultats)
- [ ] Fallback si Kimi échoue (déjà géré ligne 127-140)

---

#### Tâche 2 : Refactorer TemplateAgent - Thèmes IA Élaborés

**Priorité :** 🔴 CRITIQUE  
**Temps Estimé :** 1-2 jours  
**Fichier :** `app/core/agents/template.py`

**Problème Actuel :**
`TemplateAgent` utilise une logique ultra-basique (60 lignes) :
- 4 templates hardcodés
- Sélection par mot-clé simple (`if "e-commerce" in business_type`)
- **Aucune IA** pour génération thèmes élaborés
- Pas de couleurs/fonts/styles dynamiques
- **Résultat :** Sites avec designs statiques et moches

**Besoin Utilisateur :**
Utiliser la **puissance de l'IA** pour créer des thèmes hyper élaborés, adaptés au secteur d'activité avec :
- Palette couleurs professionnelle
- Sélection fonts appropriées
- Style visuel adapté (moderne, élégant, minimaliste, audacieux, etc.)
- Layout structure intelligente

**Nouvelle Architecture TemplateAgent :**

```python
import structlog
from typing import Dict, Any
from app.core.providers.deepseek import DeepseekProvider
from app.core.providers.kimi import KimiProvider
from app.config.settings import settings

logger = structlog.get_logger(__name__)

class TemplateAgent:
    """
    Agent IA spécialisé dans la génération de thèmes élaborés.
    
    Features:
    - Analyse secteur activité via LLM
    - Génération palette couleurs contextuelle
    - Sélection fonts professionnelles
    - Recommandation style visuel adapté
    - Recherche références design via Kimi
    """
    
    def __init__(self):
        self.llm_provider = DeepseekProvider(
            api_key=settings.DEEPSEEK_API_KEY
        )
        self.kimi_provider = KimiProvider(
            api_key=settings.KIMI_API_KEY,
            model="moonshot-v1-8k"
        )
        logger.info("TemplateAgent initialized with AI theme generation")
    
    async def run(
        self,
        business_name: str,
        industry_sector: str,
        brand_personality: str = "professional",
        target_audience: str = ""
    ) -> Dict[str, Any]:
        """
        Génère un thème élaboré via IA.
        
        Args:
            business_name: Nom de l'entreprise
            industry_sector: Secteur d'activité
            brand_personality: Personnalité marque (professional, creative, bold, elegant)
            target_audience: Audience cible (optionnel)
        
        Returns:
            Dict contenant:
                - template_id: ID template sélectionné
                - template_name: Nom template
                - theme: Thème complet (couleurs, fonts, style)
                - layout_structure: Structure recommandée
                - design_rationale: Justification choix design
        """
        try:
            logger.info(
                "Generating AI-powered theme",
                business_name=business_name,
                industry_sector=industry_sector
            )
            
            # 1. Recherche références design via Kimi
            design_references = await self._search_design_references(
                industry_sector=industry_sector
            )
            
            # 2. Génération thème via LLM
            theme_data = await self._generate_theme_via_llm(
                business_name=business_name,
                industry_sector=industry_sector,
                brand_personality=brand_personality,
                target_audience=target_audience,
                design_references=design_references
            )
            
            # 3. Sélection template adapté
            template_selection = self._select_template_for_theme(
                theme_data=theme_data,
                industry_sector=industry_sector
            )
            
            # 4. Enrichir avec métadonnées
            result = {
                **template_selection,
                "theme": theme_data,
                "metadata": {
                    "agent": "TemplateAgent",
                    "ai_generated": True,
                    "industry_sector": industry_sector,
                    "brand_personality": brand_personality
                }
            }
            
            logger.info(
                "AI theme generated successfully",
                template_id=result["template_id"],
                primary_color=theme_data.get("colors", {}).get("primary")
            )
            
            return result
            
        except Exception as e:
            logger.error("Error during AI theme generation", error=str(e))
            return self._get_fallback_theme(industry_sector)
    
    async def _search_design_references(self, industry_sector: str) -> Dict[str, Any]:
        """Recherche références design via Kimi pour inspiration."""
        try:
            search_query = f"best website design trends {industry_sector} 2025 professional modern"
            results = await self.kimi_provider.search(
                query=search_query,
                max_results=5,
                search_depth="basic"
            )
            return results
        except Exception as e:
            logger.warning("Design references search failed", error=str(e))
            return {}
    
    async def _generate_theme_via_llm(
        self,
        business_name: str,
        industry_sector: str,
        brand_personality: str,
        target_audience: str,
        design_references: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère thème complet via LLM Deepseek."""
        
        prompt = self._build_theme_generation_prompt(
            business_name=business_name,
            industry_sector=industry_sector,
            brand_personality=brand_personality,
            target_audience=target_audience,
            design_references=design_references
        )
        
        theme_result = await self.llm_provider.generate_structured(
            prompt=prompt,
            response_schema={
                "colors": {
                    "primary": "string (hex code)",
                    "secondary": "string (hex code)",
                    "accent": "string (hex code)",
                    "background": "string (hex code)",
                    "text": "string (hex code)"
                },
                "fonts": {
                    "heading": "string (font family)",
                    "body": "string (font family)",
                    "accent": "string (font family, optional)"
                },
                "style": {
                    "visual_style": "string (modern, elegant, minimalist, bold, creative)",
                    "border_radius": "string (none, subtle, rounded, pill)",
                    "spacing": "string (compact, balanced, generous)",
                    "shadows": "boolean (use shadows or not)"
                },
                "layout_structure": {
                    "header_style": "string (minimal, classic, sticky)",
                    "hero_type": "string (full-screen, split, minimal)",
                    "section_layout": "string (single-column, two-column, grid)"
                },
                "design_rationale": "string (explain design choices)"
            }
        )
        
        return theme_result
    
    def _build_theme_generation_prompt(
        self,
        business_name: str,
        industry_sector: str,
        brand_personality: str,
        target_audience: str,
        design_references: Dict[str, Any]
    ) -> str:
        """Construit prompt optimisé pour génération thème."""
        
        prompt_parts = [
            "Tu es un expert en design web et UX, spécialisé dans la création de thèmes professionnels.",
            f"\n**Entreprise :** {business_name}",
            f"**Secteur :** {industry_sector}",
            f"**Personnalité de marque :** {brand_personality}",
        ]
        
        if target_audience:
            prompt_parts.append(f"**Audience cible :** {target_audience}")
        
        if design_references and isinstance(design_references, dict):
            prompt_parts.append("\n**Tendances design 2025 :** Références disponibles pour inspiration.")
        
        prompt_parts.extend([
            "\n**Mission :** Créer un thème web élaboré, moderne et professionnel.",
            "\n**Exigences :**",
            "1. **Palette couleurs :** Harmonieuse, adaptée au secteur, accessible (WCAG AAA)",
            "2. **Typographie :** Fonts professionnelles (Google Fonts ou system fonts)",
            "3. **Style visuel :** Cohérent avec personnalité marque",
            "4. **Layout :** Structure moderne, responsive-first",
            "5. **Justification :** Expliquer choix design",
            "\n**Best practices :**",
            "- Couleur primaire forte, identifiable",
            "- Contraste texte/background optimal",
            "- Hiérarchie visuelle claire",
            "- Espacement généreux pour respiration",
            "- Mobile-first approch"
        ])
        
        return "\n".join(prompt_parts)
    
    def _select_template_for_theme(
        self,
        theme_data: Dict[str, Any],
        industry_sector: str
    ) -> Dict[str, str]:
        """Sélectionne template ID adapté au thème généré."""
        
        # Mapping style visuel → template
        style = theme_data.get("style", {}).get("visual_style", "modern")
        
        template_map = {
            "modern": {"id": "modern_business_01", "name": "Modern Business Pro"},
            "elegant": {"id": "elegant_premium_02", "name": "Elegant Premium"},
            "minimalist": {"id": "minimalist_clean_03", "name": "Minimalist Clean"},
            "bold": {"id": "bold_creative_04", "name": "Bold Creative"},
            "creative": {"id": "creative_portfolio_05", "name": "Creative Portfolio"}
        }
        
        return template_map.get(style, template_map["modern"])
    
    def _get_fallback_theme(self, industry_sector: str) -> Dict[str, Any]:
        """Retourne thème basique si LLM échoue."""
        return {
            "template_id": "modern_business_01",
            "template_name": "Modern Business (Fallback)",
            "theme": {
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#1E40AF",
                    "accent": "#60A5FA",
                    "background": "#FFFFFF",
                    "text": "#1F2937"
                },
                "fonts": {
                    "heading": "Inter",
                    "body": "Inter"
                },
                "style": {
                    "visual_style": "modern",
                    "border_radius": "rounded",
                    "spacing": "balanced",
                    "shadows": True
                }
            },
            "metadata": {
                "agent": "TemplateAgent",
                "fallback": True,
                "industry_sector": industry_sector
            }
        }
```

**Validation :**
- [ ] Refactorer `template.py` avec nouvelle classe IA
- [ ] Implémenter `_search_design_references()` avec Kimi
- [ ] Implémenter `_generate_theme_via_llm()` avec Deepseek
- [ ] Tester génération thème pour différents secteurs
- [ ] Valider qualité couleurs/fonts/style générés
- [ ] Vérifier fallback si LLM échoue
- [ ] Tests unitaires pour TemplateAgent

---

#### Tâche 3 : Stabiliser Tests Backend

**Priorité :** 🔴 CRITIQUE  
**Temps Estimé :** 4-5 heures  
**Fichiers :** `tests/test_api/`, `conftest.py`, `docker-compose.yml`

**Problèmes Identifiés :**
1. ❌ Import `json` manquant dans `tests/test_api/test_coaching.py` (ligne ~4)
2. ❌ Erreurs 401 vs 200 dans `tests/test_api/test_business.py` (auth mocks incorrects)
3. ❌ Configuration auth headers incohérente dans `conftest.py`
4. ❌ Profile test Docker absent (tests locaux vs app containerisée)

**Sous-tâche 3.1 : Fixer Imports Manquants**

```python
# Dans tests/test_api/test_coaching.py (ligne 4)
import json  # ← AJOUTER
```

**Sous-tâche 3.2 : Corriger Auth Mocks**

```python
# Dans tests/conftest.py
@pytest.fixture
def auth_headers(test_user_token):
    """Headers d'authentification valides pour tests."""
    return {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def test_user_token(test_db):
    """Génère JWT token valide pour tests."""
    # Créer user test
    user = User(email="test@example.com", id=1)
    test_db.add(user)
    test_db.commit()
    
    # Générer token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.id)
    return token
```

**Sous-tâche 3.3 : Créer Profile Test Docker**

```yaml
# Dans docker-compose.yml
services:
  # ... services existants
  
  # Service test isolé
  genesis-test:
    build:
      context: .
      dockerfile: Dockerfile
    profiles:
      - test
    command: pytest -v tests/
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@test-db:5432/genesis_test
      - REDIS_URL=redis://redis:6379/1
      - ENV=test
    depends_on:
      - test-db
      - redis
    volumes:
      - ./tests:/app/tests
      - ./app:/app/app
  
  test-db:
    image: postgres:15-alpine
    profiles:
      - test
    environment:
      - POSTGRES_DB=genesis_test
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5433:5432"
```

**Validation :**
- [ ] Fixer tous les imports manquants
- [ ] Corriger auth mocks dans `conftest.py`
- [ ] Créer profile test dans `docker-compose.yml`
- [ ] Exécuter `docker-compose --profile test up genesis-test`
- [ ] Atteindre **100% pass rate** sur `pytest -v tests/`
- [ ] Documenter commande test Docker

---

### 📚 P1 - Importants (Post-Critique)

#### Tâche 4 : Améliorer Exceptions avec Codes Erreurs

**Priorité :** 🟡 MOYEN  
**Temps Estimé :** 1-2 heures  
**Fichier :** `app/utils/exceptions.py`

**État Actuel (Trop Simpliste) :**
```python
class GenesisAIException(Exception):
    pass  # ← Pas de structure
```

**Amélioration Requise :**
```python
class GenesisAIException(Exception):
    """Exception de base pour Genesis AI avec codes erreurs structurés."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        details: dict = None,
        status_code: int = 500
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convertir en dict pour réponse API."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }

class AgentException(GenesisAIException):
    """Exception spécifique aux agents."""
    def __init__(self, message: str, agent_name: str, details: dict = None):
        super().__init__(
            error_code=f"AGENT_{agent_name.upper()}_ERROR",
            message=message,
            details=details,
            status_code=500
        )

class OrchestratorException(GenesisAIException):
    """Exception orchestrateur LangGraph."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            error_code="ORCHESTRATOR_ERROR",
            message=message,
            details=details,
            status_code=500
        )

class ProviderException(GenesisAIException):
    """Exception providers externes (DALL-E, Kimi, etc.)."""
    def __init__(self, message: str, provider_name: str, details: dict = None):
        super().__init__(
            error_code=f"PROVIDER_{provider_name.upper()}_ERROR",
            message=message,
            details=details,
            status_code=503
        )
```

**Validation :**
- [ ] Refactorer `exceptions.py` avec structure enrichie
- [ ] Migrer tous les agents pour utiliser nouvelles exceptions
- [ ] Tester gestion erreurs avec codes appropriés
- [ ] Documenter codes erreurs dans OpenAPI

---

#### Tâche 5 : Documentation Technique Complète

**Priorité :** 🟡 MOYEN  
**Temps Estimé :** 2-3 heures

**Livrables :**
1. **TECH_LEAD_HANDOVER.md** - Guide complet pour futur tech lead
2. **API_DOCUMENTATION.md** - Tous endpoints documentés
3. **AGENT_ARCHITECTURE.md** - Architecture agents + orchestrateur
4. **DEPLOYMENT_GUIDE.md** - Déploiement Docker production

---

## 📊 Critères d'Acceptation Phase 2

### Backend ✅ Finalisé
- [x] LogoAgent DALL-E 3 (déjà fait)
- [x] LangGraphOrchestrator (déjà fait)
- [ ] SeoAgent avec Kimi search (au lieu de Tavily)
- [ ] TemplateAgent avec thèmes IA élaborés
- [ ] Tests backend 100% pass rate

### Frontend ✅ Complet
- [x] SiteRenderer avec tous les blocs
- [x] Preview toolbar
- [x] Route `/preview/[siteId]`
- [x] Tests Jest

### Tests ✅ Stabilisés
- [ ] Tests backend 100% pass
- [ ] Profile test Docker opérationnel
- [ ] Commandes test documentées

### Documentation ✅ Complète
- [ ] TECH_LEAD_HANDOVER.md
- [ ] API_DOCUMENTATION.md
- [ ] AGENT_ARCHITECTURE.md

---

## 🚀 Plan d'Exécution

### Jour 1-2 : Corrections Critiques SEO + Template (P0)
- ✅ Corriger SeoAgent → Kimi search (2-3h)
- ✅ Refactorer TemplateAgent → Thèmes IA (1-2 jours)

### Jour 3-4 : Stabilisation Tests (P0)
- ✅ Fixer imports + auth mocks (2-3h)
- ✅ Créer profile test Docker (1-2h)
- ✅ Atteindre 100% pass rate pytest (2-3h)

### Jour 5-6 : Polish + Documentation (P1)
- ✅ Améliorer exceptions (1-2h)
- ✅ Documentation technique complète (2-3h)
- ✅ Tests E2E validation finale (2-3h)

**Total Phase 2 : 8-11 jours**

---

## 📚 Ressources Disponibles

### Code Existant (À Réutiliser)
- **KimiProvider** : `app/core/providers/kimi.py` (443 lignes, production-ready)
- **DeepseekProvider** : `app/core/providers/deepseek.py` (pour TemplateAgent LLM)
- **LogoAgent** : `app/core/agents/logo.py` (exemple d'agent IA complet)
- **SeoAgent actuel** : `app/core/agents/seo.py` (structure à conserver, remplacer Tavily)

### Documentation
- **PHASE2-STATE-ANALYSIS-25DEC2025.md** : Analyse complète état réel Phase 2
- **WORK_ORDER_CORRECTION_PHASE2_FRESH.md** : Diagnostic précis gaps
- **GEN-WO-004_sprint3_site_complet.md** : ⚠️ Partiellement obsolète (agents déjà faits)

---

## ⚠️ Attention - Éviter Ces Erreurs

### ❌ NE PAS FAIRE
- ❌ Réimplémenter LogoAgent (déjà fait avec DALL-E 3)
- ❌ Réimplémenter SiteRenderer (déjà fait et testé)
- ❌ Créer nouveau orchestrateur (LangGraph déjà complet)
- ❌ Créer endpoints `/api/v1/sites/` (déjà fait dans `sites.py`)

### ✅ FAIRE EN PRIORITÉ
1. Corriger SeoAgent (Tavily → Kimi)
2. Refactorer TemplateAgent (basique → IA élaboré)
3. Stabiliser tests backend
4. Documenter

---

## 🎯 Validation Finale

**Phase 2 complète si :**
- ✅ SeoAgent utilise Kimi search
- ✅ TemplateAgent génère thèmes IA élaborés
- ✅ Tests backend 100% pass rate
- ✅ Profile test Docker fonctionnel
- ✅ Documentation technique complète
- ✅ E2E DC360 → Genesis → Coaching → Site Preview avec **beau design**

---

## 🚀 ENRICHISSEMENT PHASE 2 PREMIUM (Ajout 26/12/2025)

### ⚠️ DÉCOUVERTE MAJEURE : Capacité Images IA Sous-Exploitée

**Constat :**
- `DALLEImageProvider.generate_image()` **EXISTE** dans `app/core/providers/dalle.py` (412 lignes)
- Peut générer N'IMPORTE QUELLE image (pas seulement logos)
- **MAIS** : Actuellement utilisé UNIQUEMENT par LogoAgent !
- **Résultat** : Sites avec placeholders statiques au lieu d'images IA personnalisées

**Frontend DÉJÀ PRÊT pour images dynamiques :**
- `HeroBlock.tsx` : champ `image` (side) + `overlay` (background)
- `ServicesBlock.tsx` : `service.image` pour chaque service
- `FeaturesBlock.tsx` : `feature.image` pour chaque feature
- `GalleryBlock.tsx` : galerie complète

---

### 🔥 Tâche 5 : Créer ImageAgent - Génération Images Contenu IA (P0 - NOUVEAU)

**Priorité :** 🔴 CRITIQUE pour effet "WHAOUUUU"  
**Temps Estimé :** 1-2 jours  
**Fichier :** `app/core/agents/image.py` (NOUVEAU)

**Objectif :** Générer toutes les images du site via DALL-E 3 (pas seulement le logo).

**Structure ImageAgent :**

```python
# app/core/agents/image.py
import structlog
import hashlib
from typing import Dict, Any, Optional
from app.core.providers.dalle import DALLEImageProvider
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.config.settings import settings

logger = structlog.get_logger(__name__)

class ImageAgent:
    """
    Agent spécialisé génération images contenu via DALL-E 3.
    
    Features:
    - Hero images personnalisées selon secteur
    - Illustrations services
    - Backgrounds thématiques
    - Cache Redis (TTL 7 jours)
    - Fallback images stock
    """
    
    FALLBACK_IMAGES = {
        "hero": "https://images.unsplash.com/photo-1557804506-669a67965ba0",
        "service": "https://images.unsplash.com/photo-1551434678-e076c223a692",
        "feature": "https://images.unsplash.com/photo-1460925895917-afdab827c52f"
    }
    
    def __init__(self):
        self.dalle_provider = DALLEImageProvider(
            api_key=settings.OPENAI_API_KEY,
            model="dall-e-3"
        )
        self.redis_fs = RedisVirtualFileSystem()
        logger.info("ImageAgent initialized with DALL-E 3")
    
    async def run(
        self,
        business_name: str,
        industry_sector: str,
        image_type: str,  # "hero", "service", "feature", "gallery"
        context: Optional[str] = None,
        style: str = "professional",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Génère image contenu adaptée au business.
        
        Args:
            business_name: Nom entreprise
            industry_sector: Secteur activité
            image_type: Type image (hero, service, feature, gallery)
            context: Contexte additionnel (ex: "livraison rapide")
            style: Style visuel
            use_cache: Utiliser cache Redis
        
        Returns:
            Dict avec image_url, metadata, cached
        """
        try:
            # 1. Vérifier cache
            cache_key = self._generate_cache_key(
                business_name, industry_sector, image_type, context
            )
            
            if use_cache:
                cached = await self._get_cached_image(cache_key)
                if cached:
                    return {**cached, "cached": True}
            
            # 2. Construire prompt optimisé
            prompt = self._build_image_prompt(
                business_name, industry_sector, image_type, context, style
            )
            
            # 3. Générer via DALL-E
            size = self._get_optimal_size(image_type)
            result = await self.dalle_provider.generate_image(
                prompt=prompt,
                size=size,
                quality="hd" if image_type == "hero" else "standard"
            )
            
            # 4. Cacher et retourner
            await self._cache_image(cache_key, result)
            
            logger.info(
                "Image generated successfully",
                image_type=image_type,
                business=business_name
            )
            
            return {
                "image_url": result["image_url"],
                "metadata": result["metadata"],
                "cached": False
            }
            
        except Exception as e:
            logger.error("Image generation failed", error=str(e))
            return {
                "image_url": self.FALLBACK_IMAGES.get(image_type, self.FALLBACK_IMAGES["hero"]),
                "metadata": {"fallback": True, "error": str(e)},
                "cached": False
            }
    
    def _build_image_prompt(
        self,
        business_name: str,
        industry_sector: str,
        image_type: str,
        context: Optional[str],
        style: str
    ) -> str:
        """Construit prompt optimisé selon type image."""
        
        base_prompts = {
            "hero": f"Professional hero image for {business_name}, a {industry_sector} business. {context or 'Business activity in action'}. Style: {style}, modern, high-quality. No text, no logos. Photorealistic. Wide format.",
            
            "service": f"Professional illustration for service: {context or 'business service'}. {industry_sector} business. Style: {style}, clean. No text. Square format.",
            
            "feature": f"Abstract visual representing: {context or 'business feature'}. For {industry_sector}. Style: modern, {style}, subtle gradients. No text.",
            
            "gallery": f"Professional photo of {context or industry_sector + ' business environment'}. Realistic, well-lit. No text, no logos."
        }
        
        return base_prompts.get(image_type, base_prompts["gallery"])
    
    def _get_optimal_size(self, image_type: str) -> str:
        """Retourne taille optimale DALL-E selon type."""
        sizes = {
            "hero": "1792x1024",      # Wide pour hero
            "service": "1024x1024",   # Carré
            "feature": "1024x1024",   # Carré
            "gallery": "1024x1024"    # Carré
        }
        return sizes.get(image_type, "1024x1024")
    
    def _generate_cache_key(self, *args) -> str:
        """Génère clé cache unique."""
        content = "_".join(str(a) for a in args if a)
        return f"image:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _get_cached_image(self, cache_key: str) -> Optional[Dict]:
        """Récupère image depuis cache."""
        # Implémentation similaire à LogoAgent
        pass
    
    async def _cache_image(self, cache_key: str, data: Dict, ttl: int = 604800):
        """Cache image (TTL 7 jours)."""
        # Implémentation similaire à LogoAgent
        pass
```

**Intégration Orchestrateur :**

```python
# Dans langgraph_orchestrator.py - Ajouter après logo_agent

from app.core.agents.image import ImageAgent

class LangGraphOrchestrator:
    def __init__(self):
        # ... agents existants
        self.image_agent = ImageAgent()  # ← NOUVEAU
        
        # Ajouter node dans graph
        workflow.add_node("images", self.run_image_agent)
        workflow.add_edge("logo", "images")  # Après logo
        workflow.add_edge("images", "seo")   # Avant SEO
    
    async def run_image_agent(self, state: AgentState) -> AgentState:
        """Génère toutes les images du site."""
        brief = state['business_brief']
        images = {}
        
        # Hero image
        hero = await self.image_agent.run(
            business_name=brief['business_name'],
            industry_sector=brief['industry_sector'],
            image_type="hero",
            context=brief.get('value_proposition')
        )
        images['hero_image'] = hero['image_url']
        
        # Service images (max 4)
        services = brief.get('services', [])[:4]
        service_images = []
        for svc in services:
            title = svc.get('title', svc) if isinstance(svc, dict) else svc
            result = await self.image_agent.run(
                business_name=brief['business_name'],
                industry_sector=brief['industry_sector'],
                image_type="service",
                context=title
            )
            service_images.append(result['image_url'])
        images['service_images'] = service_images
        
        return {"image_generation": images}
```

**Coût API par site :**
- Hero (1792x1024 HD) : ~$0.12
- 4 Services (1024x1024) : ~$0.16
- **Total images : ~$0.28** (très rentable vs valeur perçue)

**Validation :**
- [ ] Créer `app/core/agents/image.py`
- [ ] Intégrer dans orchestrateur (nouveau node)
- [ ] Modifier transformer pour mapper images vers blocs
- [ ] Tester génération images différents secteurs
- [ ] Vérifier fallback si DALL-E échoue
- [ ] Tests unitaires ImageAgent

---

### 🎨 Tâche 6 : Animations & Micro-interactions (P1 - NOUVEAU)

**Priorité :** 🟡 MOYEN (après tâches P0)  
**Temps Estimé :** 4-6 heures  
**Fichiers :** Frontend components

**Objectif :** Ajouter animations subtiles au scroll pour effet moderne.

**Implémentation :**

```tsx
// components/AnimatedSection.tsx
'use client';

import { useEffect, useRef, useState } from 'react';

interface AnimatedSectionProps {
  children: React.ReactNode;
  animation?: 'fade' | 'slide-up' | 'scale';
  delay?: number;
}

export default function AnimatedSection({
  children,
  animation = 'fade',
  delay = 0
}: AnimatedSectionProps) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  const baseClasses = 'transition-all duration-700 ease-out';
  const animationClasses = {
    'fade': isVisible ? 'opacity-100' : 'opacity-0',
    'slide-up': isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8',
    'scale': isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
  };

  return (
    <div
      ref={ref}
      className={`${baseClasses} ${animationClasses[animation]}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}
```

**Validation :**
- [ ] Créer `AnimatedSection.tsx`
- [ ] Wrapper les blocs principaux (Hero, Services, Features)
- [ ] Tester fluidité animations
- [ ] Vérifier performance (pas de jank)

---

## 📊 Planning Enrichi Phase 2 Premium

| Semaine | Tâches | Priorité | Jours |
|---------|--------|----------|-------|
| **S1** | SeoAgent Kimi + TemplateAgent IA | P0 | 3-4 |
| **S1** | **ImageAgent (NOUVEAU)** | P0 | 2 |
| **S2** | Tests backend stabilisation | P0 | 2 |
| **S2** | Animations (NOUVEAU) | P1 | 1 |
| **S2** | Documentation + E2E | P1 | 2 |

**Total enrichi : 10-13 jours** (vs 8-11 jours initial)

---

## ✅ Critères "WHAOUUUU" Validation Finale

**Un site est "WHAOUUUU" si :**

1. ✅ **Hero image** générée par DALL-E (pas placeholder)
2. ✅ **Images services** uniques et pertinentes
3. ✅ **Palette couleurs** harmonieuse via LLM
4. ✅ **Fonts** professionnelles adaptées secteur
5. ✅ **Textes** percutants et contextuels
6. ✅ **Animations** subtiles au scroll
7. ✅ **Logo** professionnel DALL-E
8. ✅ **SEO** optimisé via Kimi
9. ✅ **Mobile-first** impeccable
10. ✅ **Réaction entrepreneur** : "C'est exactement ce que je voulais !"

---

**Assigné à :** Dev Senior  
**Deadline :** 10 Janvier 2026 (ajusté +4 jours pour premium)  
**Status :** 🟡 READY FOR ASSIGNMENT

---

**Documents Complémentaires :**
- `PHASE2-PREMIUM-VISION-WHAOUUUU.md` - Vision stratégique complète
- `PHASE2-STATE-ANALYSIS-25DEC2025.md` - Analyse état réel

---

*Work Order créé par Genesis AI Tech Lead*  
*Enrichi le 26/12/2025 avec vision Premium "WHAOUUUU"*
