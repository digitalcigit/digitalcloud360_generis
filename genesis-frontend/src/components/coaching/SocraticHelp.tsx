import { useState } from 'react';
import { SocraticQuestion } from '@/types/coaching';
import { X, ChevronRight, MessageCircle } from 'lucide-react';

interface SocraticHelpProps {
    isOpen: boolean;
    onClose: () => void;
    questions: SocraticQuestion[];
    onAnswerComplete: (generatedText: string) => void;
    suggestion?: string;
}

export default function SocraticHelp({ isOpen, onClose, questions, onAnswerComplete, suggestion }: SocraticHelpProps) {
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
    const [answers, setAnswers] = useState<string[]>([]);
    
    if (!isOpen) return null;

    if (!questions || questions.length === 0) {
         return (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
                <div className="bg-gray-800 rounded-2xl p-6 max-w-md w-full border border-gray-700 shadow-2xl">
                    <h3 className="text-xl font-bold mb-4 text-white">💡 Aide du Coach</h3>
                    <p className="text-gray-300 mb-6">{suggestion || "Désolé, je n'ai pas de questions spécifiques pour le moment. Essayez de reformuler votre idée simplement."}</p>
                    <button onClick={onClose} className="w-full py-3 bg-gray-700 hover:bg-gray-600 rounded-xl text-white font-medium transition-colors">
                        Fermer
                    </button>
                </div>
            </div>
         );
    }

    const currentQ = questions[currentQuestionIdx];

    const handleAnswer = (answerText: string) => {
        const newAnswers = [...answers, answerText];
        setAnswers(newAnswers);
        
        if (currentQuestionIdx < questions.length - 1) {
            setCurrentQuestionIdx(currentQuestionIdx + 1);
        } else {
            // Generate a combined text from answers
            // This is a simple concatenation, in a real scenario we might want a smarter combination
            // or send it back to LLM, but for now we join them.
            // The prompt usually ensures questions build a narrative.
            const generatedText = newAnswers.join(" "); 
            onAnswerComplete(generatedText);
            onClose();
            // Reset for next time
            setAnswers([]);
            setCurrentQuestionIdx(0);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]" data-testid="socratic-help-modal">
                {/* Header */}
                <div className="p-6 border-b border-gray-800 flex justify-between items-center bg-gray-800/50">
                    <div>
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <MessageCircle className="w-5 h-5 text-purple-400" />
                            Aide à la réflexion
                        </h3>
                        <p className="text-xs text-purple-300 mt-1">Question {currentQuestionIdx + 1} sur {questions.length}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg" data-testid="close-help-btn">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto">
                    <div className="mb-8">
                        <h4 className="text-lg font-medium text-gray-100 mb-2 leading-relaxed" data-testid="socratic-question-text">
                            {currentQ.question}
                        </h4>
                        {currentQ.context_hint && (
                            <div className="bg-blue-900/20 border border-blue-800/50 rounded-lg p-3 inline-block">
                                <p className="text-sm text-blue-300">
                                    💡 {currentQ.context_hint}
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="space-y-3">
                        {currentQ.choices?.map((choice) => (
                            <button
                                key={choice.id}
                                data-testid={`socratic-choice-${choice.id}`}
                                onClick={() => handleAnswer(choice.text)}
                                className="w-full text-left p-4 bg-gray-800 hover:bg-purple-900/30 border border-gray-700 hover:border-purple-500/50 rounded-xl transition-all duration-200 group flex items-center justify-between"
                            >
                                <span className="text-gray-300 group-hover:text-white">{choice.text}</span>
                                <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-purple-400 opacity-0 group-hover:opacity-100 transition-all" />
                            </button>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 bg-gray-800/50 border-t border-gray-800 text-center">
                    <button onClick={onClose} className="text-sm text-gray-500 hover:text-gray-300 underline" data-testid="skip-help-btn">
                        Passer et annuler
                    </button>
                </div>
            </div>
        </div>
    );
}
