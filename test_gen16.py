#!/usr/bin/env python3
"""
Test script for GEN-16: Chat ↔ pgvector integration
Tests that brief generation stores embeddings in the database.
"""
import requests
import time

BASE_URL = "http://localhost:8002/api/v1"

# 1. Register a test user
print("1. Registering test user...")
register_data = {
    "email": f"test_gen16_{int(time.time())}@example.com",
    "password": "TestPassword123!",
    "name": "Test User GEN-16"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error: {response.text}")
    exit(1)

# 2. Login to get token
print("2. Getting JWT token...")
login_data = {
    "username": register_data["email"],
    "password": register_data["password"]
}
response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   Token: {token[:20]}...")

# 3. Send chat message to trigger brief generation
print("3. Sending chat message to generate brief...")
chat_data = {
    "message": "Je veux créer un site web pour mon restaurant sénégalais à Dakar. Nous servons des plats traditionnels avec une touche moderne.",
    "conversation_history": []
}
response = requests.post(f"{BASE_URL}/chat/", json=chat_data, headers=headers)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"   Brief generated: {result.get('brief_generated')}")
    print(f"   Brief ID: {result.get('brief_id')}")
    print(f"   Confidence: {result.get('orchestration_confidence')}")
    print(f"   Agents: {result.get('agents_status')}")
    
    if result.get('brief_generated'):
        print("\n✅ Brief generation successful!")
        print("4. Waiting 3 seconds for embedding to be stored...")
        time.sleep(3)
        print("\n5. Check database for embeddings manually:")
        print('   docker exec postgres psql -U genesis_user -d genesis_db -c "SELECT id, user_id, brief_id, embedding_type, metadata, created_at FROM user_embeddings ORDER BY created_at DESC LIMIT 1;"')
else:
    print(f"   Error: {response.text}")
    print("\nℹ️  Note: If orchestration fails, the embedding won't be stored (expected behavior)")
