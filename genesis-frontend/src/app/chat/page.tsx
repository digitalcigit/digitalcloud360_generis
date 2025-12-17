'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { redirect } from 'next/navigation';
import ChatInterface, { type BriefGeneratedPayload } from '@/components/ChatInterface';
import { SiteDefinition } from '@/types/site-definition';
import SiteRenderer from '@/components/SiteRenderer';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
    const { user, isLoading, isAuthenticated } = useAuth();
    const [briefGenerated, setBriefGenerated] = useState(false);
    const [siteData, setSiteData] = useState<SiteDefinition | null>(null);
    const [siteId, setSiteId] = useState<string | null>(null);
    const router = useRouter();
    
    if (isLoading) {
        return <LoadingSpinner />;
    }
    
    if (!isAuthenticated) {
        redirect('/');
    }
    
    return (
        <main className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
                <div className="flex items-center justify-between max-w-7xl mx-auto">
                    <h1 className="text-xl font-bold text-purple-400">Genesis AI</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-gray-400">{user?.email}</span>
                        <a 
                            href={process.env.NEXT_PUBLIC_DC360_URL || 'http://localhost:3000'}
                            className="text-sm text-gray-500 hover:text-white"
                        >
                            Retour au Hub
                        </a>
                    </div>
                </div>
            </header>
            
            {/* Main Content */}
            <div className="flex h-[calc(100vh-73px)]">
                {/* Chat Panel */}
                <div className="w-1/2 border-r border-gray-700">
                    <ChatInterface 
                        onBriefGenerated={(data: BriefGeneratedPayload) => {
                            setBriefGenerated(true);
                            setSiteId(data.siteId);
                            setSiteData(data.siteDefinition);
                        }}
                    />
                </div>
                
                {/* Preview Panel */}
                <div className="w-1/2 bg-gray-950">
                    {briefGenerated && siteData ? (
                        <SitePreview
                            data={siteData}
                            onOpenPreview={siteId ? () => router.push(`/preview/${siteId}`) : undefined}
                            canOpenPreview={!!siteId}
                        />
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            <div className="text-center">
                                <div className="text-6xl mb-4">🎨</div>
                                <p>Votre site apparaîtra ici</p>
                                <p className="text-sm mt-2">Commencez par décrire votre business dans le chat</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}

function LoadingSpinner() {
    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
    );
}

function SitePreview({
    data,
    onOpenPreview,
    canOpenPreview,
}: {
    data: SiteDefinition;
    onOpenPreview?: () => void;
    canOpenPreview: boolean;
}) {
    void data;
    return (
        <div className="h-full overflow-auto">
            <div className="border-b border-gray-800 bg-gray-900 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-base font-semibold">🎉 Votre site est prêt !</h2>
                        <p className="text-sm text-gray-300">Genesis a créé votre site web à partir de vos informations.</p>
                    </div>

                    <button
                        type="button"
                        onClick={onOpenPreview}
                        disabled={!canOpenPreview || !onOpenPreview}
                        className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg"
                    >
                        Voir mon site
                    </button>
                </div>
            </div>

            <div className="bg-white text-black">
                <SiteRenderer site={data} />
            </div>
        </div>
    );
}
