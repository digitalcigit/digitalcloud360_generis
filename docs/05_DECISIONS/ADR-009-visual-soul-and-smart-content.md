---
title: "ADR-009: Implémentation Visual Soul & Smart Content"
status: "adopté"
date: "2025-12-29"
deciders: ["Tech Lead", "Product Owner"]
---

# ADR-009: Implémentation Visual Soul & Smart Content

## Contexte
L'application Genesis générait des sites techniquement fonctionnels mais "froids" et génériques. Le contenu était une copie brute des réponses de l'utilisateur, et les images étaient des placeholders. Pour répondre à l'objectif de créer des produits "innovants, modernes et adaptés au marché africain", nous devions améliorer la qualité perçue (UX/UI) et la pertinence du contenu.

## Décision

Nous avons décidé d'implémenter deux modules majeurs :

1.  **Visual Soul (Images)** : Intégration de DALL-E 3 pour générer des images contextuelles.
2.  **Smart Content (Texte)** : Évolution de l'agent de contenu pour agir comme un copywriter.

### Choix Techniques Spécifiques

*   **Parallélisation des Images** :
    *   *Problème* : Générer 5-8 images séquentiellement prenait > 60 secondes (Timeouts).
    *   *Solution* : Utilisation de `asyncio.gather` pour lancer les générations en parallèle.
    *   *Sécurité* : Ajout d'un `asyncio.Semaphore(3)` pour limiter la concurrence et respecter les Rate Limits de l'API OpenAI (évite les erreurs 429).

*   **Synthèse de Contenu Structurée** :
    *   *Solution* : Le LLM (Deepseek/Kimi) génère désormais une réponse strictement formatée en JSON incluant du storytelling et des "Smart Items" (inférence de produits/services).
    *   *Intégration* : Le `Transformer` mappe ce JSON structuré vers le `SiteDefinition` du frontend.

*   **Fallback Strategy** :
    *   Images : Fallback sur Unsplash si DALL-E échoue.
    *   Contenu : Fallback sur les données brutes du brief si la génération échoue.

## Conséquences

### Positives
*   **Expérience Utilisateur** : Effet "Whaou" immédiat avec des sites visuels et bien rédigés.
*   **Performance** : La parallélisation maintient le temps de génération acceptable (< 30s pour les images en parallèle).
*   **Pertinence** : Les sites semblent faits "sur mesure" grâce aux Smart Items.

### Négatives / Risques
*   **Coûts API** : Augmentation significative du coût par génération (DALL-E 3 est coûteux).
*   **Complexité** : Ajout de logique asynchrone (Semaphore) et de parsing JSON plus complexe.

## Statut
Implémenté et validé via tests E2E.
