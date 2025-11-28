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
    const cookieStore = await cookies();
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
