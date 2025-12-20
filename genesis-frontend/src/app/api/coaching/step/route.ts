import { NextRequest, NextResponse } from 'next/server';

const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function POST(request: NextRequest) {
    const authHeader = request.headers.get('authorization');
    if (!authHeader) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const body = await request.json();
        const response = await fetch(`${GENESIS_API_URL}/api/v1/coaching/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': authHeader },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
             const errorData = await response.json().catch(() => ({}));
             return NextResponse.json(errorData, { status: response.status });
        }
        return NextResponse.json(await response.json());
    } catch (error) {
        console.error('Coaching Step API error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
