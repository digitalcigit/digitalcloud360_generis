# 📋 Work Order — GEN-7 : Transformer (Brief → SiteDefinition)

**Date :** 2025-12-04  
**De :** Tech Lead Genesis AI (Cascade)  
**À :** Développeur assigné  
**Objet :** Compléter l'algorithme de transformation Brief → SiteDefinition

---

## 1. Contexte

Le **Transformer** est le cœur de la chaîne de génération de sites Genesis. Il convertit un **Business Brief** (généré par les sub-agents IA) en un **SiteDefinition JSON** utilisable par le Block Renderer frontend.

### Liens de Suivi

| Outil | Lien / ID |
|-------|-----------|
| **Asana** | Task GID `1212209944270161` |
| **Jira** | [GEN-7](https://digitalcloud360.atlassian.net/browse/GEN-7) |
| **Dépendance** | GEN-8 ✅ (SiteDefinition Schema complété) |

---

## 2. Environnement de Développement (Docker)

Le projet tourne sous Docker. Pour développer et tester le Transformer :

1.  **Lancer le backend :**
    ```bash
    cd c:\genesis
    docker-compose up -d genesis-api
    ```
2.  **Exécuter les tests (dans le conteneur) :**
    ```bash
    docker-compose exec genesis-api pytest tests/services/test_transformer.py
    ```
    > ⚠️ **Ne pas lancer pytest en local** (hors conteneur) pour éviter les conflits de dépendances.

---

## 3. Deadline & Estimation

| Métrique | Valeur |
|----------|--------|
| **Deadline** | **05/12/2025** |
| **Estimation** | 10-12h |
| **Priorité** | 🔴 Highest |

### 2.1 Non-Objectifs (Hors Scope GEN-7)

> ⚠️ **Ne PAS faire dans cette story :**

- ❌ Modifier les composants React frontend
- ❌ Créer des endpoints API (scope GEN-10)
- ❌ Implémenter l'IA créative (Phase 2)
- ❌ Gérer le multi-pages (Phase 2)

---

## 3. État Actuel du Code

### Fichier existant : `app/services/transformer.py`

Un **squelette existe déjà** avec :
- ✅ Classe `BriefToSiteTransformer`
- ✅ Méthode `transform()` de base
- ✅ `_extract_theme_colors()` (basique)
- ✅ `_build_home_page()` (Hero + Features + Footer seulement)
- ❌ **Manque** : About, Services, Contact, Testimonials, Gallery, CTA
- ❌ **Manque** : Mapping sectoriel
- ❌ **Manque** : Tests unitaires

### Schema disponible (GEN-8) : `app/schemas/site_definition.py`

Tous les types Pydantic sont maintenant définis et peuvent être utilisés pour valider les outputs.

---

## 4. Sous-Tâches Asana (Mapping)

| # | Sous-tâche Asana | Fichier | Estimation | Status |
|---|------------------|---------|------------|--------|
| 1 | Créer module transformer.py avec BriefToSiteTransformer | `app/services/transformer.py` | ✅ Existe | À compléter |
| 2 | Implémenter `_map_hero_section()` | `app/services/transformer.py` | 0.5h | ⚠️ Basique |
| 3 | Implémenter `_map_about_section()` | `app/services/transformer.py` | 1h | ❌ Manque |
| 4 | Implémenter `_map_services_section()` | `app/services/transformer.py` | 1.5h | ❌ Manque |
| 5 | Implémenter `_map_features_section()` | `app/services/transformer.py` | 0.5h | ⚠️ Basique |
| 6 | Implémenter `_map_contact_section()` | `app/services/transformer.py` | 1h | ❌ Manque |
| 7 | Implémenter `_map_footer_section()` | `app/services/transformer.py` | 0.5h | ⚠️ Basique |
| 8 | Implémenter `_apply_theme()` | `app/services/transformer.py` | 1h | ⚠️ Basique |
| 9 | Mapping sectoriel (templates par industrie) | `app/services/sector_mappings.py` | 2h | ❌ Manque |
| 10 | Tests unitaires Transformer | `tests/services/test_transformer.py` | 2h | ❌ Manque |

---

## 5. Spécifications Techniques

### 5.1 Input : BusinessBrief

Le Transformer reçoit un `BusinessBrief` avec les données des sub-agents :

```python
class BusinessBrief:
    business_name: str
    sector: str
    mission: str
    vision: str
    value_proposition: str
    target_audience: str
    differentiation: str
    services: List[str]
    
    # Sub-agent outputs
    research_results: Dict      # Market research
    content_generation: Dict    # Content, textes, hero_image
    logo_creation: Dict         # logo_url, colors
    seo_optimization: Dict      # keywords, meta
    template_selection: Dict    # template_id, sector
```

### 5.2 Output : SiteDefinition

Le Transformer produit un `SiteDefinition` JSON conforme au schema GEN-8 :

```python
{
    "metadata": {
        "title": "Business Name",
        "description": "Meta description SEO",
        "favicon": "logo_url",
        "ogImage": "hero_image_url"
    },
    "theme": {
        "colors": {
            "primary": "#3B82F6",
            "secondary": "#10B981",
            "background": "#FFFFFF",
            "text": "#1F2937"
        },
        "fonts": {"heading": "Inter", "body": "Inter"}
    },
    "pages": [{
        "id": "home",
        "slug": "/",
        "title": "Accueil",
        "sections": [
            {"id": "hero", "type": "hero", "content": {...}},
            {"id": "about", "type": "about", "content": {...}},
            {"id": "services", "type": "services", "content": {...}},
            {"id": "features", "type": "features", "content": {...}},
            {"id": "contact", "type": "contact", "content": {...}},
            {"id": "footer", "type": "footer", "content": {...}}
        ]
    }]
}
```

### 5.3 Méthodes à Implémenter

#### `_map_about_section(brief: BusinessBrief) -> Dict`

```python
def _map_about_section(self, brief: BusinessBrief) -> Dict[str, Any]:
    """Génère la section À propos"""
    return {
        "id": "about",
        "type": "about",
        "content": {
            "title": "À propos",
            "subtitle": brief.business_name,
            "description": brief.mission,
            "mission": brief.mission,
            "vision": brief.vision,
            "image": self._extract_about_image(brief),
            "stats": self._extract_stats(brief)  # Optional
        }
    }
```

#### `_map_services_section(brief: BusinessBrief) -> Dict`

```python
def _map_services_section(self, brief: BusinessBrief) -> Dict[str, Any]:
    """Génère la section Services"""
    services = []
    
    # Extraire depuis brief.services ou content_generation
    raw_services = brief.services or []
    if brief.content_generation:
        raw_services = brief.content_generation.get("services", raw_services)
    
    for i, service in enumerate(raw_services[:6]):  # Max 6 services
        services.append({
            "id": f"service-{i+1}",
            "title": service.get("title", f"Service {i+1}"),
            "description": service.get("description", ""),
            "icon": service.get("icon", "briefcase"),
            "price": service.get("price")  # Optional
        })
    
    return {
        "id": "services",
        "type": "services",
        "content": {
            "title": "Nos Services",
            "subtitle": "Ce que nous offrons",
            "services": services,
            "layout": "grid"
        }
    }
```

#### `_map_contact_section(brief: BusinessBrief) -> Dict`

```python
def _map_contact_section(self, brief: BusinessBrief) -> Dict[str, Any]:
    """Génère la section Contact"""
    return {
        "id": "contact",
        "type": "contact",
        "content": {
            "title": "Contactez-nous",
            "subtitle": "Nous sommes à votre écoute",
            "description": f"N'hésitez pas à nous contacter pour discuter de votre projet avec {brief.business_name}.",
            "email": brief.content_generation.get("email") if brief.content_generation else None,
            "phone": brief.content_generation.get("phone") if brief.content_generation else None,
            "showForm": True,
            "formFields": [
                {"name": "name", "type": "text", "label": "Nom", "required": True},
                {"name": "email", "type": "email", "label": "Email", "required": True},
                {"name": "message", "type": "textarea", "label": "Message", "required": True}
            ]
        }
    }
```

### 5.4 Mapping Sectoriel

Créer `app/services/sector_mappings.py` :

```python
"""Mappings sectoriels pour personnaliser les sites par industrie"""

SECTOR_MAPPINGS = {
    "technology": {
        "default_colors": {"primary": "#3B82F6", "secondary": "#8B5CF6"},
        "default_icons": ["code", "server", "cloud", "cpu"],
        "section_order": ["hero", "features", "services", "about", "contact", "footer"],
        "cta_text": "Démarrer votre projet"
    },
    "restaurant": {
        "default_colors": {"primary": "#EF4444", "secondary": "#F59E0B"},
        "default_icons": ["utensils", "coffee", "wine", "cake"],
        "section_order": ["hero", "about", "services", "gallery", "contact", "footer"],
        "cta_text": "Réserver une table"
    },
    "health": {
        "default_colors": {"primary": "#10B981", "secondary": "#06B6D4"},
        "default_icons": ["heart", "stethoscope", "activity", "shield"],
        "section_order": ["hero", "about", "services", "testimonials", "contact", "footer"],
        "cta_text": "Prendre rendez-vous"
    },
    "default": {
        "default_colors": {"primary": "#3B82F6", "secondary": "#10B981"},
        "default_icons": ["star", "check", "zap", "award"],
        "section_order": ["hero", "about", "services", "features", "contact", "footer"],
        "cta_text": "Nous contacter"
    }
}

def get_sector_config(sector: str) -> dict:
    """Retourne la config sectorielle ou default"""
    return SECTOR_MAPPINGS.get(sector.lower(), SECTOR_MAPPINGS["default"])
```

### 5.5 Tests Unitaires

Créer `tests/services/test_transformer.py` :

```python
"""Tests unitaires pour BriefToSiteTransformer"""

import pytest
from app.services.transformer import BriefToSiteTransformer
from app.schemas.site_definition import SiteDefinition, BlockType


class TestBriefToSiteTransformer:
    """Tests pour le Transformer"""
    
    @pytest.fixture
    def transformer(self):
        return BriefToSiteTransformer()
    
    @pytest.fixture
    def sample_brief(self):
        """Brief de test"""
        from unittest.mock import MagicMock
        brief = MagicMock()
        brief.business_name = "TechStartup Dakar"
        brief.sector = "technology"
        brief.mission = "Digitaliser les PME africaines"
        brief.vision = "Leader de la transformation digitale en Afrique"
        brief.value_proposition = "Solutions tech sur mesure pour PME"
        brief.target_audience = "PME africaines"
        brief.differentiation = "Expertise locale. Prix compétitifs. Support 24/7."
        brief.services = ["Développement Web", "Applications Mobile", "Conseil IT"]
        brief.content_generation = {
            "hero_image": "https://example.com/hero.jpg",
            "theme_colors": {"primary": "#2563eb"}
        }
        brief.logo_creation = {"logo_url": "https://example.com/logo.png"}
        brief.seo_optimization = {"keywords": ["tech", "digital", "afrique"]}
        brief.template_selection = {"template_id": "tech-startup-v2"}
        return brief
    
    def test_transform_returns_valid_structure(self, transformer, sample_brief):
        """Test que transform() retourne une structure valide"""
        result = transformer.transform(sample_brief)
        
        assert "metadata" in result
        assert "theme" in result
        assert "pages" in result
        assert len(result["pages"]) >= 1
    
    def test_metadata_extraction(self, transformer, sample_brief):
        """Test extraction des métadonnées"""
        result = transformer.transform(sample_brief)
        
        assert result["metadata"]["title"] == "TechStartup Dakar"
        assert "Digitaliser" in result["metadata"]["description"]
    
    def test_theme_colors_from_brief(self, transformer, sample_brief):
        """Test extraction des couleurs depuis le brief"""
        result = transformer.transform(sample_brief)
        
        assert result["theme"]["colors"]["primary"] == "#2563eb"
    
    def test_home_page_has_required_sections(self, transformer, sample_brief):
        """Test que la homepage contient les sections requises"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        
        section_types = [s["type"] for s in home_page["sections"]]
        assert "hero" in section_types
        assert "footer" in section_types
    
    def test_hero_section_content(self, transformer, sample_brief):
        """Test contenu de la section Hero"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        hero = next(s for s in home_page["sections"] if s["type"] == "hero")
        
        assert hero["content"]["title"] == sample_brief.value_proposition
        assert hero["content"]["cta"]["link"] is not None
    
    def test_validates_against_pydantic_schema(self, transformer, sample_brief):
        """Test que l'output est valide selon le schema Pydantic"""
        result = transformer.transform(sample_brief)
        
        # Doit passer sans erreur
        site = SiteDefinition(**result)
        assert site.metadata.title == "TechStartup Dakar"
```

---

## 6. Workflow Git

### 6.1 Créer ta branche

```bash
cd c:\genesis
git checkout master
git pull origin master
git checkout -b feature/gen-7-transformer
```

### 6.2 Commits recommandés

```bash
git add app/services/transformer.py
git commit -m "feat(transformer): Add _map_about_section and _map_services_section"

git add app/services/sector_mappings.py
git commit -m "feat(transformer): Add sector mappings for theme customization"

git add tests/services/test_transformer.py
git commit -m "test(transformer): Add unit tests for BriefToSiteTransformer"
```

### 6.3 Push et PR

```bash
git push origin feature/gen-7-transformer
```

Créer une **Pull Request** vers `master` avec :
- Titre : `feat(transformer): [GEN-7] Complete Brief → SiteDefinition transformation`
- Reviewer : Tech Lead Genesis (Cascade)

---

## 7. Critères d'Acceptation

- [ ] **Transformer** génère toutes les sections : Hero, About, Services, Features, Contact, Footer
- [ ] **Output** validé par le schema Pydantic `SiteDefinition`
- [ ] **Mapping sectoriel** fonctionne pour au moins 3 secteurs (tech, restaurant, health)
- [ ] **Tests** passent (`pytest tests/services/test_transformer.py`)
- [ ] **Props alignées** sur les types GEN-8 (`title`, `subtitle`, `cta.link`, etc.)
- [ ] **PR** créée et prête pour review

---

## 8. Ressources

| Document | Chemin |
|----------|--------|
| Schema SiteDefinition (Pydantic) | `app/schemas/site_definition.py` |
| Types TypeScript | `genesis-frontend/src/types/site-definition.ts` |
| Transformer existant | `app/services/transformer.py` |
| Brief Tech Lead Sprint 5 | `docs/memo/MEMO_BRIEF_TECH_LEAD_SPRINT5_2025-12-02.md` |

---

## 9. Points de Contact

| Rôle | Contact | Pour |
|------|---------|------|
| **Tech Lead Genesis** | Cascade (via IDE) | Questions techniques, review PR |
| **Scrum Master** | Via Cascade | Clarifications fonctionnelles |

---

**Bonne implémentation !**

*— Tech Lead Genesis AI (Cascade)*
