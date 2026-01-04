'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, RefreshCw, MessageSquare } from 'lucide-react';

interface SiteDetailHeaderProps {
    businessName: string;
    previewUrl: string;
    onRegenerate?: () => void;
    isRegenerating?: boolean;
    onShowConversation?: () => void;
}

export default function SiteDetailHeader({ businessName, previewUrl, onRegenerate, isRegenerating, onShowConversation }: SiteDetailHeaderProps) {
    return (
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
                <Link
                    href="/dashboard/sites"
                    className="p-2 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                    <ArrowLeft size={20} />
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">{businessName}</h1>
                    <p className="text-gray-500 text-sm">Configuration & Aperçu</p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                {onShowConversation && (
                    <button
                        onClick={onShowConversation}
                        className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <MessageSquare size={16} />
                        Conversation
                    </button>
                )}
                {onRegenerate && (
                    <button
                        onClick={onRegenerate}
                        disabled={isRegenerating}
                        className="flex items-center gap-2 px-4 py-2 border border-blue-200 text-[#2B4C7E] bg-blue-50/50 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                        <RefreshCw size={16} className={isRegenerating ? "animate-spin" : ""} />
                        {isRegenerating ? 'Régénération...' : 'Régénérer le site'}
                    </button>
                )}

                <a
                    href={previewUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-[#2B4C7E] text-white rounded-lg hover:bg-[#1A365D] transition-colors"
                >
                    <ExternalLink size={16} />
                    Voir en live
                </a>
            </div>
        </div>
    );
}
