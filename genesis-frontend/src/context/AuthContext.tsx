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
                // 1. Check for token in URL (SSO redirect)
                const urlParams = new URLSearchParams(window.location.search);
                const urlToken = urlParams.get('token');
                
                if (urlToken) {
                    // 2. Validate token with backend
                    const validateResponse = await fetch('/api/auth/validate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ token: urlToken })
                    });
                    
                    if (validateResponse.ok) {
                        const userData = await validateResponse.json();
                        setUser(userData);
                        
                        // 3. Store token in cookie/localStorage
                        document.cookie = `access_token=${urlToken}; path=/; max-age=86400`;
                        
                        // 4. Clean URL (remove token from URL bar)
                        const newUrl = window.location.pathname + window.location.hash;
                        window.history.replaceState({}, '', newUrl);
                        
                        setIsLoading(false);
                        return;
                    }
                }
                
                // If no URL token, check existing session
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
