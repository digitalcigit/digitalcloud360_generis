#!/bin/bash
# Script de validation du système de profils multi-environnements

echo "🧪 Test des Profils Multi-environnements T2.2"
echo "=============================================="

echo ""
echo "📊 Test 1: Profil LOCAL (défaut)"
echo "--------------------------------"
export TEST_PROFILE=local
echo "TEST_PROFILE=$TEST_PROFILE"
python -c "
import os
os.environ['TEST_PROFILE'] = 'local'
from tests.conftest_profile import TEST_PROFILE_INFO
print(f'Environment: {TEST_PROFILE_INFO[\"environment\"]}')
print(f'Database: {TEST_PROFILE_INFO[\"database_url\"]}')
print(f'PostgreSQL: {TEST_PROFILE_INFO[\"postgres_host\"]}')
"

echo ""
echo "📦 Test 2: Profil DOCKER" 
echo "------------------------"
export TEST_PROFILE=docker
echo "TEST_PROFILE=$TEST_PROFILE"
python -c "
import os
os.environ['TEST_PROFILE'] = 'docker'
from tests.conftest_profile import TEST_PROFILE_INFO
print(f'Environment: {TEST_PROFILE_INFO[\"environment\"]}')
print(f'Database: {TEST_PROFILE_INFO[\"database_url\"]}')
print(f'PostgreSQL: {TEST_PROFILE_INFO[\"postgres_host\"]}')
"

echo ""
echo "🔍 Test 3: Détection automatique"
echo "--------------------------------"
unset TEST_PROFILE
python -c "
import os
if 'TEST_PROFILE' in os.environ:
    del os.environ['TEST_PROFILE']
from tests.conftest_profile import TEST_PROFILE_INFO
print(f'Environment détecté: {TEST_PROFILE_INFO[\"environment\"]}')
print(f'Database: {TEST_PROFILE_INFO[\"database_url\"]}')
"

echo ""
echo "✅ Tests de profils terminés"