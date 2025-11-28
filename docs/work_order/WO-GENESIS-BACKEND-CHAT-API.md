---
title: "WO-GENESIS-BACKEND-CHAT-API"
tags: ["backend", "fastapi", "security", "api", "work-order"]
status: "ready"
date: "2025-11-28"
priority: "CRITIQUE"
assignee: "Backend Dev"
---

# 🛡️ WORK ORDER - Implémentation Sécurisée API Chat

**WO ID:** WO-GENESIS-BACKEND-CHAT-API  
**Phase:** Phase 1B - Finalisation E2E  
**Priorité:** 🔴 CRITIQUE (Bloquant pour E2E Frontend)  
**Estimation:** 2-3 heures  

---

## 🎯 OBJECTIF

Implémenter l'endpoint `/api/v1/chat/` manquant côté Backend pour permettre au Frontend de communiquer.
**L'implémentation doit respecter les standards "Security by Design" les plus stricts.**

Ce Work Order ne concerne **pas** l'implémentation de l'intelligence artificielle (LangGraph) elle-même, mais la création de la **couche d'interface API sécurisée** (Controller Layer) qui servira de porte d'entrée.

---

## 🔒 STANDARDS DE SÉCURITÉ (MANDATORY)

Toute Pull Request ne respectant pas ces points sera **rejetée immédiatement**.

### 1. The Token is the Truth (Authentification)
*   **Interdiction formelle** de lire un ID utilisateur depuis le corps de la requête (body).
*   L'identité de l'utilisateur (`current_user`) doit être injectée via le Dependency Injection de FastAPI : `Depends(get_current_user)`.
*   Si le token est invalide ou absent, l'API doit renvoyer `401 Unauthorized` avant même d'exécuter la moindre ligne de logique métier.

### 2. Zero Trust Input (Validation)
*   Utiliser **Pydantic** pour valider strictement toutes les entrées.
*   Rejeter tout champ inattendu (`extra="forbid"`).
*   Sanitiser les entrées textuelles pour éviter les injections (bien que Pydantic gère le typage, attention aux XSS stockés).

### 3. Least Privilege (Réponse)
*   Ne renvoyer que les données strictement nécessaires au Frontend.
*   Intercepter toutes les exceptions pour éviter de leaker des "Stack Traces" (Information Disclosure).

---

## 🛠 SPÉCIFICATIONS TECHNIQUES

### A. Modèles de Données (Pydantic)

Créer/Modifier `app/schemas/chat.py` :

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_history: List[Message] = Field(default_factory=list)
    
    # ⛔ SECURITY: Interdiction d'ajouter user_id ici
    
    class Config:
        extra = "forbid" # Rejette tout champ parasite

class ChatResponse(BaseModel):
    response: str
    brief_generated: bool = False
    site_data: Optional[dict[str, Any]] = None
```

### B. Endpoint Implementation

Créer `app/api/v1/chat.py` :

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.schemas.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import logger

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user) # ✅ SECURITY: Source of Truth
):
    """
    Secure Chat Endpoint.
    Identity is derived from JWT Token, NOT request body.
    """
    logger.info(f"Chat request from user_id={current_user.id}")
    
    try:
        # TODO: Connecter ici l'orchestrateur LangGraph ultérieurement.
        # Pour la Phase 1B (Test E2E), nous simulons une réponse simple.
        
        # MOCK LOGIC POUR TEST E2E :
        # Si le message contient "site", on simule une génération réussie
        if "site" in request.message.lower():
            return ChatResponse(
                response="J'ai bien compris votre demande. Je génère votre site immédiatement...",
                brief_generated=True,
                site_data={
                    "id": 1,
                    "theme": "modern",
                    "colors": {"primary": "#000000"}
                }
            )
            
        return ChatResponse(
            response=f"Bonjour {current_user.email}, je suis Genesis. Parlez-moi de votre projet de site web.",
            brief_generated=False
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne est survenue."
        )
```

### C. Routing

Modifier `app/main.py` pour inclure le router :

```python
from app.api.v1 import chat # Import

# ...

app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["Chat"]
)
```

---

## ✅ DEFINITION OF DONE (DoD)

1.  [ ] L'endpoint `POST /api/v1/chat/` répond `200 OK` à une requête valide.
2.  [ ] L'endpoint répond `401 Unauthorized` si le Header Authorization est manquant (Test avec Postman requis).
3.  [ ] Le `user_id` utilisé dans les logs provient bien de `current_user.id` et non du body.
4.  [ ] Le Payload de réponse respecte le schéma `ChatResponse` attendu par le Frontend.
5.  [ ] Code couvert par un test unitaire basique (dans `tests/api/test_chat.py`).

---

## 📅 LIVRABLES ATTENDUS

*   Branche : `feature/backend-chat-api`
*   Pull Request avec description des tests de sécurité effectués.

**Tech Lead Note:** Je serai intransigeant sur la gestion du token lors de la review.

---
