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
