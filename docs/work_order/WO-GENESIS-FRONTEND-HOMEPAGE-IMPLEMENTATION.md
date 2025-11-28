---
title: "WO-GENESIS-FRONTEND-HOMEPAGE-IMPLEMENTATION"
tags: ["genesis", "frontend", "nextjs", "homepage", "sso", "work-order"]
status: "ready"
date: "2025-11-28"
priority: "critique"
assignee: "Dev Senior Genesis"
---

# 🚨 WORK ORDER - Implémentation Homepage Frontend Genesis

**WO ID:** WO-GENESIS-FRONTEND-HOMEPAGE-IMPLEMENTATION  
**Phase:** Phase 1B - Frontend Autonome  
**Priorité:** 🔴 CRITIQUE (Bloquant pour tests E2E)  
**Assigné à:** Dev Senior Genesis  
**Date Création:** 28 novembre 2025  
**Estimation:** 4-6 heures  
**Status:** 🟡 PRÊT À DÉMARRER

---

## 🎯 OBJECTIF

Remplacer la page par défaut Next.js par une **vraie page d'accueil Genesis** permettant aux utilisateurs de :
1. S'authentifier automatiquement via SSO (token DC360)
2. Accéder à l'interface de chat IA pour générer leur Business Brief
3. Visualiser leur site généré

---

## 📌 CONTEXTE

### Situation Actuelle

L'utilisateur clique sur "Lancer Genesis" depuis le Dashboard DC360 et arrive sur :

```
http://localhost:3002
```

**Problème :** La page affiche le template par défaut Next.js :
> "To get started, edit the page.tsx file."

### Attendu

Une interface Genesis fonctionnelle avec :
- Authentification SSO automatique
- Chat IA pour génération de Business Brief
- Affichage du site généré

### Captures de Référence

- **Capture 1** : Dashboard DC360 avec bouton "Lancer Genesis" ✅
- **Capture 2** : Page par défaut Next.js ❌ (à remplacer)

---

## 🛠 TÂCHES DÉTAILLÉES

### Tâche 1 – Authentification SSO (1h30)

**Objectif :** Récupérer et valider le token JWT de l'utilisateur DC360.

**Fichier à créer :** `src/lib/auth.ts`

```typescript
import { cookies } from 'next/headers';

const DC360_API_URL = process.env.DC360_API_URL || 'http://web:8000/api';

export interface User {
    id: number;
    email: string;
    first_name?: string;
    last_name?: string;
}

export async function getCurrentUser(): Promise<User | null> {
    // Option 1: Token dans les cookies (partagé si même domaine)
    const cookieStore = cookies();
    const token = cookieStore.get('my-app-auth')?.value 
                || cookieStore.get('access_token')?.value;
    
    if (!token) {
        return null;
    }
    
    try {
        // Valider le token auprès de DC360
        const response = await fetch(`${DC360_API_URL}/v1/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('SSO validation error:', error);
        return null;
    }
}

export async function validateToken(token: string): Promise<User | null> {
    try {
        const response = await fetch(`${DC360_API_URL}/v1/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) return null;
        return await response.json();
    } catch {
        return null;
    }
}
```

**Fichier à créer :** `src/context/AuthContext.tsx`

```typescript
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface User {
    id: number;
    email: string;
    first_name?: string;
    last_name?: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    isLoading: true,
    isAuthenticated: false
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    
    useEffect(() => {
        async function checkAuth() {
            try {
                const response = await fetch('/api/auth/me');
                if (response.ok) {
                    const userData = await response.json();
                    setUser(userData);
                }
            } catch (error) {
                console.error('Auth check failed:', error);
            } finally {
                setIsLoading(false);
            }
        }
        
        checkAuth();
    }, []);
    
    return (
        <AuthContext.Provider value={{ 
            user, 
            isLoading, 
            isAuthenticated: !!user 
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
```

**Livrable :** SSO fonctionnel avec DC360.

---

### Tâche 2 – Page d'Accueil (1h)

**Objectif :** Créer une landing page accueillante qui redirige vers le chat.

**Fichier à modifier :** `src/app/page.tsx`

```typescript
import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

export default async function HomePage() {
    const user = await getCurrentUser();
    
    // Si authentifié, rediriger vers le chat
    if (user) {
        redirect('/chat');
    }
    
    // Sinon, afficher la page de connexion/redirection
    return (
        <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
            <div className="container mx-auto px-4 py-16 flex flex-col items-center justify-center min-h-screen">
                {/* Logo */}
                <div className="mb-8">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        Genesis AI
                    </h1>
                    <p className="text-gray-400 text-center mt-2">
                        Votre Partenaire Digital Intelligent
                    </p>
                </div>
                
                {/* Message */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md text-center">
                    <h2 className="text-2xl font-semibold mb-4">
                        Bienvenue sur Genesis
                    </h2>
                    <p className="text-gray-300 mb-6">
                        Pour accéder à votre espace de création, veuillez vous connecter via DigitalCloud360.
                    </p>
                    <a 
                        href={process.env.NEXT_PUBLIC_DC360_URL || 'http://localhost:3000'}
                        className="inline-block bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                    >
                        Se connecter via DC360
                    </a>
                </div>
                
                {/* Features */}
                <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
                    <FeatureCard 
                        icon="💬" 
                        title="Chat IA" 
                        description="Décrivez votre business, Genesis crée votre site"
                    />
                    <FeatureCard 
                        icon="🎨" 
                        title="Design Automatique" 
                        description="Templates professionnels adaptés à votre secteur"
                    />
                    <FeatureCard 
                        icon="🚀" 
                        title="Publication Instantanée" 
                        description="Votre site en ligne en quelques minutes"
                    />
                </div>
            </div>
        </main>
    );
}

function FeatureCard({ icon, title, description }: { 
    icon: string; 
    title: string; 
    description: string 
}) {
    return (
        <div className="bg-white/5 backdrop-blur rounded-xl p-6 text-center">
            <div className="text-4xl mb-4">{icon}</div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">{description}</p>
        </div>
    );
}
```

**Livrable :** Page d'accueil avec redirection conditionnelle.

---

### Tâche 3 – Interface Chat IA (2h)

**Objectif :** Créer l'interface de chat pour la génération de Business Brief.

**Fichier à créer :** `src/app/chat/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { redirect } from 'next/navigation';
import ChatInterface from '@/components/ChatInterface';
import SitePreview from '@/components/SitePreview';

export default function ChatPage() {
    const { user, isLoading, isAuthenticated } = useAuth();
    const [briefGenerated, setBriefGenerated] = useState(false);
    const [siteData, setSiteData] = useState(null);
    
    if (isLoading) {
        return <LoadingSpinner />;
    }
    
    if (!isAuthenticated) {
        redirect('/');
    }
    
    return (
        <main className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
                <div className="flex items-center justify-between max-w-7xl mx-auto">
                    <h1 className="text-xl font-bold text-purple-400">Genesis AI</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-gray-400">{user?.email}</span>
                        <a 
                            href={process.env.NEXT_PUBLIC_DC360_URL || 'http://localhost:3000'}
                            className="text-sm text-gray-500 hover:text-white"
                        >
                            Retour au Hub
                        </a>
                    </div>
                </div>
            </header>
            
            {/* Main Content */}
            <div className="flex h-[calc(100vh-73px)]">
                {/* Chat Panel */}
                <div className="w-1/2 border-r border-gray-700">
                    <ChatInterface 
                        userId={user?.id}
                        onBriefGenerated={(data) => {
                            setBriefGenerated(true);
                            setSiteData(data);
                        }}
                    />
                </div>
                
                {/* Preview Panel */}
                <div className="w-1/2 bg-gray-950">
                    {briefGenerated && siteData ? (
                        <SitePreview data={siteData} />
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            <div className="text-center">
                                <div className="text-6xl mb-4">🎨</div>
                                <p>Votre site apparaîtra ici</p>
                                <p className="text-sm mt-2">Commencez par décrire votre business dans le chat</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}

function LoadingSpinner() {
    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
    );
}
```

**Fichier à créer :** `src/components/ChatInterface.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatInterfaceProps {
    userId?: number;
    onBriefGenerated: (data: any) => void;
}

export default function ChatInterface({ userId, onBriefGenerated }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Bonjour ! Je suis Genesis, votre assistant pour créer votre site web. 🚀\n\nParlez-moi de votre business : quel est le nom de votre entreprise et que faites-vous ?",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
        
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        };
        
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    userId,
                    history: messages
                })
            });
            
            const data = await response.json();
            
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date()
            };
            
            setMessages(prev => [...prev, assistantMessage]);
            
            // Si un brief a été généré
            if (data.briefGenerated && data.siteData) {
                onBriefGenerated(data.siteData);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Désolé, une erreur s'est produite. Veuillez réessayer.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="flex flex-col h-full">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div 
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                            msg.role === 'user' 
                                ? 'bg-purple-600 text-white' 
                                : 'bg-gray-700 text-gray-100'
                        }`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 rounded-2xl px-4 py-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <div className="border-t border-gray-700 p-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Décrivez votre business..."
                        className="flex-1 bg-gray-700 border border-gray-600 rounded-full px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-full px-6 py-3 font-semibold transition-colors"
                    >
                        Envoyer
                    </button>
                </div>
            </div>
        </div>
    );
}
```

**Livrable :** Interface de chat fonctionnelle.

---

### Tâche 4 – API Route pour le Chat (1h)

**Objectif :** Créer l'endpoint API qui communique avec Genesis Backend.

**Fichier à créer :** `src/app/api/chat/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';

const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { message, userId, history } = body;
        
        // Appeler le backend Genesis
        const response = await fetch(`${GENESIS_API_URL}/api/v1/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                message,
                conversation_history: history
            })
        });
        
        if (!response.ok) {
            throw new Error(`Genesis API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        return NextResponse.json({
            response: data.response || data.message,
            briefGenerated: data.brief_generated || false,
            siteData: data.site_data || null
        });
        
    } catch (error) {
        console.error('Chat API error:', error);
        return NextResponse.json(
            { error: 'Internal server error', response: "Désolé, une erreur s'est produite." },
            { status: 500 }
        );
    }
}
```

**Fichier à créer :** `src/app/api/auth/me/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const DC360_API_URL = process.env.DC360_API_URL || 'http://web:8000/api';

export async function GET(request: NextRequest) {
    const cookieStore = cookies();
    const token = cookieStore.get('my-app-auth')?.value 
                || cookieStore.get('access_token')?.value;
    
    if (!token) {
        return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }
    
    try {
        const response = await fetch(`${DC360_API_URL}/v1/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
        }
        
        const user = await response.json();
        return NextResponse.json(user);
        
    } catch (error) {
        console.error('Auth validation error:', error);
        return NextResponse.json({ error: 'Auth service unavailable' }, { status: 503 });
    }
}
```

**Livrable :** API routes fonctionnelles.

---

### Tâche 5 – Configuration Environnement (15 min)

**Fichier à créer/modifier :** `.env.local`

```env
# DC360 Hub
DC360_API_URL=http://web:8000/api
NEXT_PUBLIC_DC360_URL=http://localhost:3000

# Genesis Backend
GENESIS_API_URL=http://genesis-api:8000
```

**Livrable :** Variables d'environnement configurées.

---

### Tâche 6 – Layout et Providers (30 min)

**Fichier à modifier :** `src/app/layout.tsx`

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Genesis AI - Votre Partenaire Digital Intelligent',
    description: 'Créez votre site web professionnel en quelques minutes grâce à l\'IA',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="fr">
            <body className={inter.className}>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
```

**Livrable :** Layout avec providers configurés.

---

## ✅ DEFINITION OF DONE (DoD)

- [ ] Page d'accueil Genesis remplace le template Next.js par défaut
- [ ] SSO fonctionnel (utilisateur DC360 reconnu automatiquement)
- [ ] Interface de chat affichée pour les utilisateurs authentifiés
- [ ] Communication avec Genesis Backend opérationnelle
- [ ] Redirection vers DC360 si non authentifié
- [ ] Tests E2E manuels validés

---

## 📁 FICHIERS À CRÉER/MODIFIER

| Fichier | Action | Priorité |
|---------|--------|----------|
| `src/app/page.tsx` | Modifier | 🔴 Critique |
| `src/app/chat/page.tsx` | Créer | 🔴 Critique |
| `src/app/layout.tsx` | Modifier | 🔴 Critique |
| `src/lib/auth.ts` | Créer | 🔴 Critique |
| `src/context/AuthContext.tsx` | Créer | 🔴 Critique |
| `src/components/ChatInterface.tsx` | Créer | 🟡 Haute |
| `src/app/api/chat/route.ts` | Créer | 🟡 Haute |
| `src/app/api/auth/me/route.ts` | Créer | 🟡 Haute |
| `.env.local` | Créer | 🟡 Haute |

---

## 📅 TIMELINE

| Phase | Durée | Tâches |
|-------|-------|--------|
| 1 | 1h30 | Authentification SSO |
| 2 | 1h | Page d'accueil |
| 3 | 2h | Interface Chat |
| 4 | 1h | API Routes |
| 5 | 15 min | Configuration |
| 6 | 30 min | Layout & Providers |
| **Total** | **~6h** | |

---

## 🔗 RÉFÉRENCES

| Document | Chemin |
|----------|--------|
| Architecture Hub & Satellites | `docs/memo/MEMO_CLARIFICATION_VISION_ECOSYSTEME_DC360_GENESIS_27_11_2025.md` |
| Configuration Docker E2E | `docs/memo/MEMO_REPONSE_CONFIG_RESEAU_E2E_27_11_2025.md` |
| Vision Genesis AI Partner | `docs/memo/MEMO_RESPONSE_GENESIS_AI_PARTNER_VISION_27_11_2025.md` |

---

## 📞 SUPPORT

En cas de blocage :
- **Ecosystem Scrum Master** : Cascade
- **DC360 API** : `http://web:8000/api` (interne Docker)
- **Genesis API** : `http://genesis-api:8000` (interne Docker)

---

## ⚠️ POINTS D'ATTENTION

1. **Cookies Cross-Domain** : Si DC360 et Genesis sont sur des domaines différents, le cookie JWT ne sera pas partagé. Prévoir un mécanisme de passage de token via URL ou localStorage.

2. **CORS** : S'assurer que le backend Genesis accepte les requêtes du frontend (`http://localhost:3002`).

3. **Réseau Docker** : Les appels internes doivent utiliser les noms de service Docker (`web`, `genesis-api`), pas `localhost`.

---

**Démarrage recommandé : Immédiat**  
**Bloquant pour : Tests E2E complets Genesis Phase 1B**
