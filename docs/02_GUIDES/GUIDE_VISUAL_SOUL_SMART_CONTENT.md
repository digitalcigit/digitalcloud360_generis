---
title: "Guide d'Implémentation : Visual Soul & Smart Content"
tags: ["dall-e", "content-generation", "asyncio", "ux"]
status: "actif"
date: "2025-12-29"
---

# Guide d'Implémentation : Visual Soul & Smart Content

Ce guide documente les nouvelles fonctionnalités "Visual Soul" (Génération d'images) et "Smart Content" (Rédaction intelligente) intégrées à Genesis AI pour produire des sites web modernes et adaptés au marché africain.

## 1. Smart Content (L'Intelligence Contextuelle)

### Concept
Le module "Smart Content" transforme Genesis d'un simple "colleur de données" en un véritable **copywriter digital**. Au lieu de copier-coller les réponses brutes du coaching (Vision, Mission), l'IA les synthétise pour créer un discours marketing engageant.

### Implémentation Technique
*   **Agent** : `ContentSubAgent` (`app/core/deep_agents/sub_agents/content.py`)
*   **Mécanisme** : Prompt spécialisé demandant un format JSON strict.
*   **Fonctionnalités Clés** :
    *   **Storytelling** : Transforme la "Vision" en "Promesse Client".
    *   **Ton** : Chaleureux et adapté culturellement (ex: valeurs communautaires).
    *   **Smart Items** : Infère des éléments spécifiques au secteur (ex: Plats pour un restaurant) sans que l'utilisateur n'ait à les saisir manuellement.

### Structure de Données (JSON)
Le `ContentSubAgent` génère désormais une structure enrichie :
```json
{
    "hero_section": {
        "title": "Titre marketing percutant",
        "subtitle": "Sous-titre orienté bénéfice",
        "primary_cta": "Action (ex: Commander sur WhatsApp)"
    },
    "smart_content_preview": {
        "section_title": "Nos Spécialités",
        "items": [
            {"name": "Plat Signature", "desc": "Description appétissante"}
        ]
    }
}
```

---

## 2. Visual Soul (L'Âme Visuelle)

### Concept
"Visual Soul" intègre la génération d'images via **DALL-E 3** pour donner une identité visuelle unique à chaque site dès la première version. Fini les placeholders gris.

### Implémentation Technique
*   **Agent** : `ImageAgent` (`app/core/agents/image.py`)
*   **Provider** : OpenAI DALL-E 3
*   **Optimisation de Performance** :
    *   **Parallélisation** : Utilisation de `asyncio.gather` pour générer Hero, Services et Features simultanément.
    *   **Rate Limiting** : Utilisation d'un `asyncio.Semaphore(3)` pour limiter à 3 requêtes simultanées et éviter les erreurs HTTP 429.
    *   **Fallback** : En cas d'échec API, bascule automatique sur des images Unsplash haute qualité.

### Types d'Images Générées
1.  **Hero Image** (Wide) : Représente l'activité globale (sans texte).
2.  **Service Images** (Square) : Illustrent les services ou produits phares.
3.  **Feature Images** (Square) : Illustrent les atouts concurrentiels.

---

## 3. Le Transformer (L'Assembleur)

Le `BriefToSiteTransformer` (`app/services/transformer.py`) a été mis à jour pour orchestrer ces deux nouveautés :

1.  **Priorité au Contenu Généré** : Si le `ContentSubAgent` a produit du "Smart Content", il est utilisé prioritairement sur les données brutes du brief.
2.  **Mapping Visuel** : Injecte les URLs des images générées par `ImageAgent` dans les sections correspondantes (Hero, Services, Features).
3.  **Résilience** : Si une étape échoue (Contenu ou Image), le Transformer utilise les données brutes ou les images de fallback pour garantir qu'un site est toujours généré.

## 4. Configuration

Les clés API suivantes sont requises dans le `.env` :
*   `OPENAI_API_KEY` : Pour DALL-E 3.
*   `DEEPSEEK_API_KEY` (ou autre LLM) : Pour la génération de contenu.

## 5. Bonnes Pratiques de Maintenance
*   **Rate Limits** : Surveiller les quotas OpenAI si le volume d'utilisateurs augmente. Le Semaphore est actuellement réglé sur `3`.
*   **Prompt Engineering** : Toute modification du prompt `ContentSubAgent` doit conserver le format JSON strict pour ne pas casser le Transformer.
