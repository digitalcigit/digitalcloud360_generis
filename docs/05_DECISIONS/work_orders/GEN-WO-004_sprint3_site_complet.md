# GEN-WO-004 : Sprint 3 - Site Web Complet & Professionnel

---
title: "Sprint 3 - Génération Site Web Complet"
tags: ["sprint3", "logo", "seo", "dalle", "renderer", "agents"]
status: "approuvé"
date: "2025-12-20"
priority: "P0 - Critique pour MVP"
estimated_effort: "5-7 jours"
assigned_to: "Senior Dev (IA simulée)"
validated_by: "PO + Tech Lead Cascade"
---

## 1. Contexte et Justification

### 1.1 Constat Post-Sprint 2

Le test E2E du 20/12/2025 a validé le coaching maïeutique (5 étapes) avec succès. Cependant, l'analyse approfondie révèle des **lacunes critiques** pour la finalité visible du produit :

| Composant | État Actuel | Impact Business |
|-----------|-------------|-----------------|
| **LogoAgent** | MOCK (URL fictive) | Pas de logo réel généré |
| **SeoAgent** | Partiel (search sans LLM) | SEO basique non optimisé |
| **TemplateAgent** | 4 templates hardcodés | Choix non intelligent |
| **Site Renderer** | Non implémenté | Impossible de "voir son site" |

### 1.2 Vision PO

> *"Le coaching est le service noyau (collecte de data), mais la finalité visible et appréciable par les entrepreneurs demeure la génération d'un site avec un minimum d'optimisation."*

### 1.3 Objectif Sprint 3

**Livrer un site web visible, professionnel et optimisé** à partir du business brief généré par le coaching.

---

## 2. Périmètre Fonctionnel

### 2.1 P0 - Critiques (Bloquants MVP)

#### 2.1.1 Logo Agent avec DALL-E 3

**Fichiers concernés:**
- `app/core/agents/logo.py` → Refactoring complet
- `app/core/integrations/logoai.py` → À supprimer ou adapter
- `app/core/providers/dalle.py` → Déjà implémenté ✅

**Travail requis:**
1. Remplacer `LogoAIClient` par `DALLEImageProvider`
2. Adapter signature `run()` pour matcher format orchestrateur
3. Ajouter gestion erreurs et fallback (logo placeholder)
4. Stocker logo généré dans Redis avec TTL 24h

**Exemple d'intégration:**
```python
from app.core.providers.dalle import DALLEImageProvider

class LogoAgent:
    def __init__(self):
        self.dalle_provider = DALLEImageProvider(
            api_key=settings.OPENAI_API_KEY,
            model="dall-e-3"
        )
    
    async def run(self, business_name: str, industry: str, style: str = "modern") -> dict:
        result = await self.dalle_provider.generate_logo(
            business_name=business_name,
            industry=industry,
            style=style
        )
        return {
            "logo_url": result.get("image_url"),
            "logo_data": result.get("image_data"),  # Base64 pour persistance
            "metadata": result.get("metadata")
        }
```

**Tests requis:**
- [ ] Unit test génération logo basique
- [ ] Test intégration avec orchestrateur
- [ ] Test fallback si DALL-E échoue

---

#### 2.1.2 SEO Agent Intelligent

**Fichiers concernés:**
- `app/core/agents/seo.py` → Refactoring avec LLM

**Travail requis:**
1. Injecter `DeepseekProvider` pour analyse SEO intelligente
2. Générer mots-clés contextuels via LLM (pas juste search)
3. Créer méta-descriptions optimisées par IA
4. Suggérer structure headings (H1, H2, etc.)

**Exemple d'amélioration:**
```python
async def run(self, business_brief: dict) -> dict:
    # 1. Recherche concurrence SEO
    search_data = await self.search_provider.search(
        f"SEO {business_brief['industry_sector']} {business_brief['location']['country']}"
    )
    
    # 2. Analyse LLM pour génération SEO optimisé
    seo_analysis = await self.llm_provider.generate_structured(
        prompt=self._build_seo_prompt(business_brief, search_data),
        response_schema={
            "primary_keywords": "array",
            "secondary_keywords": "array",
            "meta_title": "string",
            "meta_description": "string",
            "heading_structure": "object"
        }
    )
    
    return seo_analysis
```

**Tests requis:**
- [ ] Unit test génération SEO
- [ ] Test qualité mots-clés générés

---

#### 2.1.3 Site Renderer (Frontend)

**Fichiers à créer:**
- `genesis-frontend/src/app/site/[siteId]/page.tsx` → Page rendu site
- `genesis-frontend/src/components/site-renderer/` → Composants blocs

**Travail requis:**
1. Route `/site/[siteId]` pour afficher le site généré
2. Fetch `SiteDefinition` depuis API (`/api/v1/sites/{siteId}`)
3. Renderer dynamique par type de bloc :
   - `HeaderBlock` → Hero avec titre, CTA
   - `AboutBlock` → Section À propos
   - `ServicesBlock` → Grille services
   - `ContactBlock` → Formulaire contact
   - `FooterBlock` → Footer avec liens

**Architecture Renderer:**
```typescript
// site-renderer/BlockRenderer.tsx
interface BlockRendererProps {
  block: SiteBlock;
}

export function BlockRenderer({ block }: BlockRendererProps) {
  switch (block.type) {
    case 'header':
      return <HeaderBlock data={block.data} />;
    case 'about':
      return <AboutBlock data={block.data} />;
    case 'services':
      return <ServicesBlock data={block.data} />;
    case 'contact':
      return <ContactBlock data={block.data} />;
    default:
      return null;
  }
}
```

**Tests requis:**
- [ ] Test rendu chaque type de bloc
- [ ] Test responsive (mobile-first)
- [ ] Test E2E coaching → génération → visualisation

---

### 2.2 P1 - Importants (Post-MVP)

#### 2.2.1 Template Agent Intelligent

**Fichiers concernés:**
- `app/core/agents/template.py`

**Travail requis:**
1. Enrichir catalogue templates (10+ templates)
2. Ajouter matching intelligent par secteur via LLM
3. Prévisualisation template avant sélection

---

#### 2.2.2 Persistance Logo Cloud

**Travail requis:**
1. Upload logo généré vers stockage cloud (S3/R2)
2. URL permanente vs URL DALL-E (expire 1h)

---

### 2.3 P2 - Améliorations (Sprint 4+)

- Édition site post-génération
- Multi-templates par site
- Export HTML statique
- Domaine personnalisé

---

## 3. Architecture Technique

### 3.1 Flux Mis à Jour

```
┌─────────────────────────────────────────────────────────────────┐
│                     COACHING (5 étapes)                         │
│  Vision → Mission → Clientèle → Différenciation → Offre         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH ORCHESTRATOR                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐ │
│  │ Research │ → │ Content  │   │   Logo   │   │     SEO      │ │
│  │  (Kimi)  │   │(Deepseek)│   │ (DALL-E) │   │(Deepseek+)   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘ │
│                              │                                   │
│                    Template Selection                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SITE DEFINITION JSON                         │
│  { blocks: [...], seo: {...}, logo: {...}, theme: {...} }      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SITE RENDERER                               │
│  Next.js Dynamic Block Rendering → Site Web Visible             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Endpoints API à Créer/Modifier

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/sites/{siteId}` | GET | Récupère SiteDefinition |
| `/api/v1/sites/{siteId}/preview` | GET | URL preview temporaire |
| `/api/v1/logos/generate` | POST | Génération logo isolée |

---

## 4. Plan d'Exécution

### Phase 1 : Agents Backend (2-3 jours)

| Jour | Tâche | Livrable |
|------|-------|----------|
| J1 AM | Refactoring LogoAgent → DALL-E | Logo Agent fonctionnel |
| J1 PM | Tests unitaires Logo | Couverture 80% |
| J2 AM | Refactoring SeoAgent → LLM | SEO Agent intelligent |
| J2 PM | Tests unitaires SEO | Couverture 80% |
| J3 | Intégration orchestrateur + Tests E2E | 5/5 agents OK |

### Phase 2 : Site Renderer Frontend (2-3 jours)

| Jour | Tâche | Livrable |
|------|-------|----------|
| J4 AM | Route `/site/[siteId]` + API fetch | Page squelette |
| J4 PM | HeaderBlock + AboutBlock | 2 blocs fonctionnels |
| J5 AM | ServicesBlock + ContactBlock | 4 blocs fonctionnels |
| J5 PM | Styling Tailwind + Responsive | Site pro mobile-first |
| J6 | Tests E2E complet coaching→site | Flow validé |

### Phase 3 : Intégration & Polish (1 jour)

| Tâche | Livrable |
|-------|----------|
| Bouton "Voir mon site" post-coaching | Navigation fluide |
| Gestion erreurs gracieuse | UX robuste |
| Documentation technique | TECH_LEAD_HANDOVER.md |

---

## 5. Critères d'Acceptation

### 5.1 Fonctionnels

- [ ] **Logo**: Un logo unique est généré par DALL-E 3 et affiché sur le site
- [ ] **SEO**: Méta-title et méta-description générés par IA et présents dans le HTML
- [ ] **Site visible**: Clic "Voir mon site" → Landing page complète affichée
- [ ] **Responsive**: Site lisible sur mobile (90% trafic Afrique)
- [ ] **Performance**: Temps génération site < 30 secondes

### 5.2 Techniques

- [ ] Orchestrateur retourne `successful_agents=5/5`
- [ ] Tests unitaires agents: couverture > 80%
- [ ] Tests E2E: flow complet coaching → site
- [ ] Aucune régression sur coaching existant

---

## 6. Risques et Mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| DALL-E rate limit | Logo non généré | Fallback placeholder + retry queue |
| Coût DALL-E ($0.04/image HD) | Budget API | Limite 1 logo/session, cache Redis |
| Temps génération long | UX dégradée | Progress bar + génération async |
| Content policy DALL-E | Logo refusé | Prompt sanitization + fallback |

---

## 7. Variables d'Environnement

**Requis Sprint 3:**
```bash
# Déjà configurés
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx        # Utilisé pour DALL-E 3
KIMI_API_KEY=sk-xxx          # Recherche web

# Optionnel (stockage cloud logos)
AWS_S3_BUCKET=genesis-assets
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

---

## 8. Validation

| Rôle | Validation |
|------|------------|
| **PO** | ✅ Scope approuvé le 20/12/2025 |
| **Tech Lead Cascade** | ✅ Architecture validée |
| **Senior Dev** | ⏳ En attente assignation |

---

## 9. Références

- **GEN-WO-002**: Coaching Maïeutique Backend
- **GEN-WO-003**: Coaching Frontend
- **ADR-001**: Architecture Hub & Satellites
- **Test E2E 20/12**: Validation coaching avec clés API réelles

---

*Document généré par Tech Lead Cascade - 20/12/2025*
