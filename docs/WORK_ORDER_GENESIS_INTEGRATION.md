# WORK ORDER - INTÉGRATION GENESIS AI DANS DIGITALCLOUD360

**Date:** 25 Août 2025  
**Chef de Projet:** Cascade  
**Développeur:** Qoder  
**Objectif:** Intégrer Genesis AI dans le dashboard DigitalCloud360 existant

---

## 🎯 **OBJECTIF GLOBAL**

Intégrer Genesis AI comme nouveau service dans la plateforme DigitalCloud360, permettant aux utilisateurs d'accéder au coaching IA directement depuis leur dashboard principal.

### **Workflow Utilisateur Final**
```
1. Utilisateur → Login DigitalCloud360 Dashboard
2. Dashboard vérifie → Abonnement Genesis AI actif ?
3. Si actif → Affiche carte "Genesis AI Coach" 
4. Clic carte → Pages coaching intégrées
5. Interface coaching → Appels API Genesis AI
6. Résultats → Affichage dans dashboard
```

---

## 📋 **TÂCHES DÉTAILLÉES**

### **PHASE 1: BACKEND DJANGO - GESTION ABONNEMENTS (4h)**

#### **Tâche 1.1: Créer ServiceCategory Genesis AI**
```python
# Dans apps/subscription_module/management/commands/setup_genesis_category.py
from apps.subscription_module.models import ServiceCategory, Plan, PlanPricing

# Créer catégorie Genesis AI
category = ServiceCategory.objects.create(
    name="Genesis AI",
    description="Coach IA personnel pour entrepreneurs africains",
    slug="genesis-ai", 
    icon="brain",
    is_active=True
)
```

#### **Tâche 1.2: Créer Plans Genesis AI**
```python
# Plan Genesis AI Basic
basic_plan = Plan.objects.create(
    name="Genesis AI Basic",
    description="Coach IA avec 5 sub-agents spécialisés",
    category=category,
    is_active=True
)

# Tarification mensuelle/annuelle
PlanPricing.objects.create(
    plan=basic_plan,
    billing_cycle="monthly",
    price=29.99,
    currency="EUR"
)

PlanPricing.objects.create(
    plan=basic_plan, 
    billing_cycle="yearly",
    price=299.99,
    currency="EUR"
)
```

#### **Tâche 1.3: API Vérification Abonnement Genesis**
```python
# Dans apps/api_module/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_genesis_subscription(request):
    """Vérifier si utilisateur a abonnement Genesis AI actif."""
    try:
        subscription = request.user.subscriptions.filter(
            plan__category__slug='genesis-ai',
            status__in=['active', 'trial']
        ).first()
        
        return Response({
            'has_genesis': bool(subscription),
            'plan_name': subscription.plan.name if subscription else None,
            'status': subscription.status if subscription else None
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# URL: /api/subscriptions/genesis-check/
```

#### **Tâche 1.4: API Gateway Genesis AI**
```python
# Dans apps/api_gateway/views.py
import httpx
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def genesis_business_brief(request):
    """Proxy vers Genesis AI pour génération business brief."""
    # 1. Vérifier abonnement Genesis
    if not has_genesis_subscription(request.user):
        return Response({'error': 'Genesis subscription required'}, status=403)
    
    # 2. Préparer données pour Genesis AI
    genesis_data = {
        'user_id': request.user.id,
        'coaching_session_id': request.data.get('session_id'),
        'business_brief': request.data.get('business_brief')
    }
    
    # 3. Appel Genesis AI API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.GENESIS_AI_API_URL}/api/v1/business/brief/generate",
            json=genesis_data,
            headers={
                'Authorization': f'Bearer {get_genesis_service_token()}',
                'Content-Type': 'application/json'
            }
        )
    
    return Response(response.json())
```

### **PHASE 2: FRONTEND REACT - DASHBOARD EXTENSION (3h)**

#### **Tâche 2.1: Extension SubscriptionContext**
```jsx
// Dans src/contexts/SubscriptionContext.jsx
const SubscriptionContext = createContext();

export const SubscriptionProvider = ({ children }) => {
    const [genesisSubscription, setGenesisSubscription] = useState(null);
    const [canAccessGenesis, setCanAccessGenesis] = useState(false);

    useEffect(() => {
        const checkGenesisSubscription = async () => {
            try {
                const response = await api.get('/api/subscriptions/genesis-check/');
                setGenesisSubscription(response.data);
                setCanAccessGenesis(response.data.has_genesis);
            } catch (error) {
                console.error('Genesis subscription check failed:', error);
            }
        };

        checkGenesisSubscription();
    }, []);

    return (
        <SubscriptionContext.Provider value={{
            // ... existing values
            genesisSubscription,
            canAccessGenesis
        }}>
            {children}
        </SubscriptionContext.Provider>
    );
};
```

#### **Tâche 2.2: Nouvelle Carte Genesis AI Dashboard**
```jsx
// Dans src/pages/DashboardPage.jsx - Ajouter après ligne 350

{/* Genesis AI Coach Card - Only if user has Genesis subscription */}
{canAccessGenesis && (
    <Grid item xs={12} md={6}>
        <Card
            elevation={2}
            sx={{
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                    elevation: 4,
                    transform: 'translateY(-2px)'
                },
                display: 'flex',
                flexDirection: 'column',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
        >
            <CardContent sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                flexGrow: 1
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{
                        bgcolor: '#7c3aed',
                        borderRadius: '50%',
                        p: 1,
                        mr: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <SmartToy sx={{ color: 'white' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'white' }}>
                        Genesis AI Coach
                    </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 3, flexGrow: 1, color: 'rgba(255,255,255,0.9)' }}>
                    Votre coach IA personnel pour développer votre business avec 5 agents spécialisés.
                </Typography>
                <Button
                    variant="contained"
                    onClick={() => navigate('/genesis-coaching')}
                    fullWidth
                    size="large"
                    startIcon={<SmartToy />}
                    sx={{
                        borderRadius: 2,
                        textTransform: 'none',
                        fontWeight: 600,
                        mt: 'auto',
                        bgcolor: '#7c3aed',
                        '&:hover': {
                            bgcolor: '#6d28d9'
                        }
                    }}
                >
                    🚀 Démarrer Mon Coaching
                </Button>
            </CardContent>
        </Card>
    </Grid>
)}
```

#### **Tâche 2.3: Pages Coaching Genesis Intégrées**
```jsx
// Créer src/pages/GenesisCoachingPage.jsx
import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Typography } from '@mui/material';

const GenesisCoachingPage = () => {
    const [activeStep, setActiveStep] = useState(0);
    const [businessBrief, setBusinessBrief] = useState({});

    const steps = [
        'Informations Business',
        'Marché & Clientèle', 
        'Génération IA',
        'Résultats & Site Web'
    ];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, textAlign: 'center' }}>
                🤖 Genesis AI Coach - Votre Assistant Entrepreneur
            </Typography>
            
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                {steps.map((label) => (
                    <Step key={label}>
                        <StepLabel>{label}</StepLabel>
                    </Step>
                ))}
            </Stepper>

            {/* Wizard Steps Components */}
            {activeStep === 0 && <BusinessInfoStep />}
            {activeStep === 1 && <MarketInfoStep />}
            {activeStep === 2 && <AIGenerationStep />}
            {activeStep === 3 && <ResultsStep />}
        </Container>
    );
};

export default GenesisCoachingPage;
```

### **PHASE 3: COMPOSANTS COACHING WIZARD (4h)**

#### **Tâche 3.1: Composant BusinessInfoStep**
```jsx
// src/components/genesis/BusinessInfoStep.jsx
const BusinessInfoStep = ({ businessBrief, setBusinessBrief, onNext }) => {
    return (
        <Card sx={{ p: 4 }}>
            <Typography variant="h5" sx={{ mb: 3 }}>
                Parlez-nous de votre business
            </Typography>
            
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <TextField
                        fullWidth
                        label="Nom de votre business"
                        value={businessBrief.business_name || ''}
                        onChange={(e) => setBusinessBrief({
                            ...businessBrief, 
                            business_name: e.target.value
                        })}
                    />
                </Grid>
                
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Votre vision"
                        placeholder="Quelle est votre vision pour ce business ?"
                        value={businessBrief.vision || ''}
                        onChange={(e) => setBusinessBrief({
                            ...businessBrief,
                            vision: e.target.value
                        })}
                    />
                </Grid>
                
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        multiline  
                        rows={3}
                        label="Votre mission"
                        placeholder="Quelle est la mission de votre business ?"
                        value={businessBrief.mission || ''}
                        onChange={(e) => setBusinessBrief({
                            ...businessBrief,
                            mission: e.target.value
                        })}
                    />
                </Grid>
            </Grid>

            <Button 
                variant="contained" 
                onClick={onNext}
                sx={{ mt: 3 }}
                disabled={!businessBrief.business_name || !businessBrief.vision}
            >
                Suivant
            </Button>
        </Card>
    );
};
```

#### **Tâche 3.2: Composant AIGenerationStep**
```jsx
// src/components/genesis/AIGenerationStep.jsx
const AIGenerationStep = ({ businessBrief, onComplete }) => {
    const [generating, setGenerating] = useState(false);
    const [progress, setProgress] = useState({
        research: false,
        content: false, 
        logo: false,
        seo: false,
        template: false
    });

    const startGeneration = async () => {
        setGenerating(true);
        
        try {
            const response = await api.post('/api/genesis/business-brief/', {
                session_id: Date.now(),
                business_brief: businessBrief
            });
            
            // Simuler progression agents
            const agents = ['research', 'content', 'logo', 'seo', 'template'];
            for (let i = 0; i < agents.length; i++) {
                setTimeout(() => {
                    setProgress(prev => ({
                        ...prev,
                        [agents[i]]: true
                    }));
                }, (i + 1) * 2000);
            }
            
            setTimeout(() => {
                setGenerating(false);
                onComplete(response.data);
            }, 12000);
            
        } catch (error) {
            console.error('Genesis generation failed:', error);
            setGenerating(false);
        }
    };

    return (
        <Card sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" sx={{ mb: 4 }}>
                🤖 Genesis AI travaille pour vous...
            </Typography>

            <Box sx={{ mb: 4 }}>
                {[
                    { key: 'research', label: 'Agent Recherche', icon: '🔍' },
                    { key: 'content', label: 'Agent Contenu', icon: '✍️' },
                    { key: 'logo', label: 'Agent Logo', icon: '🎨' },
                    { key: 'seo', label: 'Agent SEO', icon: '🔍' },
                    { key: 'template', label: 'Agent Template', icon: '🎨' }
                ].map((agent) => (
                    <Box key={agent.key} sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        mb: 2,
                        p: 2,
                        bgcolor: progress[agent.key] ? 'success.light' : 'grey.100',
                        borderRadius: 2
                    }}>
                        <Typography sx={{ mr: 2 }}>{agent.icon}</Typography>
                        <Typography sx={{ flexGrow: 1, textAlign: 'left' }}>
                            {agent.label}
                        </Typography>
                        {progress[agent.key] ? (
                            <CheckCircle color="success" />
                        ) : (
                            <CircularProgress size={20} />
                        )}
                    </Box>
                ))}
            </Box>

            {!generating && (
                <Button
                    variant="contained"
                    size="large" 
                    onClick={startGeneration}
                    startIcon={<SmartToy />}
                >
                    Démarrer Genesis AI
                </Button>
            )}
        </Card>
    );
};
```

### **PHASE 4: CONFIGURATION & TESTS (2h)**

#### **Tâche 4.1: Configuration Django Settings**
```python
# Dans backend/digitalcloud360/settings.py - Ajouter
GENESIS_AI_API_URL = os.getenv('GENESIS_AI_API_URL', 'http://localhost:8001')
GENESIS_AI_SERVICE_SECRET = os.getenv('GENESIS_AI_SERVICE_SECRET', 'your-service-secret')
```

#### **Tâche 4.2: URL Routing**
```python
# Dans backend/digitalcloud360/urls.py
urlpatterns = [
    # ... existing patterns
    path('api/genesis/', include('apps.api_gateway.urls')),
    path('api/subscriptions/', include('apps.subscription_module.urls')),
]

# Dans frontend/src/App.jsx - Ajouter route
<Route path="/genesis-coaching" element={<GenesisCoachingPage />} />
```

#### **Tâche 4.3: Tests End-to-End**
```javascript
// e2e-tests/genesis-integration.spec.js
describe('Genesis AI Integration', () => {
    test('should show Genesis card for subscribed user', async () => {
        // 1. Login user with Genesis subscription
        await page.goto('/login');
        await page.fill('[name="email"]', 'user@genesis.test');
        await page.fill('[name="password"]', 'password');
        await page.click('button[type="submit"]');

        // 2. Verify Genesis card appears
        await page.waitForSelector('[data-testid="genesis-card"]');
        
        // 3. Click Genesis card
        await page.click('[data-testid="genesis-card"] button');
        
        // 4. Verify coaching page loads
        await page.waitForSelector('h4:has-text("Genesis AI Coach")');
        
        expect(page.url()).toContain('/genesis-coaching');
    });
    
    test('should generate business brief', async () => {
        // Test coaching workflow complet
        await fillBusinessInfo();
        await fillMarketInfo();
        await clickGenerateAI();
        await waitForResults();
        
        expect(await page.textContent('[data-testid="results"]')).toContain('Brief généré');
    });
});
```

---

## ⚡ **CRITÈRES DE SUCCÈS**

### **Fonctionnalités**
- ✅ Carte Genesis AI apparaît pour utilisateurs abonnés
- ✅ Workflow coaching step-by-step fonctionnel
- ✅ Intégration API Genesis AI opérationnelle
- ✅ Génération business brief complète
- ✅ Design cohérent avec dashboard existant

### **Technique**
- ✅ Tests E2E passent
- ✅ API Gateway opérationnel
- ✅ Gestion erreurs robuste
- ✅ Performance acceptable (<3s génération)
- ✅ Compatible mobile/desktop

### **UX**
- ✅ Navigation fluide dashboard → coaching
- ✅ Feedback visuel progression agents
- ✅ Messages d'erreur explicites
- ✅ Design cohérent Material-UI

---

## 📋 **CHECKLIST LIVRAISON**

- [ ] **Backend:** API vérification abonnements Genesis
- [ ] **Backend:** API Gateway proxy Genesis AI
- [ ] **Frontend:** Carte Genesis AI dashboard
- [ ] **Frontend:** Pages coaching intégrées
- [ ] **Frontend:** Composants wizard business brief
- [ ] **Config:** Variables environnement
- [ ] **Tests:** Tests E2E complets
- [ ] **Docs:** Documentation API endpoints
- [ ] **Démo:** Workflow complet fonctionnel

---

## 🔧 **ENVIRONNEMENT & DÉPENDANCES**

### **Backend Django**
```bash
# Nouvelles dépendances si nécessaires
pip install httpx  # Pour appels API Genesis
```

### **Frontend React**
```json
// Nouvelles dépendances dans package.json
{
  "@mui/icons-material": "^5.0.0",
  "axios": "^1.0.0"
}
```

### **Variables Environnement**
```env
# Backend .env
GENESIS_AI_API_URL=http://localhost:8001
GENESIS_AI_SERVICE_SECRET=your-genesis-service-secret

# Frontend .env  
REACT_APP_API_BASE_URL=http://localhost:8000
```

---

**Temps Estimé Total:** 13 heures  
**Priorité:** Haute  
**Délai Recommandé:** 3 jours

**Contact Chef de Projet:** Cascade  
**Questions/Blocages:** Rapporter immédiatement via chat

---

## 📞 **SUPPORT TECHNIQUE**

En cas de blocage, contacter Cascade avec:
1. **Description problème** exact
2. **Code concerné** (snippet)
3. **Messages d'erreur** complets
4. **Étapes de reproduction**

Bonne implémentation ! 🚀
