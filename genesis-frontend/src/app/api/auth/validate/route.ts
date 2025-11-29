import { NextRequest, NextResponse } from 'next/server';
import { validateToken } from '@/lib/auth';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { token } = body;

        if (!token) {
            return NextResponse.json({ error: 'Token required' }, { status: 400 });
        }

        const user = await validateToken(token);

        if (!user) {
            return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
        }

        return NextResponse.json(user);

    } catch (error) {
        console.error('Token validation error:', error);
        return NextResponse.json(
            { error: 'Validation failed' },
            { status: 500 }
        );
    }
}
