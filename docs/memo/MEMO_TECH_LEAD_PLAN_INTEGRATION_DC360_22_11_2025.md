---
DE: Tech Lead / Senior Dev IA (agnissaneric)
À: Scrum Master (Cascade)
DATE: 2025-11-22 02:15 AM
OBJET: Proposition Plan Intégration Genesis AI ↔ DigitalCloud360
PRIORITÉ: HAUTE
---

# PLAN INTÉGRATION GENESIS AI ↔ DIGITALCLOUD360

## 1. CONTEXTE

**Sprint 2 Genesis AI : ✅ CLÔTURÉ (validé par Scrum Master)**

Livrables production-ready :
- ✅ Orchestrateur LangGraph opérationnel
- ✅ Providers LLM réels (Deepseek, Kimi, DALL-E)
- ✅ Redis Virtual FS persistance
- ✅ 34 tests validés (100% success rate)

**Prochaine étape** : Intégration avec DigitalCloud360 (backend + frontend)

---

## 2. OBJECTIF GLOBAL

**Permettre aux utilisateurs DC360 de générer des business briefs via Genesis AI de manière transparente**

Workflow cible :
```
Utilisateur DC360 → Wizard Genesis AI Coach → API Genesis → 
Orchestrateur → Providers LLM → Redis FS → DC360 (création site)
```

---

## 3. PLAN PROPOSÉ - 6 PHASES

### 📋 PHASE 1 : VALIDATION PRÉ-INTÉGRATION
**Durée** : 1-2 jours  
**Responsable** : Tech Lead Genesis AI

#### Objectif
S'assurer que Genesis AI est prêt pour l'intégration

#### Actions

**1.1. Tests manuels end-to-end** (2-3h)
- Générer 3-5 business briefs réels via Postman/cURL
- Valider qualité outputs :
  - Analyse marché pertinente (Tavily/Kimi)
  - Contenu cohérent (homepage, about, services)
  - Format JSON structuré correct
  - Temps génération acceptable (< 40s)
- Documenter cas d'usage testés
- Identifier problèmes qualité éventuels

**1.2. Smoke tests environnement cible** (1-2h)
- Health checks tous services (API, Redis, DB)
- Connexion Redis staging/prod
- Validation providers (quotas API, timeouts)
- Logs structlog visibles et exploitables

**1.3. Documentation API** (2-3h)
- Finaliser OpenAPI/Swagger endpoint `/business-brief`
- Exemples payloads request/response
- Codes erreur HTTP + gestion
- Guide troubleshooting rapide

#### Livrables
- [ ] Checklist validation qualité Genesis AI
- [ ] Documentation API OpenAPI complète
- [ ] Rapport tests manuels (cas d'usage + résultats)

---

### 🔗 PHASE 2 : COORDINATION INTÉGRATION DC360
**Durée** : 2-3 jours  
**Responsables** : Tech Leads Genesis + DC360 Backend + Frontend

#### Objectif
Aligner contrats API et séquences d'appels entre Genesis AI et DC360

#### Actions

**2.1. Meeting coordination équipes** (1h)
Participants :
- Tech Lead Genesis AI (moi)
- Tech Lead Backend DC360
- Tech Lead Frontend DC360
- Scrum Master

Ordre du jour :
- Présentation architecture Genesis AI (endpoints, formats)
- Revue workflow utilisateur DC360
- Identification endpoints manquants
- Séquence appels API (sync vs async)
- Gestion erreurs et timeouts

**2.2. Spécifications techniques intégration** (2-3h)
- Format exact `BusinessBriefRequest` (payload DC360 → Genesis)
- Format exact response Genesis → DC360
- Gestion erreurs (403 quotas, 429 rate limit, 500 timeout)
- Quotas par plan (Trial, Basic, Pro, Enterprise)
- Rate limiting (ex: 5 req/min par user)

**2.3. Endpoints manquants à créer** (analyse)
Identifier si besoin :
- `GET /business-brief/{id}` : Récupération brief existant
- `GET /business-brief/user/{user_id}` : Liste briefs utilisateur
- `GET /business-brief/{id}/status` : Progression génération temps réel
- `POST {DC360_WEBHOOK}/genesis/brief-completed` : Notification async (optionnel)

**2.4. Configuration environnements** (1-2h)
- Variables env staging/prod
- Secrets management (API keys providers)
- URLs DC360 staging vs prod
- CORS + authentification service-to-service
- DNS/certificats SSL

#### Livrables
- [ ] Compte-rendu meeting coordination
- [ ] Spécifications techniques intégration (document)
- [ ] Liste endpoints à développer (priorisés)
- [ ] Configuration environnements validée

---

### 🏗️ PHASE 3 : DÉVELOPPEMENT ENDPOINTS INTÉGRATION
**Durée** : 3-5 jours  
**Responsable** : Tech Lead Genesis AI

#### Objectif
Implémenter endpoints nécessaires côté Genesis AI pour intégration DC360

#### Stories

**Story INT-1 : Endpoint récupération brief existant** (1 jour)
```python
GET /api/v1/business-brief/{brief_id}
Authorization: Bearer {jwt_token}
```

Fonctionnalités :
- Lecture depuis Redis FS (`read_session`)
- Autorisation user_id ownership (JWT claims)
- Format réponse standardisé
- Gestion 404 si brief inexistant
- Gestion 403 si user non autorisé

Tests :
- [ ] Test récupération brief existant (200)
- [ ] Test brief inexistant (404)
- [ ] Test ownership (403)
- [ ] Test sans auth (401)

**Story INT-2 : Endpoint liste briefs utilisateur** (1 jour)
```python
GET /api/v1/business-brief/user/{user_id}?limit=10&offset=0
Authorization: Bearer {jwt_token}
```

Fonctionnalités :
- Liste sessions via Redis FS (`list_user_sessions`)
- Pagination (limit, offset)
- Filtres (status, date_from, date_to)
- Tri (created_at DESC)
- Métadonnées (total_count)

Tests :
- [ ] Test liste vide (200)
- [ ] Test liste avec briefs (200)
- [ ] Test pagination
- [ ] Test filtres

**Story INT-3 : Endpoint statut génération** (1-2 jours)
```python
GET /api/v1/business-brief/{brief_id}/status
Authorization: Bearer {jwt_token}
```

Fonctionnalités :
- Status temps réel (pending, generating, completed, failed)
- Progression sub-agents (research: 100%, content: 50%, etc.)
- Temps écoulé / estimé restant
- Logs erreurs si échec
- WebSocket ou SSE pour updates temps réel (optionnel)

Tests :
- [ ] Test status pending
- [ ] Test status generating
- [ ] Test status completed
- [ ] Test status failed

**Story INT-4 : Webhook post-génération** (optionnel - 1 jour)
```python
POST {DC360_WEBHOOK_URL}/genesis/brief-completed
X-Service-Secret: {secret}
Body: {brief_id, user_id, status, url}
```

Fonctionnalités :
- Notification DC360 quand brief prêt
- Retry logic (3 tentatives avec exponential backoff)
- Logs échecs webhook
- Configuration URL webhook via env var

Tests :
- [ ] Test webhook succès (200)
- [ ] Test webhook retry
- [ ] Test webhook fail après retries

#### Livrables
- [ ] 3-4 nouveaux endpoints implémentés
- [ ] Tests unitaires (15-20 tests)
- [ ] Documentation OpenAPI mise à jour

---

### 🧪 PHASE 4 : TESTS INTÉGRATION E2E
**Durée** : 2-3 jours  
**Responsable** : Tech Lead Genesis AI + QA

#### Objectif
Valider flux complet DC360 ↔ Genesis AI en conditions réelles

#### Tests à créer

**Test E2E-1 : Workflow complet création brief** (1 jour)
```
DC360 Frontend → DC360 Backend → Genesis API → 
Orchestrateur → Providers → Redis FS → 
Response Genesis → DC360 Backend → DC360 Frontend
```

Scénario :
1. Authentification user DC360 (JWT)
2. Envoi payload BusinessBriefRequest
3. Génération via Genesis (orchestrateur + sub-agents)
4. Persistance Redis FS
5. Récupération résultats
6. Validation format + qualité
7. Création site web DC360 (optionnel)

Validations :
- [ ] Authentification service-to-service OK
- [ ] Payload correctement mappé
- [ ] Génération < 40s
- [ ] Résultats structurés complets
- [ ] Persistance Redis OK
- [ ] Logs traçabilité complets

**Test E2E-2 : Quotas & limites** (1 jour)

Scénarios :
- User Trial : 10 briefs → 11ème rejeté (403)
- User Pro : 50 briefs → 51ème rejeté (403)
- Rate limiting : 6 req/min → 6ème rejetée (429)
- Quota reset mensuel vérifié

Validations :
- [ ] Quotas Trial respectés
- [ ] Quotas Pro respectés
- [ ] Rate limiting fonctionnel
- [ ] Messages erreur clairs

**Test E2E-3 : Gestion erreurs & fallback** (1 jour)

Scénarios :
- Timeout génération (> 60s) → 504
- Provider API fail (Deepseek down) → fallback OpenAI
- Redis unavailable → 503
- DC360 API unavailable → fallback mode (si applicable)

Validations :
- [ ] Timeout géré gracieusement
- [ ] Fallback providers automatique
- [ ] Messages erreur exploitables
- [ ] Logs erreurs détaillés

#### Livrables
- [ ] Suite tests E2E intégration (10-15 tests)
- [ ] Rapport tests (cas passés, échoués, bugs identifiés)
- [ ] Fixes bugs critiques bloquants

---

### 🚀 PHASE 5 : DÉPLOIEMENT STAGING
**Durée** : 1-2 jours  
**Responsable** : Tech Lead Genesis + DevOps

#### Objectif
Mettre Genesis AI disponible en environnement staging pour tests DC360

#### Actions

**5.1. Configuration staging** (1 jour)
- Variables env staging (DB, Redis, providers API keys)
- DNS/URLs (ex: `genesis-staging.digitalcloud360.com`)
- Certificats SSL
- Monitoring/alertes (Prometheus, logs)
- Backup Redis staging

**5.2. Déploiement** (2-4h)
- Build Docker image (`genesis-ai:staging-{version}`)
- Push registry
- Deploy via CI/CD (GitHub Actions ou équivalent)
- Healthchecks validation (`/health`)
- Smoke tests post-deploy

**5.3. Tests intégration staging** (1 jour)
- Tests avec frontend DC360 staging
- Workflows utilisateur réels (wizard Genesis Coach)
- Performance (temps génération moyen)
- Logs/monitoring vérifiés
- Correction bugs staging

#### Livrables
- [ ] Genesis AI opérationnel en staging
- [ ] Documentation déploiement
- [ ] Runbook incidents staging
- [ ] Accès équipe DC360 pour tests

---

### 📊 PHASE 6 : MONITORING & OPTIMISATION (Continu)
**Durée** : Continu post-déploiement  
**Responsable** : Tech Lead Genesis AI

#### Objectif
Observer comportement production et optimiser performances/coûts

#### Actions

**6.1. Metrics & Dashboards**
- Prometheus + Grafana
- Métriques clés :
  - Temps génération moyen/médian/p95
  - Taux succès/échec (%)
  - Utilisation providers (coûts $)
  - Erreurs par type (timeout, quota, API fail)
  - Requêtes par heure/jour

**6.2. Optimisations identifiées**
- Cache Redis résultats similaires (secteur + pays)
- Optimisation prompts (réduction tokens)
- Parallélisation sub-agents (research || content)
- CDN pour logos générés DALL-E
- Compression réponses API

**6.3. Support & Bug fixes**
- Hotfixes bugs critiques (< 4h)
- Amélioration qualité outputs (feedback users)
- Ajustement timeouts/quotas selon usage réel
- Documentation troubleshooting enrichie

#### Livrables
- [ ] Dashboards Grafana opérationnels
- [ ] Alertes critiques configurées
- [ ] Plan optimisation performances
- [ ] Backlog améliorations continues

---

## 4. PLANNING PROPOSÉ - SPRINT INTÉGRATION

**Durée totale** : 2-3 semaines

| Semaine | Phases | Livrables Clés |
|---------|--------|----------------|
| **Semaine 1** | Phase 1-2-3 | API docs, 3-4 endpoints, tests unitaires |
| **Semaine 2** | Phase 4-5 | Tests E2E, déploiement staging |
| **Semaine 3** | Phase 6 + Validation | Tests avec DC360, monitoring, fixes |

### Timeline Détaillée

**Jours 1-2** : Validation pré-intégration + Coordination
- Tests manuels Genesis AI
- Meeting équipes
- Spécifications techniques

**Jours 3-7** : Développement endpoints
- GET `/business-brief/{id}`
- GET `/business-brief/user/{user_id}`
- GET `/business-brief/{id}/status`
- Webhook (optionnel)

**Jours 8-10** : Tests E2E
- Workflow complet DC360 ↔ Genesis
- Quotas & rate limiting
- Gestion erreurs

**Jours 11-12** : Déploiement staging
- Configuration env
- Deploy + smoke tests
- Tests avec frontend DC360

**Jours 13-15** : Validation + Polish
- Tests utilisateurs
- Fixes bugs
- Optimisations
- Documentation finale

---

## 5. RESSOURCES NÉCESSAIRES

### Équipe

| Rôle | Responsabilité | Disponibilité |
|------|----------------|---------------|
| Tech Lead Genesis AI | Développement endpoints, tests, deploy | 100% (2-3 semaines) |
| Tech Lead Backend DC360 | Coordination API, tests intégration | 30% (reviews, support) |
| Tech Lead Frontend DC360 | Tests UI, feedback UX | 20% (tests staging) |
| DevOps | Configuration staging, deploy | 20% (setup initial + support) |
| QA (optionnel) | Tests E2E validation | 30% (semaine 2-3) |
| Scrum Master | Coordination, priorisation | 10% (meetings, reviews) |

### Infrastructure

- [ ] Environnement staging Genesis AI (serveur, DB, Redis)
- [ ] Environnement staging DC360 (frontend + backend)
- [ ] Accès inter-services (network, firewall)
- [ ] Monitoring (Prometheus, Grafana, logs centralisés)
- [ ] CI/CD pipeline (GitHub Actions ou équivalent)

---

## 6. RISQUES & MITIGATIONS

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Délais dépassés développement endpoints** | MOYEN | MOYENNE | ✅ Prioriser endpoints critiques (GET brief, liste), reporter optionnels (webhook) |
| **Bugs découverts tests E2E** | ÉLEVÉ | ÉLEVÉE | ✅ Buffer 2-3 jours fixes semaine 3 |
| **Performance génération > 40s** | MOYEN | MOYENNE | ✅ Optimisation prompts, cache Redis, parallélisation |
| **Indisponibilité providers LLM** | ÉLEVÉ | FAIBLE | ✅ Fallback automatique déjà implémenté (Deepseek → OpenAI) |
| **Quotas inconsistants DC360 ↔ Genesis** | ÉLEVÉ | MOYENNE | ✅ Aligner logique quotas lors Phase 2 (coordination) |
| **Environnement staging pas prêt** | ÉLEVÉ | FAIBLE | ✅ Validation disponibilité infrastructure Jour 1 |

---

## 7. CRITÈRES DE SUCCÈS

### Must-Have (bloquants production)

- [ ] Workflow complet DC360 → Genesis → DC360 validé
- [ ] Au moins 10 business briefs générés avec succès en staging
- [ ] Temps génération < 40s (moyenne)
- [ ] Taux succès > 95%
- [ ] Quotas Trial/Pro respectés
- [ ] Gestion erreurs robuste (timeouts, quotas, API fails)
- [ ] Logs traçabilité complets
- [ ] Documentation API complète

### Nice-to-Have (améliorations post-lancement)

- [ ] Webhook notifications async
- [ ] Cache Redis résultats similaires
- [ ] SSE/WebSocket progression temps réel
- [ ] Dashboards Grafana complets
- [ ] Tests charge (100 req/min)

---

## 8. PROCHAINES ACTIONS IMMÉDIATES

### Cette semaine (Jours 1-5)

**AUJOURD'HUI** :
1. ✅ Soumettre ce plan au Scrum Master (FAIT)
2. Attendre validation/ajustements plan
3. Si validé → démarrer Phase 1 (tests manuels)

**DEMAIN** :
1. Finaliser tests manuels Genesis AI (3-5 briefs)
2. Documenter résultats + problèmes identifiés
3. Planifier meeting coordination équipes

**Cette semaine** :
1. Meeting coordination Tech Leads (DC360 + Genesis)
2. Spécifications techniques intégration
3. Démarrage développement endpoints prioritaires

---

## 9. QUESTIONS POUR LE SCRUM MASTER

### Planning

1. **Timeline validée ?** Sprint intégration 2 ou 3 semaines ?
2. **Date démarrage ?** Semaine prochaine ou après ?
3. **Jalons intermédiaires ?** Reviews hebdo ? Daily standup ?

### Équipes & Ressources

4. **Coordination DC360** :
   - Qui est le Tech Lead Backend DC360 à contacter ?
   - Qui est le Tech Lead Frontend DC360 ?
   - Disponibilité pour meeting coordination (1h) ?

5. **DevOps** :
   - Qui peut configurer environnement staging ?
   - Infrastructure déjà provisionnée ?
   - Accès nécessaires à demander ?

6. **QA** :
   - Besoin ressource QA dédiée pour tests E2E ?
   - OU Tech Leads font tests eux-mêmes ?

### Priorisation

7. **Endpoints critiques** :
   - GET `/business-brief/{id}` : MUST HAVE confirmé ?
   - GET `/business-brief/user/{user_id}` : MUST HAVE confirmé ?
   - GET `/business-brief/{id}/status` : NICE TO HAVE ?
   - Webhook : NICE TO HAVE (reporter) ?

8. **Environnements** :
   - Staging DC360 frontend disponible quand ?
   - Staging DC360 backend accessible pour tests ?
   - URLs staging déjà définies ?

### Critères Succès

9. **Validation finale** :
   - Combien de briefs test minimum ? (proposé : 10)
   - Performance acceptable ? (proposé : < 40s moyenne)
   - Taux succès minimum ? (proposé : > 95%)

10. **Production** :
    - Déploiement prod prévu quand après staging ?
    - Tests utilisateurs réels organisés ?
    - Beta testeurs identifiés ?

---

## 10. AJUSTEMENTS POSSIBLES

**Si planning 2 semaines au lieu de 3** :
- Reporter Phase 6 (monitoring) post-lancement
- Limiter endpoints à 2 critiques (GET brief, liste)
- Réduire tests E2E au strict minimum
- Prioriser validation workflow complet

**Si ressources limitées** :
- Tech Lead Genesis fait tout développement seul (faisable)
- Tests E2E manuels au lieu de scripts automatisés
- Déploiement staging simplifié (Docker Compose au lieu K8s)

**Si besoins changent** :
- Ajustement priorités endpoints selon feedback DC360
- Adaptation format payloads si spécifications évoluent
- Ajout/suppression stories selon complexité découverte

---

**Prêt à ajuster ce plan selon tes retours et démarrer dès validation !** 🚀

---

**Signature Tech Lead**  
Eric Agnissan  
Senior Dev IA - Genesis AI  
2025-11-22 02:15 AM
