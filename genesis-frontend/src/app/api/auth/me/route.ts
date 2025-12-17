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
        return NextResponse.json({ error: 'Auth service unavailable' }, { status: 503 });
    }
}
