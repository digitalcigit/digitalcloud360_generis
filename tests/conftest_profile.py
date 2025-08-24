"""Test profile manager for automatic environment detection."""

import os
import sys
from pathlib import Path

# Détection automatique de l'environnement
def detect_test_environment():
    """Détecter l'environnement de test (local vs docker)."""
    
    # Méthode 1: Variable d'environnement explicite
    test_profile = os.getenv("TEST_PROFILE", "").lower()
    if test_profile in ["local", "docker"]:
        return test_profile
    
    # Méthode 2: Détection via présence de variables Docker
    if os.getenv("RUNNING_IN_DOCKER") or os.getenv("CONTAINER_NAME"):
        return "docker"
    
    # Méthode 3: Détection via hostname
    hostname = os.getenv("HOSTNAME", "")
    if hostname.startswith("genesis-") or "-api" in hostname:
        return "docker"
    
    # Méthode 4: Détection via accessibilité réseau
    import socket
    try:
        # Teste si on peut accéder au service Docker depuis l'hôte
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5433))  # Port test-db local
        sock.close()
        if result == 0:
            return "local"
    except:
        pass
    
    # Défaut: local
    return "local"

# Auto-import du bon conftest selon l'environnement
test_env = detect_test_environment()

print(f"🧪 Test Profile détecté: {test_env.upper()}")

if test_env == "docker":
    print("📦 Utilisation conftest_docker.py pour environnement conteneurisé")
    from tests.conftest_docker import *
else:
    print("💻 Utilisation conftest_local.py pour environnement local")  
    from tests.conftest_local import *

# Export des fixtures selon le profil
if test_env == "docker":
    # Renommage des fixtures Docker vers les noms standards
    test_engine = test_engine_docker
    db_session = db_session_docker
    client = client_docker
    test_password = test_password_docker
    test_user = test_user_docker
    auth_headers = auth_headers_docker
    test_env_fixture = test_env_docker
else:
    # Renommage des fixtures Local vers les noms standards
    test_engine = test_engine_local
    db_session = db_session_local
    client = client_local
    test_password = test_password_local
    test_user = test_user_local
    auth_headers = auth_headers_local
    test_env_fixture = test_env_local

# Métadonnées du profil actuel
TEST_PROFILE_INFO = {
    "environment": test_env,
    "database_url": TEST_DATABASE_URL_DOCKER if test_env == "docker" else TEST_DATABASE_URL_LOCAL,
    "description": f"Tests en environnement {'Docker' if test_env == 'docker' else 'Local'}",
    "postgres_host": "test-db:5432" if test_env == "docker" else "localhost:5433"
}

print(f"🔗 Base de données: {TEST_PROFILE_INFO['database_url']}")
print(f"📍 PostgreSQL: {TEST_PROFILE_INFO['postgres_host']}")
print("=" * 60)