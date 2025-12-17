'use client';

import { useEffect, useState, Suspense } from 'react';
import { useParams } from 'next/navigation';
import { getSite } from '@/utils/api';
import { useAuthStore } from '@/stores/useAuthStore';
import { SiteDefinition } from '@/types/site-definition';
import BlockRenderer from '@/components/BlockRenderer';

function SiteContent() {
    const params = useParams();
    const siteId = params.id as string;
    const token = useAuthStore((state) => state.token);
    const [site, setSite] = useState<SiteDefinition | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchSite() {
            if (!token) {
                setError('Non authentifié');
                setLoading(false);
                return;
            }

            try {
                const siteData = await getSite(siteId, token);
                setSite(siteData.site_definition);
            } catch (err) {
                setError('Impossible de charger le site');
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        fetchSite();
    }, [siteId, token]);

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Chargement du site...</p>
                </div>
            </div>
        );
    }

    if (error || !site) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-red-600 mb-2">Erreur</h2>
                    <p className="text-gray-600">{error || 'Site non trouvé'}</p>
                </div>
            </div>
        );
    }

    // Apply theme colors to the page
    const homePage = site.pages.find(p => p.slug === '/');

    return (
        <div className="min-h-screen">
            <style jsx global>{`
        :root {
          --color-primary: ${site.theme.colors.primary};
          --color-secondary: ${site.theme.colors.secondary};
          --color-background: ${site.theme.colors.background};
          --color-text: ${site.theme.colors.text};
        }
      `}</style>

            {homePage?.sections.map((section) => (
                <BlockRenderer key={section.id} section={section} />
            ))}
        </div>
    );
}

export default function SitePage() {
    return (
        <Suspense fallback={<div>Chargement...</div>}>
            <SiteContent />
        </Suspense>
    );
}
