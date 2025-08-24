# 🎯 PROTOCOLE DE RECRUTEMENT - Développeurs IA-Assistés

**Basé sur l'expérience Genesis AI**  
**Créé par :** Équipe Genesis AI (USER + Cascade)  
**Date :** 22 août 2025  

---

## 📋 **Vue d'ensemble du Processus**

Ce protocole de recrutement vise à identifier les profils capables de **collaborer efficacement avec les IA** dans des projets de développement complexes, basé sur notre expérience réussie du projet Genesis AI.

### **🎯 Objectifs Tests**
1. **Capacité collaboration IA** : Utilisation productive des assistants IA
2. **Architecture thinking** : Vision systémique sans expertise POO avancée  
3. **Quality assurance** : Validation technique et tests
4. **Problem-solving** : Résolution de blocages complexes
5. **Project management** : Gestion de livrables et deadlines

---

## 🧪 **TEST 1 : Collaboration IA & Architecture (2h)**

### **Contexte Fourni au Candidat**
```
Un service de coaching IA pour entrepreneurs doit intégrer 3 APIs externes :
- API Recherche (comme Tavily)  
- API Génération Contenu (comme OpenAI)
- API Storage (comme Redis)

Mission : Concevoir l'architecture et implémenter la structure de base
```

### **Ressources Autorisées**
- **IA Assistant** (Claude, GPT, Cursor, etc.) - OBLIGATOIRE
- Documentation officielle des technologies
- Recherche web limitée (30 min max)

### **Livrables Attendus (2h)**
1. **Architecture diagram** (Mermaid ou autre)
2. **Structure code** Python/FastAPI avec intégrations
3. **Configuration Docker** basique  
4. **Tests unitaires** pour au moins 2 intégrations
5. **README** avec setup instructions

### **Critères d'Évaluation**
- ✅ **Utilisation IA productive** : Prompts efficaces, itérations rapides
- ✅ **Vision architecture** : Séparation concerns, modularité
- ✅ **Code quality** : Structure professionnelle, naming conventions
- ✅ **Documentation** : Clara et actionnable
- ✅ **Tests coverage** : Au moins 70% des fonctions critiques

### **Signaux Positifs**
- Pose questions pertinentes à l'IA
- Valide les suggestions avant implémentation  
- Structure projet de manière évolutive
- Anticipe les points de vigilance

### **Red Flags**
- Copie/colle aveugle des suggestions IA
- Architecture monolithique sans modularité
- Absence de gestion d'erreurs
- Documentation inexistante ou superficielle

---

## 🔍 **TEST 2 : Debug & Problem Solving (90 min)**

### **Scenario : "L'Incident TRAE"**
```
Vous héritez d'un projet où l'agent IA précédent (TRAE) a rencontré 
des blocages sur les tests d'authentification. 

Symptômes :
- Tests authentication : 3/6 passent
- Import app.main : ModuleNotFoundError  
- Docker startup : Container exits with code 1
- SQLAlchemy : AsyncIO conflicts

Code source fourni avec ces bugs intentionnels.
```

### **Mission**
1. **Diagnostic** : Identifier les causes racines (30 min)
2. **Resolution** : Corriger les bugs un par un (45 min)  
3. **Validation** : Prouver que ça marche (15 min)

### **Critères Succès**
- ✅ **6/6 tests authentication** passent
- ✅ **Application startup** sans erreur
- ✅ **Docker container** démarre correctement
- ✅ **Rapport diagnostic** structuré

### **Évaluation Compétences**
- **Méthodologie debug** : Approche systématique vs random
- **Collaboration IA** : Utilise l'assistant pour accélérer diagnostic
- **Documentation** : Trace les corrections appliquées
- **Testing** : Valide chaque correction avant next step

---

## 📊 **TEST 3 : Quality Assurance & Audit (60 min)**

### **Contexte : "Validation Work Order"**
```
Un autre développeur (Qoder) prétend avoir résolu 15 tâches critiques 
avec 97% de tests qui passent. 

Vous devez auditer ses affirmations et valider la production-readiness.
```

### **Documentation Fournie**
- Rapport Qoder avec métriques impressionnantes
- Code source modifié (avec quelques pièges subtils)
- Work order original avec critères succès

### **Mission Audit**
1. **Validation claims** : Tests réels vs affirmations (30 min)
2. **Code review** : Qualité architecture et implémentation (20 min)
3. **Rapport final** : Recommandation go/no-go (10 min)

### **Critères d'Excellence**
- **Skeptical mindset** : Vérifie avant d'approuver
- **Test execution** : Lance les tests pour confirmer les %
- **Architecture review** : Identifie les points faibles
- **Risk assessment** : Anticipe les problèmes production

---

## 🎯 **TEST 4 : Project Leadership (45 min)**

### **Scenario Management**
```
Vous devez créer un work order pour une équipe de 2 développeurs IA 
pour implémenter un module "Analytics & Reporting" dans Genesis AI.

Fonctionnalités requises :
- Dashboard metrics business
- Export PDF rapports  
- API endpoints analytics
- Integration base de données existante
```

### **Livrables**
1. **Work order structuré** avec tâches définies
2. **Planning timeline** réaliste  
3. **Critères acceptation** mesurables
4. **Risk assessment** avec mitigation

### **Évaluation Leadership**
- **Task breakdown** : Décomposition logique et actionnable
- **Resource planning** : Estimation réaliste charges
- **Quality gates** : Checkpoints et validation steps
- **Communication** : Clarté instructions pour développeurs

---

## 🏆 **SCORING & PROFILS**

### **Barème de Notation (Total /100)**
- **Test 1 - Architecture** : /30 points
- **Test 2 - Problem Solving** : /30 points  
- **Test 3 - Quality Assurance** : /25 points
- **Test 4 - Project Leadership** : /15 points

### **Profils Candidats**

#### **🥇 Senior IA-Assisted Developer (85-100 points)**
- **Autonomie complète** : Peut gérer projet end-to-end
- **Mentoring capability** : Peut former autres développeurs  
- **Architecture leadership** : Conçoit solutions scalables
- **Business impact** : Comprend enjeux métier

**Rôle recommandé :** Technical Lead ou Project Owner

#### **🥈 Confirmed IA-Assisted Developer (70-84 points)**  
- **Collaboration productive IA** : Utilise assistants efficacement
- **Code quality standard** : Livre du code maintenable
- **Problem solving** : Résout blocages avec support minimal
- **Team player** : S'intègre bien dans équipe

**Rôle recommandé :** Développeur sénior avec supervision légère

#### **🥉 Junior IA-Assisted Developer (55-69 points)**
- **Potentiel confirmé** : Bases solides pour progression
- **Apprentissage rapide** : S'adapte aux nouveaux outils
- **Collaboration** : Travaille bien avec supervision
- **Motivation** : Intérêt genuine pour développement IA-assisté  

**Rôle recommandé :** Développeur junior avec mentoring

#### **❌ Non-Compatible (<55 points)**
- Résistance outils IA ou utilisation inefficace
- Approche trop traditionnelle incompatible
- Qualité code insuffisante même avec assistance
- Manque vision architecture globale

---

## 🎨 **VARIANTES DE TESTS**

### **Pour Profil "Integration Specialist"**
- **Focus DevOps** : Docker-compose complexe, CI/CD pipeline
- **Monitoring emphasis** : Prometheus metrics, health checks
- **Infrastructure as Code** : Terraform ou équivalent

### **Pour Profil "Technical Conductor"**  
- **Multi-project management** : Coordination 3 projets parallèles
- **Stakeholder communication** : Rapports exec et techniques
- **Resource allocation** : Optimisation charge équipe

### **Pour Profil "IA-Native Developer"**
- **Advanced prompting** : Optimisation interactions LLM
- **Model comparison** : Choix tech stack selon use case
- **Performance tuning** : Optimisation réponse time APIs

---

## 📈 **RECOMMANDATIONS POST-RECRUTEMENT**

### **Onboarding Process (2 semaines)**
1. **Formation outils IA** : Windsurf, Cursor, Copilot, Claude
2. **Architecture Genesis** : Deep dive code existant  
3. **Collaboration patterns** : Standards équipe et workflows
4. **Quality standards** : Tests, documentation, validation

### **Période d'Évaluation (3 mois)**
- **Projet pilote** : Module complet en autonomie
- **Code reviews** : Évaluation qualité continue  
- **Feedback loops** : Ajustements et amélioration
- **Performance metrics** : Velocity, quality, collaboration

---

**Protocole créé basé sur l'expérience Genesis AI**  
**Validé par l'équipe USER + Cascade - Août 2025**
