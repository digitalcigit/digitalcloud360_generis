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

        const conversation_history = Array.isArray(history)
            ? history
                  .filter((m) => m && typeof m === 'object')
                  .map((m) => ({
                      role: (m as { role?: unknown }).role,
                      content: (m as { content?: unknown }).content,
                  }))
                  .filter(
                      (m): m is { role: 'user' | 'assistant' | 'system'; content: string } =>
                          (m.role === 'user' || m.role === 'assistant' || m.role === 'system') &&
                          typeof m.content === 'string' &&
                          m.content.trim().length > 0
                  )
            : [];
        
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
                conversation_history
            })
        });
        
        if (!response.ok) {
            throw new Error(`Genesis API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        return NextResponse.json({
            response: data.response || data.message,
            briefGenerated: data.brief_generated || false,
            briefId: data.brief_id || null,
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
