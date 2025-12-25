import { cookies } from 'next/headers';

const DC360_API_URL = process.env.DC360_API_URL || 'http://web:8000/api';

export interface User {
    id: number;
    email: string;
    first_name?: string;
    last_name?: string;
}

export async function getCurrentUser(): Promise<User | null> {
    // Bypass for E2E testing (Runtime check)
    if (process.env.E2E_TEST_MODE === 'true') {
        console.log('🔒 Auth Bypass Active (E2E_TEST_MODE)');
        return {
            id: 999,
            email: 'e2e@test.com',
            first_name: 'E2E',
            last_name: 'Test'
        };
    }

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
        // Fallback: Si DC360 n'est pas accessible, valider le token localement via Genesis API
        console.log('🔄 Fallback: Validating token via Genesis API...');
        try {
            const genesisApiUrl = process.env.GENESIS_API_URL || 'http://genesis-api:8000';
            const genesisResponse = await fetch(`${genesisApiUrl}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (genesisResponse.ok) {
                const user = await genesisResponse.json();
                console.log('✅ Token validated via Genesis API');
                return user;
            }
        } catch (genesisError) {
            console.error('Genesis API validation also failed:', genesisError);
        }
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
