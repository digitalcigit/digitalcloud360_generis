---
title: "WO-GENESIS-SSO-TOKEN-PASSING"
tags: ["frontend", "auth", "sso", "work-order"]
status: "ready"
date: "2025-11-29"
priority: "HIGH"
assignee: "Frontend Dev"
---

# 🔐 WORK ORDER - SSO Token Passing (Cross-Domain Fix)

**WO ID:** WO-GENESIS-SSO-TOKEN-PASSING
**Phase:** Phase 1B - UX Polish
**Priorité:** 🔴 HAUTE (Bloquant pour fluidité UX dev local)

---

## 🎯 OBJECTIF

Permettre l'authentification automatique sur Genesis (port 3002) lorsqu'un utilisateur est redirigé depuis le Hub DC360 (port 3000), en contournant la limitation des cookies `SameSite`/Domain en localhost.

**Mécanisme cible :**
1. L'utilisateur arrive sur `http://localhost:3002?token=<JWT_TOKEN>`
2. Genesis intercepte ce token.
3. Genesis stocke le token dans ses propres cookies (ou localStorage).
4. Genesis nettoie l'URL (retire le paramètre token) pour la sécurité.
5. L'utilisateur est connecté.

---

## 🛠 SPÉCIFICATIONS TECHNIQUES

### A. Fichier `src/app/page.tsx` (Landing Page)

Modifier la Landing Page pour qu'elle agisse comme un "Sluice Gate" (Sas d'entrée).

1.  **Client Component Wrapper** :
    La page actuelle est un Server Component. Il faudra peut-être extraire la logique de détection d'URL dans un composant client (`<AuthReceiver />`) inséré dans la page, ou utiliser un `useEffect` si la page devient `'use client'`.

2.  **Logique de Traitement :**
    ```typescript
    // Pseudo-code
    useEffect(() => {
        const params = useSearchParams();
        const token = params.get('token');

        if (token) {
            // 1. Valider basiquement (optionnel, le backend le fera)
            // 2. Stocker le token
            document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
            
            // 3. Nettoyer l'URL sans recharger la page
            const newUrl = window.location.pathname;
            window.history.replaceState({}, '', newUrl);
            
            // 4. Forcer un rafraichissement du contexte d'auth ou rediriger vers /chat
            window.location.href = '/chat';
        }
    }, []);
    ```

### B. Sécurité

*   **Token Exposure** : Le token est visible dans l'URL le temps de la redirection. C'est acceptable pour le contexte "Dev Local" ou "Transition".
*   **History Cleaning** : Impératif de faire un `replaceState` pour que le token ne reste pas dans l'historique du navigateur.

---

## ✅ DEFINITION OF DONE (DoD)

1.  [ ] Si j'ouvre `http://localhost:3002?token=TEST_TOKEN`, je suis redirigé vers `/chat` (ou je reste sur Home connecté).
2.  [ ] Le cookie `access_token` est créé sur le domaine `localhost:3002`.
3.  [ ] L'URL finale dans la barre d'adresse ne contient plus `?token=...`.
4.  [ ] Le contexte `AuthContext` détecte l'utilisateur connecté.

---

## 📅 LIVRABLES

*   Branche : `feature/frontend-sso-token`
*   PR incluant les modifications Frontend uniquement.

---
