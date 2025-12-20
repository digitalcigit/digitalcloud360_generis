import { SiteDefinition } from './site-definition';

export enum CoachingStepEnum {
    VISION = "vision",
    MISSION = "mission",
    CLIENTELE = "clientele",
    DIFFERENTIATION = "differentiation",
    OFFRE = "offre"
}

export interface ClickableChoice {
    id: string;
    text: string;
    description?: string;
}

export interface CoachingResponse {
    session_id: string;
    current_step: CoachingStepEnum;
    coach_message: string;
    examples: string[];
    progress: Record<string, boolean>;
    confidence_score?: number;
    is_step_complete: boolean;
    site_data?: SiteDefinition;
    clickable_choices: ClickableChoice[];
    next_questions?: string[];
}

export interface CoachingHelpResponse {
    session_id: string;
    current_step: CoachingStepEnum;
    socratic_questions: SocraticQuestion[];
    suggestion: string;
}

export interface SocraticQuestion {
    question: string;
    context_hint?: string;
    choices: Array<{ id: string; text: string }>;
}

export interface GenerateProposalsResponse {
    session_id: string;
    step: CoachingStepEnum;
    proposals: Proposal[];
    coach_advice: string;
}

export interface Proposal {
    id: string;
    title: string;
    content: string;
    justification: string;
}

export interface ReformulateResponse {
    original_text: string;
    reformulated_text: string;
    is_better: boolean;
    suggestions: string[];
}
