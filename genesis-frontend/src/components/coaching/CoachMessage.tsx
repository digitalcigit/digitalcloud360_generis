interface CoachMessageProps {
    message: string;
    examples?: string[];
}

export default function CoachMessage({ message, examples = [] }: CoachMessageProps) {
    return (
        <div className="flex gap-4 mb-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl shadow-lg">
                    🤖
                </div>
            </div>
            
            <div className="flex-1 space-y-4">
                <div className="bg-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-2xl rounded-tl-none p-5 text-gray-100 shadow-xl">
                    <p className="text-lg leading-relaxed whitespace-pre-wrap">{message}</p>
                </div>

                {examples.length > 0 && (
                    <div className="bg-blue-900/20 border border-blue-800/50 rounded-xl p-4 ml-4">
                        <p className="text-sm text-blue-300 font-semibold mb-2 flex items-center gap-2">
                            <span>💡</span> Exemples pour vous inspirer :
                        </p>
                        <ul className="space-y-2">
                            {examples.map((example, index) => (
                                <li key={index} className="text-sm text-gray-300 pl-4 border-l-2 border-blue-500/30 italic">
                                    "{example}"
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
