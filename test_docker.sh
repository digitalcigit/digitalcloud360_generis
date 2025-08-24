#!/bin/bash
# Script pour tester depuis l'intérieur du conteneur genesis-api

echo "🐋 Tests depuis conteneur Docker genesis-api"
echo "=============================================="

# Configuration pour tests depuis conteneur
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@test-db:5432/test_db"

echo "📊 Configuration tests :"
echo "Database URL: $TEST_DATABASE_URL"
echo ""

echo "🧪 Exécution des tests d'authentification..."
pytest tests/test_api/test_auth.py -v

echo ""
echo "🧪 Exécution des tests d'intégration..."
pytest tests/test_integrations/ -v

echo ""
echo "✅ Tests Docker terminés"