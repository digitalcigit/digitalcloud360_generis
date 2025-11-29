## Contexte
- Phase 1A validée, Phase 1B (Moteur de rendu) engagée; livrables backend + frontend présents.
- Intégration DC360 en cours, blocages E2E liés au réseau Docker et au SSO cross-domain.

## Constats clés (code et docs)
- Endpoint Genesis aligné DC360 côté backend:
  - Génération brief (contrat interne): `app/api/v1/genesis.py:113` → `POST /api/v1/genesis/business-brief/`
  - Alias DC360: `app/api/dc360_adapter.py:238` → `POST /api/genesis/generate-brief/` (auth `X-Service-Secret`)
  - Router inclus: `app/main.py:309-314` (préfixe `/api/genesis`)
- Chat API (mock Phase 1B): `app/api/v1/chat.py:20` → `POST /api/v1/chat/`
- Transformer (brief → site): `app/services/transformer.py:7-20, 67-116`
- Sites API (génération/lecture): `app/api/v1/sites.py:24-66`, `app/api/v1/sites.py:67-84`
- Frontend renderer dynamique: `genesis-frontend/src/components/BlockRenderer.tsx:10-41`
- SSO Token Passing (déjà amorcé):
  - Validation token: `genesis-frontend/src/app/api/auth/validate/route.ts:4-20`
  - Session utilisateur: `genesis-frontend/src/app/api/auth/me/route.ts:16-28`
  - Réception token via URL & nettoyage: `genesis-frontend/src/context/AuthContext.tsx:28-55`
- Docker & réseau:
  - Backend exposé `8002→8000`, réseau dédié `genesis-ai-network`: `docker-compose.yml:19-41`, `docker-compose.yml:192-197`
  - Frontend appelle DC360 via `http://web:8000/api`: `docker-compose.yml:146` (nécessite réseau partagé avec le Hub)
- Sécurité JWT actuelle HS256: `app/core/security.py:12, 42, 48` (migration DC360 RS256 à faible impact immédiat)

## Écarts et risques
- 404 côté DC360 probable par isolation réseau (alias `/api/genesis/generate-brief/` est bien branché, mais conteneur Hub ne voit pas `genesis-api`).
- SSO local: cookies cross-domain en localhost nécessitent "Token URL Passing" (déjà amorcé, finalisation et DoD à valider).
- Mention de `HOSTNAME=0.0.0.0` confirmée dans mémo mais non retrouvée dans compose (à vérifier dans environnement Hub/DC360).

## Plan d’action
1. Réseau Docker unifié pour E2E
- Créer `digitalcloud360-network` partagé, y attacher `genesis-api` et `frontend`.
- Documenter URLs internes: `http://genesis-api:8000`, `http://web:8000`.
- Valider reachability par healthchecks.

2. Finaliser SSO Token Passing côté frontend
- Stocker `?token=` en cookie `access_token` et nettoyer l’URL; rediriger vers `/chat`.
- Vérifier détection session (`AuthContext`) et route `me`.

3. Vérifier contrat DC360 du wizard
- Confirmer payload attendu et mapping (adapter déjà en place): `app/api/dc360_adapter.py:182-231`.
- Test d’intégration avec `X-Service-Secret` (tests existants): `tests/test_dc360_adapter.py:112-297`.

4. Chaîne complète Brief → Site (démo)
- Générer un brief via alias `/api/genesis/generate-brief/`.
- Appeler `POST /api/v1/sites/generate` avec `brief_id`.
- Afficher `/sites/[id]` côté frontend.

5. Sécurité & migration JWT (RS256)
- Préparer lecture JWKS si validation nécessaire côté Genesis ultérieurement.
- Garder HS256 local pour l’API interne tant que DC360 assure gateway.

## Vérifications & livrables
- Test manuel E2E sur environnement Docker partagé (login Hub → Genesis → génération brief → rendu site).
- Journaliser preuves (logs, captures) et mettre à jour `docs/memo` d’acceptation.
- Rapporter écarts éventuels (réseau, CORS, variables d’environnement) et proposer correctifs.
