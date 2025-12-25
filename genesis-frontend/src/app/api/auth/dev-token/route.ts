import { NextRequest, NextResponse } from 'next/server';

const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function GET(request: NextRequest) {
    try {
        // Call backend to generate a dev token for user ID 1
        const response = await fetch(`${GENESIS_API_URL}/api/v1/auth/dev-token`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            console.error('Failed to get dev token from backend:', response.status);
            return NextResponse.json(
                { error: 'Failed to get dev token' },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data, { status: 200 });
    } catch (error) {
        console.error('Dev token API error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
