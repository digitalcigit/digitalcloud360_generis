import { 
    CoachingResponse, 
    CoachingHelpResponse, 
    ReformulateResponse, 
    GenerateProposalsResponse,
    CoachingStepEnum 
} from '@/types/coaching';

const API_BASE = '/api/coaching';

class CoachingApi {
    private async fetchWithAuth<T>(endpoint: string, token: string, options: RequestInit = {}): Promise<T> {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers,
        };

        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || errorData.detail || `API Error: ${response.status}`);
        }

        return response.json();
    }

    async onboarding(
        token: string,
        payload: {
            business_name?: string;
            sector: string;
            sector_other?: string;
            logo_source?: 'upload' | 'generate' | 'later';
            logo_url?: string | null;
        }
    ): Promise<{ session_id: string; onboarding: Record<string, any> }> {
        return this.fetchWithAuth('/onboarding', token, {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }

    async start(token: string, params?: { message?: string; session_id?: string }): Promise<CoachingResponse> {
        return this.fetchWithAuth<CoachingResponse>('/start', token, {
            method: 'POST',
            body: JSON.stringify(params ?? {}),
        });
    }

    async step(token: string, sessionId: string, userResponse: string): Promise<CoachingResponse> {
        return this.fetchWithAuth<CoachingResponse>('/step', token, {
            method: 'POST',
            body: JSON.stringify({ 
                session_id: sessionId, 
                user_response: userResponse 
            }),
        });
    }

    async help(token: string, sessionId: string): Promise<CoachingHelpResponse> {
        return this.fetchWithAuth<CoachingHelpResponse>('/help', token, {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId }),
        });
    }

    async reformulate(token: string, sessionId: string, text: string, targetStep?: CoachingStepEnum): Promise<ReformulateResponse> {
        return this.fetchWithAuth<ReformulateResponse>('/reformulate', token, {
            method: 'POST',
            body: JSON.stringify({ 
                session_id: sessionId, 
                text,
                target_step: targetStep 
            }),
        });
    }

    async generateProposals(token: string, sessionId: string): Promise<GenerateProposalsResponse> {
        return this.fetchWithAuth<GenerateProposalsResponse>('/generate-proposals', token, {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId }),
        });
    }
}

export const coachingApi = new CoachingApi();
