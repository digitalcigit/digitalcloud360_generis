'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, Search } from 'lucide-react';
import { dashboardApi } from '@/utils/dashboard-api';
import { SiteListItem } from '@/types/dashboard';
import SiteCard from './SiteCard';

export default function SitesList() {
    const [sites, setSites] = useState<SiteListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSites = async () => {
            try {
                // Simple cookie retrieval
                const token = document.cookie
                    .split('; ')
                    .find(row => row.startsWith('access_token='))
                    ?.split('=')[1];

                if (!token) {
                    // Si pas de token, on laisse le AuthContext gérer (rediriger)
                    // Mais ici on veut éviter l'appel API qui fail
                    setError("Session expirée. Veuillez vous reconnecter.");
                    setLoading(false);
                    return;
                }

                const data = await dashboardApi.getUserSites(token);
                setSites(data);
            } catch (err) {
                console.error('Failed to fetch sites:', err);
                setError("Impossible de charger vos sites. Veuillez réessayer.");
            } finally {
                setLoading(false);
            }
        };

        fetchSites();
    }, []);

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-80 bg-gray-100 rounded-xl animate-pulse"></div>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-500 mb-4">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="text-[#2B4C7E] hover:underline"
                >
                    Réessayer
                </button>
            </div>
        );
    }

    return (
        <div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Mes Sites</h1>
                    <p className="text-gray-500 text-sm mt-1">
                        Gérez vos sites générés et leurs business briefs
                    </p>
                </div>

                <Link
                    href="/coaching/onboarding"
                    className="bg-[#2B4C7E] text-white px-4 py-2 rounded-lg hover:bg-[#1A365D] transition-colors flex items-center gap-2 text-sm font-medium w-fit"
                >
                    <Plus size={18} />
                    Créer un nouveau site
                </Link>
            </div>

            {sites.length === 0 ? (
                <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-300">
                    <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Globe className="text-gray-400" size={32} />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun site pour le moment</h3>
                    <p className="text-gray-500 max-w-sm mx-auto mb-6">
                        Commencez l'aventure Genesis en créant votre premier site web intelligent avec notre coach IA.
                    </p>
                    <Link
                        href="/coaching/onboarding"
                        className="text-[#2B4C7E] font-medium hover:underline"
                    >
                        Démarrer le coaching &rarr;
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {sites.map((site) => (
                        <SiteCard key={site.session_id} site={site} />
                    ))}
                </div>
            )}
        </div>
    );
}

function Globe({ className, size }: { className?: string; size?: number }) {
    // Lucide wrapper to fix hydration issues if imported directly in conditional render sometimes
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
    );
}
