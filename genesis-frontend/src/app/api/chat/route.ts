import { NextRequest, NextResponse } from 'next/server';

const GENESIS_API_URL = process.env.GENESIS_API_URL || 'http://genesis-api:8000';

export async function POST(request: NextRequest) {
    // 1. Récupérer le token entrant (CRITICAL: Chain of Trust)
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
        const body = await request.json();
        const { message, history } = body;
        
        // Appeler le backend Genesis avec propagation du token
        const response = await fetch(`${GENESIS_API_URL}/api/v1/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader  // CRITICAL: Propagation du token (Règle "The Token is the Truth")
            },
            body: JSON.stringify({
                // user_id supprimé : Le backend décode l'identité depuis le JWT (Security Rule #1)
                message,
                conversation_history: history
            })
        });
        
        if (!response.ok) {
            throw new Error(`Genesis API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        return NextResponse.json({
            response: data.response || data.message,
            briefGenerated: data.brief_generated || false,
            siteData: data.site_data || null
        });
        
    } catch (error) {
        console.error('Chat API error:', error);
        return NextResponse.json(
            { error: 'Internal server error', response: "Désolé, une erreur s'est produite." },
            { status: 500 }
        );
    }
}
