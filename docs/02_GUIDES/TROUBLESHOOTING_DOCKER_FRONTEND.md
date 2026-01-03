---
title: "Dépannage : Erreurs 404 dans le conteneur Docker Frontend"
tags: ["docker", "nextjs", "frontend", "troubleshooting"]
status: "adopté"
date: "2026-01-01"
---

# Dépannage : Erreurs 404 dans le conteneur Docker Frontend

## Contexte
Lors du développement du projet Genesis, nous avons rencontré des erreurs 404 lors de la navigation vers de nouvelles routes (ex: `/genesis/themes`) à l'intérieur du conteneur Docker, alors que les fichiers correspondants existaient sur l'hôte.

## Cause Racine
Le conteneur `genesis-frontend` n'utilisait pas de volumes pour synchroniser le code source en temps réel. Lors de la création de nouvelles pages ou de modifications de routes sur l'hôte, le conteneur restait sur sa version buildée au démarrage, ignorant les nouveaux fichiers.

## Solution Implémentée
Mise à jour du fichier `docker-compose.yml` pour inclure des montages de volumes pour le service `frontend`.

### Modifications dans `docker-compose.yml`
```yaml
  frontend:
    # ...
    volumes:
      - ./genesis-frontend:/app
      - /app/node_modules
      - /app/.next
    # ...
```

### Explications des volumes :
1.  `./genesis-frontend:/app` : Synchronise le code source entre l'hôte et le conteneur.
2.  `/app/node_modules` : Volume anonyme pour préserver les dépendances installées à l'intérieur du conteneur (évite les conflits avec l'hôte).
3.  `/app/.next` : Volume anonyme pour les artefacts de build de Next.js.

## Procédure de Vérification
Si vous rencontrez une erreur 404 sur une route existante :
1.  Vérifiez que le fichier `page.tsx` est présent dans `src/app/` sur votre machine.
2.  Exécutez `docker exec genesis-frontend ls -R /app/src/app` pour confirmer la présence du fichier dans le conteneur.
3.  Si le fichier est absent, redémarrez le service :
    ```bash
    docker-compose up -d --build frontend
    ```

## Références
- [Protocole de Maintenance de la Documentation](../03_COLLABORATION_GUIDE/PROTOCOLE_MAINTENANCE_DOC.md) (Note: chemin fictif pour l'exemple, à adapter si nécessaire)
