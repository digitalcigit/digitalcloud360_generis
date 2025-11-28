'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatInterfaceProps {
    userId?: number;
    onBriefGenerated: (data: any) => void;
}

export default function ChatInterface({ userId, onBriefGenerated }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Bonjour ! Je suis Genesis, votre assistant pour créer votre site web. 🚀\n\nParlez-moi de votre business : quel est le nom de votre entreprise et que faites-vous ?",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
        
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        };
        
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    userId,
                    history: messages
                })
            });
            
            const data = await response.json();
            
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date()
            };
            
            setMessages(prev => [...prev, assistantMessage]);
            
            // Si un brief a été généré
            if (data.briefGenerated && data.siteData) {
                onBriefGenerated(data.siteData);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Désolé, une erreur s'est produite. Veuillez réessayer.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="flex flex-col h-full">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div 
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                            msg.role === 'user' 
                                ? 'bg-purple-600 text-white' 
                                : 'bg-gray-700 text-gray-100'
                        }`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 rounded-2xl px-4 py-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <div className="border-t border-gray-700 p-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Décrivez votre business..."
                        className="flex-1 bg-gray-700 border border-gray-600 rounded-full px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-full px-6 py-3 font-semibold transition-colors"
                    >
                        Envoyer
                    </button>
                </div>
            </div>
        </div>
    );
}
