'use client';

import React, { useEffect, useState } from 'react';
import { X, MessageSquare, User, Bot } from 'lucide-react';
import { dashboardApi } from '@/utils/dashboard-api';
import { ConversationMessage } from '@/types/dashboard';

interface ConversationHistoryModalProps {
    sessionId: string;
    isOpen: boolean;
    onClose: () => void;
}

export default function ConversationHistoryModal({ sessionId, isOpen, onClose }: ConversationHistoryModalProps) {
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen && sessionId) {
            fetchConversation();
        }
    }, [isOpen, sessionId]);

    const fetchConversation = async () => {
        setLoading(true);
        try {
            const token = document.cookie
                .split('; ')
                .find(row => row.startsWith('access_token='))
                ?.split('=')[1];

            if (!token) {
                setError("Non authentifié");
                setLoading(false);
                return;
            }

            const data = await dashboardApi.getSiteConversation(sessionId, token);
            setMessages(data.messages);
        } catch (err) {
            console.error(err);
            setError("Impossible de charger la conversation.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                {/* Header */}
                <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-[#2B4C7E]">
                        <MessageSquare size={20} />
                        <h3 className="font-semibold text-lg">Historique de Coaching</h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 text-gray-400 hover:text-gray-900 rounded-full hover:bg-gray-100 transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
                    {loading ? (
                        <div className="text-center py-8 text-gray-500">Chargement...</div>
                    ) : error ? (
                        <div className="text-center py-8 text-red-500">{error}</div>
                    ) : messages.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">Aucun message trouvé.</div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                                    }`}>
                                    {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                                </div>
                                <div className={`max-w-[80%] rounded-lg p-3 text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-[#2B4C7E] text-white rounded-tr-none'
                                        : 'bg-white border border-gray-200 text-gray-700 rounded-tl-none shadow-sm'
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
