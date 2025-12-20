import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, HelpCircle } from 'lucide-react';

interface UserInputProps {
    onSubmit: (text: string) => void;
    onReformulate: (text: string) => void;
    onHelp: () => void;
    onDontKnow: () => void;
    isLoading: boolean;
    reformulatedPreview?: string;
}

export default function UserInput({ 
    onSubmit, 
    onReformulate, 
    onHelp, 
    onDontKnow, 
    isLoading,
    reformulatedPreview 
}: UserInputProps) {
    const [text, setText] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [text]);

    const handleSubmit = () => {
        if (!text.trim() || isLoading) return;
        onSubmit(text);
        setText('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newText = e.target.value;
        setText(newText);
        onReformulate(newText);
    };

    return (
        <div className="space-y-4 max-w-3xl mx-auto w-full">
            {/* Reformulation Preview */}
            {reformulatedPreview && text.length > 30 && (
                <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-3 text-sm animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center gap-2 text-purple-300 mb-1 font-semibold">
                        <Sparkles className="w-4 h-4" />
                        <span>Suggestion de reformulation :</span>
                    </div>
                    <p className="text-gray-300 italic pl-6">{reformulatedPreview}</p>
                </div>
            )}

            <div className="relative bg-gray-800 border border-gray-700 rounded-2xl shadow-lg focus-within:ring-2 focus-within:ring-purple-500/50 focus-within:border-purple-500 transition-all">
                <textarea
                    data-testid="chat-input"
                    ref={textareaRef}
                    value={text}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Tapez votre réponse ici..."
                    className="w-full bg-transparent text-white placeholder-gray-500 p-4 min-h-[80px] max-h-[200px] resize-none focus:outline-none rounded-2xl"
                    disabled={isLoading}
                />
                
                <div className="flex justify-between items-center p-2 bg-gray-800/50 rounded-b-2xl border-t border-gray-700">
                    <div className="flex gap-2">
                        <button
                            data-testid="help-btn"
                            onClick={onHelp}
                            disabled={isLoading}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-300 bg-blue-900/30 hover:bg-blue-900/50 rounded-lg transition-colors"
                            title="Obtenir de l'aide pour répondre"
                        >
                            <HelpCircle className="w-3.5 h-3.5" />
                            Aide-moi
                        </button>
                        
                        <button
                            data-testid="dont-know-btn"
                            onClick={onDontKnow}
                            disabled={isLoading}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-400 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors"
                            title="Je ne sais pas quoi répondre"
                        >
                            <span>🤷‍♂️</span>
                            Je ne sais pas
                        </button>
                    </div>

                    <button
                        data-testid="send-btn"
                        onClick={handleSubmit}
                        disabled={!text.trim() || isLoading}
                        className={`
                            flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all
                            ${text.trim() && !isLoading 
                                ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg hover:shadow-purple-500/25 transform hover:-translate-y-0.5' 
                                : 'bg-gray-700 text-gray-500 cursor-not-allowed'}
                        `}
                    >
                        <span>Envoyer</span>
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
