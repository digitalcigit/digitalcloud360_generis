import { ClickableChoice } from '@/types/coaching';

interface ClickableChoicesProps {
    choices: ClickableChoice[];
    onSelect: (choice: ClickableChoice) => void;
    isLoading?: boolean;
}

export default function ClickableChoices({ choices, onSelect, isLoading = false }: ClickableChoicesProps) {
    if (!choices || choices.length === 0) return null;
    
    return (
        <div className="mt-4 animate-in fade-in slide-in-from-bottom-2 delay-300 w-full max-w-3xl ml-auto">
            <p className="text-sm text-gray-400 mb-3 flex items-center gap-2">
                <span>🎯</span> Ou choisissez une piste rapide :
            </p>
            <div className="flex flex-wrap gap-3">
                {choices.map((choice) => (
                    <button
                        key={choice.id}
                        data-testid={`clickable-choice-${choice.id}`}
                        onClick={() => onSelect(choice)}
                        disabled={isLoading}
                        className="group flex flex-col items-start text-left px-4 py-3 bg-gray-800/80 hover:bg-purple-900/40 
                                   border border-gray-700 hover:border-purple-500/50 rounded-xl transition-all duration-200
                                   hover:shadow-[0_0_15px_rgba(168,85,247,0.15)] disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <span className="font-medium text-gray-200 group-hover:text-purple-300 transition-colors">
                            {choice.text}
                        </span>
                        {choice.description && (
                            <span className="text-xs text-gray-500 mt-1 group-hover:text-gray-400">
                                {choice.description}
                            </span>
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
}
