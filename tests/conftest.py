"""Pytest configuration for the Genesis AI Service tests - Multi-environment profile."""

# Import du gestionnaire de profils multi-environnements
# Sélectionne automatiquement conftest_local.py ou conftest_docker.py
# selon l'environnement détecté (local vs Docker)

from tests.conftest_profile import *

# Les fixtures sont automatiquement importées selon le profil:
# - LOCAL: conftest_local.py (PostgreSQL localhost:5433)
# - DOCKER: conftest_docker.py (PostgreSQL test-db:5432)

# Pour forcer un profil spécifique, utiliser:
# export TEST_PROFILE=local  # ou docker
# pytest tests/

# Informations sur le profil actuel disponibles via TEST_PROFILE_INFO

# Note: All standard fixtures (test_engine, db_session, client, etc.) are 
# provided by the imported profile module. Do not redefine them here.
