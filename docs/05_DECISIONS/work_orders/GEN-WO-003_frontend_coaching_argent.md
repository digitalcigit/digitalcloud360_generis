---
title: "Work Order GEN-WO-003: Frontend Coaching Maïeutique - Niveau Argent"
type: work_order
priority: P0 - CRITIQUE
status: approved
created: 2025-12-20
updated: 2025-12-20
depends_on: GEN-WO-002
tech_lead: Cascade (Tech Lead Genesis)
assignee: Senior Dev IA
estimated_effort: 3-4 jours
tags: ["frontend", "react", "nextjs", "coaching", "niveau-argent", "ux"]
---

# 🎯 WORK ORDER GEN-WO-003
## Frontend Coaching Maïeutique - Niveau Argent

**Ce Work Order complète GEN-WO-002** en implémentant l'interface utilisateur pour le coaching maïeutique.

> **CONTEXTE**: Le backend GEN-WO-002 est mergé sur master (PR #19). 
> Les endpoints sont prêts mais **aucun frontend** ne les consomme actuellement.
> Sans cette UI, le produit "Niveau Argent" n'est pas utilisable par l'entrepreneur.

---

## 1. CONTEXTE & JUSTIFICATION

### 1.1 Pourquoi ce WO est critique

| Situation actuelle | Impact |
|-------------------|--------|
| Backend `/api/v1/coaching/*` prêt | ✅ Fonctionnel |
| Frontend `/coaching` | ❌ **INEXISTANT** |
| Utilisateur peut tester le flow | ❌ **IMPOSSIBLE** |
| PO peut valider l'UX | ❌ **IMPOSSIBLE** |

### 1.2 Endpoints Backend Disponibles (GEN-WO-002)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/coaching/start` | POST | Démarre/reprend une session |
| `/api/v1/coaching/step` | POST | Soumet une réponse à une étape |
| `/api/v1/coaching/help` | POST | Questions socratiques (Aide-moi) |
| `/api/v1/coaching/reformulate` | POST | Reformulation temps réel |
| `/api/v1/coaching/generate-proposals` | POST | Mode "Je ne sais pas" |

---

## 2. OBJECTIF & CRITÈRES DE SUCCÈS

### 2.1 Objectif Principal

Implémenter une **interface utilisateur complète** pour le coaching maïeutique Niveau Argent, permettant à l'entrepreneur d'interagir avec le Coach IA de manière fluide et intuitive.

### 2.2 Definition of Done

- [ ] Page `/coaching` accessible après authentification
- [ ] Affichage du message coach avec exemples sectoriels
- [ ] Zone de saisie texte avec envoi
- [ ] **Bouton "Aide-moi à formuler"** → Affiche questions socratiques
- [ ] **Choix cliquables** → Pistes thématiques cliquables
- [ ] **Reformulation temps réel** → Affichage pendant la frappe (debounce 500ms)
- [ ] **Bouton "Je ne sais pas"** → Affiche 3 propositions à choisir/modifier
- [ ] Barre de progression des 5 étapes
- [ ] Affichage du site généré après étape OFFRE
- [ ] Design responsive (mobile-first)
- [ ] Tests E2E avec Chrome DevTools MCP

---

## 3. ARCHITECTURE CIBLE

### 3.1 Structure des Fichiers

```
genesis-frontend/src/
├── app/
│   ├── coaching/
│   │   └── page.tsx              # Page principale coaching
│   └── api/
│       └── coaching/
│           ├── start/route.ts    # Proxy vers backend
│           ├── step/route.ts
│           ├── help/route.ts
│           ├── reformulate/route.ts
│           └── generate-proposals/route.ts
├── components/
│   └── coaching/
│       ├── CoachingInterface.tsx # Composant principal
│       ├── CoachMessage.tsx      # Bulle message coach
│       ├── UserInput.tsx         # Zone saisie + boutons
│       ├── ProgressBar.tsx       # Progression 5 étapes
│       ├── ClickableChoices.tsx  # Pistes cliquables
│       ├── SocraticHelp.tsx      # Modal questions socratiques
│       ├── ProposalsModal.tsx    # Modal "Je ne sais pas"
│       └── ReformulationPreview.tsx # Preview reformulation
├── types/
│   └── coaching.ts               # Types TypeScript
└── utils/
    └── coaching-api.ts           # Client API coaching
```

### 3.2 Flow Utilisateur

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAGE /coaching                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ [●] Vision  [○] Mission  [○] Clientèle  [○] Diff.  [○] Offre│ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 🤖 Coach IA:                                                │ │
│  │ "Parlons de votre VISION. Dans 5 ans, si votre business    │ │
│  │  est un succès total, à quoi ressemble-t-il?"              │ │
│  │                                                             │ │
│  │ 💡 Exemples pour vous inspirer:                            │ │
│  │ • "Devenir LA référence du Thieboudienne à Dakar"          │ │
│  │ • "Ouvrir 3 restaurants dans la sous-région"               │ │
│  │                                                             │ │
│  │ 🎯 Ou choisissez une piste:                                │ │
│  │ ┌─────────────────────┐ ┌─────────────────────┐            │ │
│  │ │ Devenir référence   │ │ Transformer secteur │            │ │
│  │ │      locale         │ │                     │            │ │
│  │ └─────────────────────┘ └─────────────────────┘            │ │
│  │ ┌─────────────────────┐                                    │ │
│  │ │ Créer emplois       │                                    │ │
│  │ │   communauté        │                                    │ │
│  │ └─────────────────────┘                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Votre réponse:                                             │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ je veux faire le meilleur thieb de dakar              │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ ✨ Reformulation suggérée:                                 │ │
│  │ "Devenir LA référence du Thieboudienne authentique à      │ │
│  │  Dakar, reconnu pour la qualité et la générosité..."      │ │
│  │                                                             │ │
│  │ [💡 Aide-moi]  [❓ Je ne sais pas]  [Valider ✓]           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. TÂCHES DÉTAILLÉES

### TÂCHE 1: Types TypeScript & API Client (0.5 jour)

**Fichiers à créer**:
- `src/types/coaching.ts` - Types pour les réponses API
- `src/utils/coaching-api.ts` - Client API avec gestion erreurs

**Types requis**:
```typescript
export enum CoachingStepEnum {
    VISION = "vision",
    MISSION = "mission",
    CLIENTELE = "clientele",
    DIFFERENTIATION = "differentiation",
    OFFRE = "offre"
}

export interface CoachingResponse {
    session_id: string;
    current_step: CoachingStepEnum;
    coach_message: string;
    examples: string[];
    progress: Record<string, boolean>;
    confidence_score: number;
    is_step_complete: boolean;
    site_data?: SiteDefinition;
    clickable_choices: ClickableChoice[];
}

export interface ClickableChoice {
    id: string;
    text: string;
    description?: string;
}

export interface CoachingHelpResponse {
    session_id: string;
    current_step: CoachingStepEnum;
    socratic_questions: SocraticQuestion[];
    suggestion: string;
}

export interface GenerateProposalsResponse {
    session_id: string;
    step: CoachingStepEnum;
    proposals: Proposal[];
    coach_advice: string;
}

export interface ReformulateResponse {
    original_text: string;
    reformulated_text: string;
    is_better: boolean;
    suggestions: string[];
}
```

---

### TÂCHE 2: Routes API Next.js (Proxy) (0.5 jour)

**Fichiers à créer** dans `src/app/api/coaching/`:

```typescript
// start/route.ts
import { NextRequest, NextResponse } from 'next/server';

const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function POST(request: NextRequest) {
    const authHeader = request.headers.get('authorization');
    if (!authHeader) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const body = await request.json();
        const response = await fetch(`${GENESIS_API_URL}/api/v1/coaching/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': authHeader },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) throw new Error(`Backend error: ${response.status}`);
        return NextResponse.json(await response.json());
    } catch (error) {
        console.error('Coaching Start API error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
```

**Pattern identique pour**: `step/route.ts`, `help/route.ts`, `reformulate/route.ts`, `generate-proposals/route.ts`

---

### TÂCHE 3: Composants React (1.5 jours)

#### 3.1 CoachingInterface.tsx (Composant Principal)

```typescript
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/stores/useAuthStore';
import { coachingApi } from '@/utils/coaching-api';
import { CoachingResponse, CoachingStepEnum } from '@/types/coaching';
import ProgressBar from './ProgressBar';
import CoachMessage from './CoachMessage';
import UserInput from './UserInput';
import ClickableChoices from './ClickableChoices';
import SocraticHelp from './SocraticHelp';
import ProposalsModal from './ProposalsModal';

export default function CoachingInterface() {
    const token = useAuthStore((state) => state.token);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [coachingState, setCoachingState] = useState<CoachingResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showHelp, setShowHelp] = useState(false);
    const [showProposals, setShowProposals] = useState(false);
    const [reformulatedText, setReformulatedText] = useState('');

    // Démarrer session au montage
    useEffect(() => {
        if (token) startSession();
    }, [token]);

    const startSession = async () => {
        setIsLoading(true);
        try {
            const response = await coachingApi.start(token!);
            setSessionId(response.session_id);
            setCoachingState(response);
        } catch (error) {
            console.error('Failed to start session:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const submitResponse = async (userResponse: string) => {
        if (!sessionId) return;
        setIsLoading(true);
        try {
            const response = await coachingApi.step(token!, sessionId, userResponse);
            setCoachingState(response);
            setReformulatedText('');
        } catch (error) {
            console.error('Failed to submit response:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleReformulate = useCallback(
        debounce(async (text: string) => {
            if (!sessionId || text.length < 30) return;
            try {
                const response = await coachingApi.reformulate(token!, sessionId, text);
                if (response.is_better) {
                    setReformulatedText(response.reformulated_text);
                }
            } catch (error) {
                console.error('Reformulation failed:', error);
            }
        }, 500),
        [sessionId, token]
    );

    // ... render
}
```

#### 3.2 ProgressBar.tsx

```typescript
interface ProgressBarProps {
    progress: Record<string, boolean>;
    currentStep: CoachingStepEnum;
}

const STEPS = [
    { key: 'vision', label: 'Vision', icon: '👁️' },
    { key: 'mission', label: 'Mission', icon: '🎯' },
    { key: 'clientele', label: 'Clientèle', icon: '👥' },
    { key: 'differentiation', label: 'Différenciation', icon: '⭐' },
    { key: 'offre', label: 'Offre', icon: '💼' }
];

export default function ProgressBar({ progress, currentStep }: ProgressBarProps) {
    return (
        <div className="flex justify-between items-center mb-8 px-4">
            {STEPS.map((step, index) => (
                <div key={step.key} className="flex flex-col items-center">
                    <div className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-xl
                        ${progress[step.key] ? 'bg-green-500' : 
                          currentStep === step.key ? 'bg-purple-500 animate-pulse' : 'bg-gray-600'}
                    `}>
                        {step.icon}
                    </div>
                    <span className="text-xs mt-1 text-gray-400">{step.label}</span>
                </div>
            ))}
        </div>
    );
}
```

#### 3.3 ClickableChoices.tsx

```typescript
interface ClickableChoicesProps {
    choices: ClickableChoice[];
    onSelect: (choice: ClickableChoice) => void;
}

export default function ClickableChoices({ choices, onSelect }: ClickableChoicesProps) {
    if (!choices.length) return null;
    
    return (
        <div className="mt-4">
            <p className="text-sm text-gray-400 mb-2">🎯 Ou choisissez une piste:</p>
            <div className="flex flex-wrap gap-2">
                {choices.map((choice) => (
                    <button
                        key={choice.id}
                        onClick={() => onSelect(choice)}
                        className="px-4 py-2 bg-purple-900/50 hover:bg-purple-800 
                                   border border-purple-500 rounded-lg text-sm
                                   transition-colors duration-200"
                    >
                        {choice.text}
                    </button>
                ))}
            </div>
        </div>
    );
}
```

#### 3.4 SocraticHelp.tsx (Modal Questions Socratiques)

```typescript
interface SocraticHelpProps {
    isOpen: boolean;
    onClose: () => void;
    questions: SocraticQuestion[];
    onAnswerComplete: (generatedText: string) => void;
}

export default function SocraticHelp({ isOpen, onClose, questions, onAnswerComplete }: SocraticHelpProps) {
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState<string[]>([]);

    if (!isOpen) return null;

    const handleAnswer = (answer: string) => {
        const newAnswers = [...answers, answer];
        setAnswers(newAnswers);
        
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        } else {
            // Générer texte basé sur réponses
            const generatedText = generateFromAnswers(newAnswers);
            onAnswerComplete(generatedText);
            onClose();
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-xl p-6 max-w-lg w-full mx-4">
                <h3 className="text-xl font-bold mb-4">💡 Aide à la formulation</h3>
                
                <div className="mb-4">
                    <p className="text-gray-300">{questions[currentQuestion].question}</p>
                    {questions[currentQuestion].context_hint && (
                        <p className="text-sm text-gray-500 mt-1">
                            {questions[currentQuestion].context_hint}
                        </p>
                    )}
                </div>

                <div className="flex flex-wrap gap-2">
                    {questions[currentQuestion].choices.map((choice) => (
                        <button
                            key={choice.id}
                            onClick={() => handleAnswer(choice.text)}
                            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
                        >
                            {choice.text}
                        </button>
                    ))}
                </div>

                <div className="mt-4 flex justify-between items-center">
                    <span className="text-sm text-gray-500">
                        Question {currentQuestion + 1}/{questions.length}
                    </span>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        Annuler
                    </button>
                </div>
            </div>
        </div>
    );
}
```

#### 3.5 ProposalsModal.tsx (Mode "Je ne sais pas")

```typescript
interface ProposalsModalProps {
    isOpen: boolean;
    onClose: () => void;
    proposals: Proposal[];
    coachAdvice: string;
    onSelect: (proposal: Proposal) => void;
}

export default function ProposalsModal({ isOpen, onClose, proposals, coachAdvice, onSelect }: ProposalsModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                <h3 className="text-xl font-bold mb-2">❓ Pas d'inquiétude !</h3>
                <p className="text-gray-400 mb-4">{coachAdvice}</p>

                <div className="space-y-4">
                    {proposals.map((proposal, index) => (
                        <div 
                            key={proposal.id}
                            className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 cursor-pointer
                                       border-2 border-transparent hover:border-purple-500 transition-all"
                            onClick={() => onSelect(proposal)}
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-2xl">
                                    {['🅰️', '🅱️', '🅲'][index]}
                                </span>
                                <div>
                                    <h4 className="font-semibold text-white">{proposal.title}</h4>
                                    <p className="text-gray-300 mt-1">{proposal.content}</p>
                                    <p className="text-sm text-purple-400 mt-2">
                                        💡 {proposal.justification}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-6 flex justify-end">
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
}
```

---

### TÂCHE 4: Page /coaching (0.5 jour)

**Fichier**: `src/app/coaching/page.tsx`

```typescript
import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';
import CoachingInterface from '@/components/coaching/CoachingInterface';

export default async function CoachingPage() {
    const user = await getCurrentUser();
    
    if (!user) {
        redirect('/');
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
            <div className="container mx-auto px-4 py-8 max-w-4xl">
                <header className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        Coach Genesis AI
                    </h1>
                    <p className="text-gray-400 mt-2">
                        Construisons ensemble la vision de votre business
                    </p>
                </header>
                
                <CoachingInterface />
            </div>
        </main>
    );
}
```

---

### TÂCHE 5: Tests E2E (0.5 jour)

**Test avec Chrome DevTools MCP**:
1. Démarrer stack Docker
2. Se connecter via DC360
3. Naviguer vers `/coaching`
4. Parcourir les 5 étapes avec différents scénarios:
   - Réponse texte libre
   - Clic sur choix proposé
   - Utilisation "Aide-moi"
   - Utilisation "Je ne sais pas"
5. Vérifier génération du site final

---

## 5. FICHIERS À CRÉER

| Fichier | Type | Priorité |
|---------|------|----------|
| `src/types/coaching.ts` | Types | P0 |
| `src/utils/coaching-api.ts` | API Client | P0 |
| `src/app/api/coaching/start/route.ts` | API Route | P0 |
| `src/app/api/coaching/step/route.ts` | API Route | P0 |
| `src/app/api/coaching/help/route.ts` | API Route | P0 |
| `src/app/api/coaching/reformulate/route.ts` | API Route | P0 |
| `src/app/api/coaching/generate-proposals/route.ts` | API Route | P0 |
| `src/components/coaching/CoachingInterface.tsx` | Component | P0 |
| `src/components/coaching/ProgressBar.tsx` | Component | P0 |
| `src/components/coaching/CoachMessage.tsx` | Component | P0 |
| `src/components/coaching/UserInput.tsx` | Component | P0 |
| `src/components/coaching/ClickableChoices.tsx` | Component | P0 |
| `src/components/coaching/SocraticHelp.tsx` | Component | P1 |
| `src/components/coaching/ProposalsModal.tsx` | Component | P1 |
| `src/components/coaching/ReformulationPreview.tsx` | Component | P1 |
| `src/app/coaching/page.tsx` | Page | P0 |

---

## 6. DÉPENDANCES

- **Backend GEN-WO-002**: ✅ Mergé (PR #19)
- **Authentification DC360**: ✅ Existante
- **TailwindCSS**: ✅ Configuré
- **Zustand (AuthStore)**: ✅ Existant

---

## 7. TIMELINE

| Jour | Tâches |
|------|--------|
| J1 | Types + API Client + Routes Next.js |
| J2 | Composants principaux (CoachingInterface, ProgressBar, UserInput) |
| J3 | Composants Niveau Argent (SocraticHelp, ProposalsModal, Reformulation) |
| J4 | Page /coaching + Tests E2E + Corrections |

---

## 8. NOTES IMPORTANTES

### 8.1 Gestion du Token
Le token JWT doit être propagé à chaque appel API. Utiliser le store Zustand existant.

### 8.2 Debounce Reformulation
La reformulation temps réel doit utiliser un debounce de 500ms pour éviter de surcharger l'API.

### 8.3 Mobile First
Le design doit être responsive et fonctionner sur mobile (cible: entrepreneurs avec smartphone).

### 8.4 Gestion des Erreurs
Afficher des messages d'erreur clairs en cas d'échec API. Prévoir un retry automatique.

---

**ATTENDU**: PR avec toutes les modifications, tests passants, prêt pour test E2E via Chrome DevTools MCP.
