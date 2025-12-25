import { NextRequest, NextResponse } from 'next/server';

// GENESIS_API_URL = http://genesis-api:8000 (sans /api/v1)
const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const token = request.headers.get('Authorization')?.replace('Bearer ', '');

        if (!token) {
            return NextResponse.json(
                { error: 'Missing authorization token' },
                { status: 401 }
            );
        }

        const backendUrl = `${GENESIS_API_URL}/api/v1/coaching/onboarding`;
        console.log('Calling backend:', backendUrl);

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return NextResponse.json(
                errorData || { error: `Backend error: ${response.status}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data, { status: 200 });
    } catch (error) {
        console.error('Onboarding API error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
