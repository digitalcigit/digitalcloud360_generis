import { Proposal } from '@/types/coaching';
import { X, Check } from 'lucide-react';

interface ProposalsModalProps {
    isOpen: boolean;
    onClose: () => void;
    proposals: Proposal[];
    coachAdvice: string;
    onSelect: (proposal: Proposal) => void;
}

export default function ProposalsModal({ isOpen, onClose, proposals, coachAdvice, onSelect }: ProposalsModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-3xl shadow-2xl flex flex-col max-h-[90vh]" data-testid="proposals-modal">
                
                {/* Header */}
                <div className="p-6 border-b border-gray-800 flex justify-between items-center bg-gray-800/50">
                    <div>
                        <h3 className="text-xl font-bold text-white">🤷‍♂️ Pas d'inquiétude !</h3>
                        <p className="text-sm text-gray-400 mt-1">Voici 3 propositions adaptées à votre contexte.</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg" data-testid="close-proposals-btn">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar">
                    {/* Coach Advice */}
                    <div className="bg-blue-900/20 border border-blue-800/50 rounded-xl p-4 mb-6 flex gap-4 items-start">
                        <span className="text-2xl">💡</span>
                        <div>
                            <p className="text-blue-200 font-medium mb-1">Conseil du Coach</p>
                            <p className="text-sm text-blue-300/90 leading-relaxed" data-testid="coach-advice">{coachAdvice}</p>
                        </div>
                    </div>

                    {/* Proposals Grid */}
                    <div className="grid gap-4 md:grid-cols-1">
                        {proposals.map((proposal, index) => (
                            <div 
                                key={proposal.id}
                                data-testid={`proposal-card-${proposal.id}`}
                                onClick={() => onSelect(proposal)}
                                className="group relative bg-gray-800 hover:bg-gray-800/80 border border-gray-700 hover:border-purple-500 rounded-xl p-5 cursor-pointer transition-all duration-200 hover:shadow-lg hover:shadow-purple-900/20"
                            >
                                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
                                        Choisir <Check className="w-3 h-3" />
                                    </span>
                                </div>

                                <div className="flex gap-4">
                                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-xl font-bold text-gray-400 group-hover:bg-purple-900/50 group-hover:text-purple-300 transition-colors">
                                        {['A', 'B', 'C'][index]}
                                    </div>
                                    <div>
                                        <h4 className="text-lg font-semibold text-white mb-2 group-hover:text-purple-300 transition-colors">
                                            {proposal.title}
                                        </h4>
                                        <p className="text-gray-300 text-sm leading-relaxed mb-3">
                                            {proposal.content}
                                        </p>
                                        <div className="text-xs text-purple-400/80 italic border-l-2 border-purple-500/30 pl-3">
                                            Pourquoi : {proposal.justification}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 bg-gray-800/50 border-t border-gray-800 text-center">
                    <button onClick={onClose} className="text-sm text-gray-500 hover:text-gray-300 underline" data-testid="cancel-proposals-btn">
                        Je préfère rédiger moi-même
                    </button>
                </div>

            </div>
        </div>
    );
}
