---
title: "Work Order GEN-15 — pgvector Mémoire Sémantique"
work_order_id: "WO-GEN-15"
date: "2025-12-18"
from: "Tech Lead Genesis AI (Cascade)"
to: "Senior Dev IA (Cascade Instance)"
branch: "feature/GEN-15-pgvector-memory"
priority: "🟡 MOYENNE"
status: "ASSIGNÉ"
estimated_effort: "5 points (2 jours)"
tags: ["phase2", "pgvector", "embeddings", "semantic-memory", "sprint6"]
---

# 📋 Work Order GEN-15 — pgvector Mémoire Sémantique

## 🎯 Objectif

> **Ajouter une mémoire sémantique** pour personnaliser les recommandations basées sur l'historique utilisateur et les briefs similaires.

**Résultat attendu :** Le système peut suggérer des templates, contenus et stratégies basés sur des projets similaires passés.

---

## 📂 Informations Branche

| Info | Valeur |
|------|--------|
| **Branche de travail** | `feature/GEN-15-pgvector-memory` |
| **Branche source** | `master` |
| **Commit de départ** | `68642d89` |

```bash
# Pour démarrer
git fetch origin
git checkout feature/GEN-15-pgvector-memory
```

---

## 🐳 Environnement Containerisé

### Architecture Docker Actuelle

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK                            │
│              genesis-ai-network                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ genesis-api  │  │ postgres     │  │ redis        │       │
│  │ :8000 → 8002 │  │ :5432 → 5435 │  │ :6379 → 6382 │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │         PostgreSQL 15 + pgvector (À AJOUTER)            ││
│  │  ┌─────────────────────────────────────────────────┐    ││
│  │  │ user_embeddings                                  │    ││
│  │  │ - id, user_id, brief_id                          │    ││
│  │  │ - embedding vector(1536)                         │    ││
│  │  │ - metadata jsonb                                 │    ││
│  │  └─────────────────────────────────────────────────┘    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Commandes de lancement

```bash
# Depuis c:\genesis

# Lancer l'environnement de dev
docker-compose up -d postgres redis genesis-api

# Vérifier que tout est healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Logs de l'API
docker logs -f genesis-api

# Accès PostgreSQL pour debug
docker exec -it postgres psql -U genesis_user -d genesis_db
```

### Ports exposés (hôte Windows)

| Service | Port Interne | Port Hôte | URL |
|---------|--------------|-----------|-----|
| Genesis API | 8000 | **8002** | `http://localhost:8002` |
| PostgreSQL | 5432 | **5435** | `localhost:5435` |
| Redis | 6379 | **6382** | `localhost:6382` |

---

## 📁 Fichiers à Créer/Modifier

### 1. Modifier `docker-compose.yml` — Ajouter pgvector

**Emplacement :** `c:\genesis\docker-compose.yml`

**Modification requise (ligne ~46) :**
```yaml
# AVANT
postgres:
  image: postgres:15-alpine

# APRÈS  
postgres:
  image: pgvector/pgvector:pg15
  # ... reste identique
```

**Note :** L'image `pgvector/pgvector:pg15` inclut PostgreSQL 15 + extension pgvector.

---

### 2. Créer `app/models/embedding.py` — Modèle SQLAlchemy

**Emplacement :** `c:\genesis\app\models\embedding.py`

**Contenu cible :**
```python
"""Embedding model for semantic memory with pgvector"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from .base import BaseModel

class UserEmbedding(BaseModel):
    """Stockage des embeddings utilisateur pour mémoire sémantique"""
    __tablename__ = "user_embeddings"
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    brief_id = Column(String, nullable=False, index=True)
    
    # Embedding vector (OpenAI text-embedding-3-small = 1536 dimensions)
    embedding = Column(Vector(1536), nullable=False)
    
    # Source content that was embedded
    source_text = Column(Text, nullable=False)
    embedding_type = Column(String, default="brief")  # brief, conversation, preference
    
    # Metadata for filtering
    metadata = Column(JSONB, default={})
    # Example: {"sector": "restaurant", "location": "Dakar", "template": "modern"}
    
    # Relationships
    user = relationship("User", back_populates="embeddings")
```

---

### 3. Créer `app/core/memory/vector_store.py` — Service VectorStore

**Emplacement :** `c:\genesis\app\core\memory\vector_store.py`

**Contenu cible :**
```python
"""Vector Store Service for semantic memory operations"""

import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from openai import AsyncOpenAI

from app.config.settings import settings
from app.models.embedding import UserEmbedding

logger = structlog.get_logger()

class VectorStore:
    """Service for storing and searching embeddings"""
    
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimensions = 1536
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = await self.openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.info("Text embedded successfully", text_length=len(text))
            return embedding
        except Exception as e:
            logger.error("Failed to embed text", error=str(e))
            raise
    
    async def store_embedding(
        self,
        db: AsyncSession,
        user_id: int,
        brief_id: str,
        text: str,
        embedding_type: str = "brief",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserEmbedding:
        """
        Store text and its embedding in the database.
        
        Args:
            db: Database session
            user_id: User ID
            brief_id: Brief ID
            text: Source text to embed
            embedding_type: Type of embedding (brief, conversation, preference)
            metadata: Additional metadata for filtering
            
        Returns:
            Created UserEmbedding object
        """
        # Generate embedding
        embedding_vector = await self.embed_text(text)
        
        # Create record
        user_embedding = UserEmbedding(
            user_id=user_id,
            brief_id=brief_id,
            embedding=embedding_vector,
            source_text=text,
            embedding_type=embedding_type,
            metadata=metadata or {}
        )
        
        db.add(user_embedding)
        await db.commit()
        await db.refresh(user_embedding)
        
        logger.info(
            "Embedding stored",
            user_id=user_id,
            brief_id=brief_id,
            embedding_type=embedding_type
        )
        
        return user_embedding
    
    async def search_similar(
        self,
        db: AsyncSession,
        query_text: str,
        user_id: Optional[int] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using cosine similarity.
        
        Args:
            db: Database session
            query_text: Text to search for
            user_id: Optional user ID to filter results
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar embeddings with scores
        """
        # Generate query embedding
        query_embedding = await self.embed_text(query_text)
        
        # Build query with pgvector cosine distance
        # Note: pgvector uses <=> for cosine distance (1 - similarity)
        # So we convert to similarity: 1 - distance
        
        query = text("""
            SELECT 
                id,
                user_id,
                brief_id,
                source_text,
                embedding_type,
                metadata,
                1 - (embedding <=> :query_embedding) as similarity
            FROM user_embeddings
            WHERE 1 - (embedding <=> :query_embedding) >= :threshold
            {user_filter}
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """.format(
            user_filter="AND user_id = :user_id" if user_id else ""
        ))
        
        params = {
            "query_embedding": str(query_embedding),
            "threshold": threshold,
            "limit": limit
        }
        if user_id:
            params["user_id"] = user_id
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        similar_items = []
        for row in rows:
            similar_items.append({
                "id": row.id,
                "user_id": row.user_id,
                "brief_id": row.brief_id,
                "source_text": row.source_text,
                "embedding_type": row.embedding_type,
                "metadata": row.metadata,
                "similarity": float(row.similarity)
            })
        
        logger.info(
            "Similar embeddings found",
            query_length=len(query_text),
            results_count=len(similar_items)
        )
        
        return similar_items
    
    async def delete_user_embeddings(
        self,
        db: AsyncSession,
        user_id: int,
        brief_id: Optional[str] = None
    ) -> int:
        """
        Delete embeddings for a user.
        
        Args:
            db: Database session
            user_id: User ID
            brief_id: Optional specific brief ID
            
        Returns:
            Number of deleted records
        """
        query = select(UserEmbedding).where(UserEmbedding.user_id == user_id)
        if brief_id:
            query = query.where(UserEmbedding.brief_id == brief_id)
        
        result = await db.execute(query)
        embeddings = result.scalars().all()
        
        count = len(embeddings)
        for embedding in embeddings:
            await db.delete(embedding)
        
        await db.commit()
        
        logger.info("Embeddings deleted", user_id=user_id, count=count)
        return count
```

---

### 4. Créer `app/api/v1/memory.py` — API Endpoint

**Emplacement :** `c:\genesis\app\api\v1\memory.py`

**Contenu cible :**
```python
"""Memory API Endpoints for semantic search"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional, Any

from app.api.v1.dependencies import get_current_user, get_db
from app.models.user import User
from app.core.memory.vector_store import VectorStore
from app.utils.logger import logger

router = APIRouter()
vector_store = VectorStore()

class SimilarSearchRequest(BaseModel):
    """Request schema for similarity search"""
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    include_all_users: bool = Field(default=False)
    
    class Config:
        extra = "forbid"

class SimilarItem(BaseModel):
    """Single similar item in response"""
    brief_id: str
    source_text: str
    embedding_type: str
    metadata: dict
    similarity: float

class SimilarSearchResponse(BaseModel):
    """Response schema for similarity search"""
    results: List[SimilarItem]
    query: str
    count: int

@router.post("/similar", response_model=SimilarSearchResponse)
async def search_similar(
    request: SimilarSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for similar briefs/content in semantic memory.
    
    Returns items similar to the query text, ordered by similarity.
    By default, searches only the current user's embeddings.
    Set include_all_users=True to search across all users (for recommendations).
    """
    logger.info(f"Similarity search from user_id={current_user.id}")
    
    try:
        user_id = None if request.include_all_users else current_user.id
        
        results = await vector_store.search_similar(
            db=db,
            query_text=request.query,
            user_id=user_id,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return SimilarSearchResponse(
            results=[SimilarItem(**r) for r in results],
            query=request.query,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la recherche."
        )

@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all semantic memory for the current user.
    Use with caution - this action is irreversible.
    """
    logger.info(f"Deleting all embeddings for user_id={current_user.id}")
    
    try:
        count = await vector_store.delete_user_embeddings(db, current_user.id)
        logger.info(f"Deleted {count} embeddings for user_id={current_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to delete embeddings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la suppression."
        )
```

---

### 5. Créer Migration Alembic

**Emplacement :** `c:\genesis\alembic\versions\xxxx_add_pgvector.py`

**Commande pour générer :**
```bash
docker exec genesis-api alembic revision --autogenerate -m "add_pgvector_extension_and_user_embeddings"
```

**Contenu migration (à ajuster) :**
```python
"""add_pgvector_extension_and_user_embeddings

Revision ID: xxxx
Revises: previous_revision
Create Date: 2025-12-18
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = 'xxxx'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create user_embeddings table
    op.create_table(
        'user_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('brief_id', sa.String(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('embedding_type', sa.String(), default='brief'),
        sa.Column('metadata', sa.dialects.postgresql.JSONB(), default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_user_embeddings_user_id', 'user_embeddings', ['user_id'])
    op.create_index('ix_user_embeddings_brief_id', 'user_embeddings', ['brief_id'])
    
    # Create HNSW index for fast similarity search
    op.execute('''
        CREATE INDEX ix_user_embeddings_embedding 
        ON user_embeddings 
        USING hnsw (embedding vector_cosine_ops)
    ''')

def downgrade():
    op.drop_table('user_embeddings')
    op.execute('DROP EXTENSION IF EXISTS vector')
```

---

### 6. Modifier `app/models/user.py` — Ajouter relation

**Ajouter relationship :**
```python
# Dans class User
embeddings = relationship("UserEmbedding", back_populates="user")
```

---

### 7. Modifier `app/api/v1/__init__.py` — Enregistrer router

**Ajouter import et include_router :**
```python
from app.api.v1.memory import router as memory_router

# Dans la fonction qui configure les routes
api_router.include_router(memory_router, prefix="/memory", tags=["memory"])
```

---

### 8. Modifier `requirements.txt` — Ajouter dépendances

**Ajouter :**
```
pgvector>=0.2.0
```

---

## 🔄 Flow d'Intégration avec Chat

Après implémentation de GEN-15, modifier `app/api/v1/chat.py` pour :

1. **Stocker l'embedding** après génération d'un brief :
```python
# Après transformation réussie
await vector_store.store_embedding(
    db=db,
    user_id=current_user.id,
    brief_id=brief_id,
    text=f"{business_context['vision']} {business_context['mission']}",
    embedding_type="brief",
    metadata={
        "sector": business_context.get("industry_sector"),
        "location": business_context.get("location", {}).get("city")
    }
)
```

2. **Suggérer des templates** basés sur similarité :
```python
# Avant génération, chercher des briefs similaires
similar = await vector_store.search_similar(
    db=db,
    query_text=request.message,
    limit=3
)
# Utiliser les templates des briefs similaires comme suggestions
```

---

## ✅ Critères d'Acceptation

- [ ] Extension `pgvector` installée et fonctionnelle dans PostgreSQL
- [ ] Table `user_embeddings` créée via migration Alembic
- [ ] Service `VectorStore` implémenté avec `embed_text()` et `search_similar()`
- [ ] Endpoint `POST /api/v1/memory/similar` fonctionnel
- [ ] Endpoint `DELETE /api/v1/memory/user` fonctionnel
- [ ] Tests unitaires pour le VectorStore
- [ ] Documentation API (schémas Pydantic)
- [ ] Index HNSW créé pour performance

---

## 🧪 Tests

### Vérifier pgvector dans PostgreSQL

```bash
docker exec -it postgres psql -U genesis_user -d genesis_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Test manuel via curl

```powershell
# 1. Obtenir un token
$token = (Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/token" `
  -Method POST `
  -Body "username=test@genesis.ai&password=test123456" `
  -ContentType "application/x-www-form-urlencoded" | 
  ConvertFrom-Json).access_token

# 2. Recherche similarité
Invoke-WebRequest -Uri "http://localhost:8002/api/v1/memory/similar" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -Body '{"query": "restaurant africain à Dakar", "limit": 5}' `
  -ContentType "application/json"
```

### Tests unitaires

```bash
docker exec genesis-api pytest tests/test_api/test_memory.py -v
```

---

## ⚠️ Points d'Attention

### 1. Image Docker PostgreSQL

**IMPORTANT :** Changer l'image de `postgres:15-alpine` à `pgvector/pgvector:pg15`.

Après modification, reconstruire :
```bash
docker-compose down postgres
docker-compose up -d postgres
```

### 2. Clé API OpenAI

Les embeddings utilisent `OPENAI_API_KEY`. Vérifier qu'elle est configurée dans `.env`.

### 3. Coût API

Chaque embedding coûte ~$0.00002 pour `text-embedding-3-small`. Prévoir un mécanisme de cache si volume important.

### 4. Index HNSW

L'index HNSW accélère les recherches vectorielles. Sans cet index, les performances dégradent avec le volume de données.

---

## 📤 Livraison

1. **Commit convention :** 
   - `feat(memory): add pgvector extension and user embeddings model`
   - `feat(memory): implement VectorStore service for semantic search`
   - `feat(api): add /memory/similar endpoint`
   
2. **Push sur la branche :** `git push origin feature/GEN-15-pgvector-memory`

3. **Notifier le Tech Lead** pour review

---

## 📞 Support

En cas de blocage :
1. Vérifier que l'extension pgvector est installée : `\dx` dans psql
2. Consulter les logs : `docker logs genesis-api --tail 100`
3. Vérifier `OPENAI_API_KEY` dans `.env`
4. Escalader au Tech Lead avec diagnostic détaillé

---

**Bonne implémentation !**

*Tech Lead Genesis AI*  
*18 décembre 2025*
