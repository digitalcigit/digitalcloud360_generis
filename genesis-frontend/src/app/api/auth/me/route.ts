import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const DC360_API_URL = process.env.DC360_API_URL || 'http://web:8000/api';

export async function GET(request: NextRequest) {
    void request;
    const cookieStore = await cookies();
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
        // Fallback: Si DC360 n'est pas accessible, valider via Genesis API
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
                return NextResponse.json(user);
            }
        } catch (genesisError) {
            console.error('Genesis API validation also failed:', genesisError);
        }
        return NextResponse.json({ error: 'Auth service unavailable' }, { status: 503 });
    }
}
