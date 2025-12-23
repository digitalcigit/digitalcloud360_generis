'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';
import { coachingApi } from '@/utils/coaching-api';
import { 
    CoachingResponse, 
    CoachingStepEnum, 
    ClickableChoice, 
    SocraticQuestion,
    Proposal
} from '@/types/coaching';
import { Loader2 } from 'lucide-react';

import ProgressBar from './ProgressBar';
import CoachMessage from './CoachMessage';
import UserInput from './UserInput';
import ClickableChoices from './ClickableChoices';
import SocraticHelp from './SocraticHelp';
import ProposalsModal from './ProposalsModal';

// Debounce utility
function debounce<T extends (...args: any[]) => any>(func: T, wait: number) {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

const SKIP_DEFAULTS: Record<CoachingStepEnum, string> = {
    [CoachingStepEnum.VISION]: 'Créer un business à impact positif pour ma communauté',
    [CoachingStepEnum.MISSION]: 'Offrir un service de qualité accessible à tous',
    [CoachingStepEnum.CLIENTELE]: 'Familles et professionnels de ma région',
    [CoachingStepEnum.DIFFERENTIATION]: 'Un accompagnement personnalisé et authentique',
    [CoachingStepEnum.OFFRE]: 'Des services adaptés aux besoins locaux',
};

export default function CoachingInterface() {
    const router = useRouter();
    const token = useAuthStore((state) => state.token);
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [coachingState, setCoachingState] = useState<CoachingResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    // Modals & Features state
    const [showHelp, setShowHelp] = useState(false);
    const [helpData, setHelpData] = useState<{questions: SocraticQuestion[], suggestion: string} | null>(null);
    const [isHelpLoading, setIsHelpLoading] = useState(false);

    const [showProposals, setShowProposals] = useState(false);
    const [proposalsData, setProposalsData] = useState<{proposals: Proposal[], coachAdvice: string} | null>(null);
    const [isProposalsLoading, setIsProposalsLoading] = useState(false);

    const [reformulatedText, setReformulatedText] = useState('');

    // Redirect if not authenticated
    useEffect(() => {
        if (!isAuthenticated()) {
            router.push('/login');
        }
    }, [isAuthenticated, router]);

    // Start session on mount
    useEffect(() => {
        if (token && !sessionId) {
            startSession();
        }
    }, [token, sessionId]);

    const startSession = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await coachingApi.start(token!);
            setSessionId(response.session_id);
            setCoachingState(response);
        } catch (err: any) {
            console.error('Failed to start session:', err);
            setError(err.message || 'Impossible de démarrer la session.');
        } finally {
            setIsLoading(false);
        }
    };

    const submitResponse = async (userResponse: string) => {
        if (!sessionId || !token) return;
        setIsLoading(true);
        setError(null);
        try {
            const response = await coachingApi.step(token, sessionId, userResponse);
            setCoachingState(response);
            setReformulatedText(''); // Clear previous reformulation
            
            // If session complete (site generated), handle it (e.g. redirect or show confetti)
            if (response.current_step === CoachingStepEnum.OFFRE && response.is_step_complete) {
                // For now, the UI will show the "Site Generated" state if we handle it in render
            }
        } catch (err: any) {
            console.error('Failed to submit response:', err);
            setError(err.message || 'Erreur lors de l\'envoi de la réponse.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleChoiceSelect = (choice: ClickableChoice) => {
        submitResponse(choice.text);
    };

    // --- SILVER FEATURES ---

    // 1. Reformulation (Debounced)
    const handleReformulate = useCallback(
        debounce(async (text: string) => {
            if (!sessionId || !token || text.length < 30) {
                setReformulatedText('');
                return;
            }
            try {
                // Use current step if available, else undefined (backend defaults to vision)
                const currentStep = coachingState?.current_step;
                const response = await coachingApi.reformulate(token, sessionId, text, currentStep);
                if (response.is_better) {
                    setReformulatedText(response.reformulated_text);
                } else {
                    setReformulatedText('');
                }
            } catch (err) {
                console.error('Reformulation failed:', err);
            }
        }, 500),
        [sessionId, token, coachingState?.current_step]
    );

    // 2. Socratic Help
    const handleHelp = async () => {
        if (!sessionId || !token) return;
        setIsHelpLoading(true);
        try {
            const response = await coachingApi.help(token, sessionId);
            setHelpData({
                questions: response.socratic_questions,
                suggestion: response.suggestion
            });
            setShowHelp(true);
        } catch (err: any) {
            console.error('Help failed:', err);
            setError(err.message || "Impossible d'obtenir de l'aide.");
        } finally {
            setIsHelpLoading(false);
        }
    };

    // 3. Generate Proposals ("I don't know")
    const handleDontKnow = async () => {
        if (!sessionId || !token || !coachingState) return;
        const defaultText = SKIP_DEFAULTS[coachingState.current_step] || "Je passe cette question";
        await submitResponse(defaultText);
    };

    const handleProposalSelect = (proposal: Proposal) => {
        submitResponse(proposal.content);
        setShowProposals(false);
    };

    const handleHelpAnswer = (generatedText: string) => {
        // Here we could either submit directly or put it in the input.
        // Let's submit directly for fluidity, or maybe put in input?
        // The user might want to edit. But UserInput doesn't expose setText easily from here.
        // For MVP/Silver, let's submit directly as it's "coached" text.
        submitResponse(generatedText);
    };


    // --- RENDER ---

    if (!token) return null; // Or loading spinner while checking auth

    if (!coachingState && isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh]">
                <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
                <p className="text-gray-400">Initialisation de votre Coach IA...</p>
            </div>
        );
    }

    if (error && !coachingState) {
        return (
            <div className="text-center p-8 bg-red-900/20 border border-red-800 rounded-2xl">
                <h3 className="text-red-400 font-bold mb-2">Une erreur est survenue</h3>
                <p className="text-gray-300 mb-4">{error}</p>
                <button 
                    onClick={startSession}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                    Réessayer
                </button>
            </div>
        );
    }

    if (!coachingState) return null;

    // Success State (Site Generated)
    if (coachingState.site_data) {
        // Extract sessionId from coachingState to ensure it's available
        const currentSessionId = sessionId || coachingState.session_id;
        
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8 animate-in fade-in zoom-in duration-500">
                <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(34,197,94,0.4)]">
                    <span className="text-4xl">🚀</span>
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Félicitations !</h2>
                    <p className="text-xl text-gray-300">Votre site web a été généré avec succès.</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 max-w-md w-full">
                    <p className="text-gray-400 mb-4">Votre business brief est complet.</p>
                    <button 
                        className="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold rounded-xl transition-all shadow-lg hover:scale-105"
                        onClick={() => {
                            console.log('Redirecting to preview with sessionId:', currentSessionId);
                            router.push(`/preview/${currentSessionId}`);
                        }}
                    >
                        Voir mon site
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto pb-20">
            <ProgressBar 
                progress={coachingState.progress} 
                currentStep={coachingState.current_step} 
            />

            <div className="mt-8 space-y-6">
                <CoachMessage 
                    message={coachingState.coach_message} 
                    examples={coachingState.examples} 
                />

                <ClickableChoices 
                    choices={coachingState.clickable_choices} 
                    onSelect={handleChoiceSelect}
                    isLoading={isLoading}
                />

                <div className="mt-8" data-testid="user-input-area">
                    <UserInput 
                        onSubmit={submitResponse}
                        onReformulate={handleReformulate}
                        onHelp={handleHelp}
                        onDontKnow={handleDontKnow}
                        isLoading={isLoading || isHelpLoading || isProposalsLoading}
                        reformulatedPreview={reformulatedText}
                    />
                </div>
            </div>

            {/* Modals */}
            <SocraticHelp 
                isOpen={showHelp}
                onClose={() => setShowHelp(false)}
                questions={helpData?.questions || []}
                suggestion={helpData?.suggestion}
                onAnswerComplete={handleHelpAnswer}
            />

            <ProposalsModal
                isOpen={showProposals}
                onClose={() => setShowProposals(false)}
                proposals={proposalsData?.proposals || []}
                coachAdvice={proposalsData?.coachAdvice || ''}
                onSelect={handleProposalSelect}
            />
        </div>
    );
}
