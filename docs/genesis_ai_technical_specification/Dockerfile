# =============================================================================
# Genesis AI Deep Agents Service - Production Dockerfile
# =============================================================================

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Genesis AI Team"
LABEL version="1.0.0"
LABEL description="Genesis AI Deep Agents Service - Premier Coach IA Entrepreneur Africain"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création utilisateur non-root pour sécurité
RUN groupadd -r genesisai && useradd -r -g genesisai genesisai

# Répertoire travail
WORKDIR /app

# Copie requirements et installation dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie code source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini pytest.ini ./

# Permissions utilisateur
RUN chown -R genesisai:genesisai /app
USER genesisai

# Port exposition
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
