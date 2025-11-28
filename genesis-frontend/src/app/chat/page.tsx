'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { redirect } from 'next/navigation';
import ChatInterface from '@/components/ChatInterface';

export default function ChatPage() {
    const { user, isLoading, isAuthenticated } = useAuth();
    const [briefGenerated, setBriefGenerated] = useState(false);
    const [siteData, setSiteData] = useState(null);
    
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
                        userId={user?.id}
                        onBriefGenerated={(data) => {
                            setBriefGenerated(true);
                            setSiteData(data);
                        }}
                    />
                </div>
                
                {/* Preview Panel */}
                <div className="w-1/2 bg-gray-950">
                    {briefGenerated && siteData ? (
                        <SitePreview data={siteData} />
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

function SitePreview({ data }: { data: any }) {
    return (
        <div className="p-8">
            <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">🎉 Votre site est prêt !</h2>
                <p className="text-gray-300 mb-4">
                    Genesis a créé votre site web à partir de vos informations.
                </p>
                <button className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-6 rounded-lg">
                    Voir mon site
                </button>
            </div>
        </div>
    );
}
