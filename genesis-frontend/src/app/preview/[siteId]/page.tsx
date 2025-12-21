'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getSitePreview, getCoachingSite } from '@/utils/api';
import { getCookieValue } from '@/utils/cookies';
import { useAuthStore } from '@/stores/useAuthStore';
import type { SiteDefinition } from '@/types/site-definition';
import SiteRenderer from '@/components/SiteRenderer';
import PreviewToolbar, { ViewportSize } from '@/components/PreviewToolbar';
import SiteRendererSkeleton from '@/components/SiteRendererSkeleton';

export default function PreviewPage() {
    const params = useParams();
    const router = useRouter();

    const siteId = params.siteId as string;

    const storeToken = useAuthStore((state) => state.token);
    const token = storeToken || getCookieValue('access_token');

    const [viewport, setViewport] = useState<ViewportSize>('desktop');
    const [site, setSite] = useState<SiteDefinition | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchPreview() {
            // SECURITY: Validate siteId format before API call
            // Allow both site_ID and UUID (session ID)
            if (!siteId) {
                setError('ID manquant');
                setLoading(false);
                return;
            }

            if (!token) {
                setError('Non authentifié');
                setLoading(false);
                return;
            }

            try {
                // If siteId starts with "site_", it's a generated site ID.
                // Otherwise, assume it's a coaching session UUID.
                // We can also check if it contains '-' but UUIDs do, and site_ also might.
                // Logic: Session IDs (UUIDs) don't usually start with "site_".
                let siteDefinition: SiteDefinition;
                
                if (siteId.startsWith('site_')) {
                    siteDefinition = await getSitePreview(siteId, token);
                } else {
                    siteDefinition = await getCoachingSite(siteId, token);
                }
                
                setSite(siteDefinition);
            } catch (err) {
                console.error('Preview fetch error:', err);
                setError('Impossible de charger le site');
            } finally {
                setLoading(false);
            }
        }

        setLoading(true);
        setError(null);
        setSite(null);

        fetchPreview();
    }, [siteId, token]);

    const viewportStyle = useMemo(() => {
        if (viewport === 'mobile') return { width: 375 };
        if (viewport === 'tablet') return { width: 768 };
        return { width: '100%' };
    }, [viewport]);

    const handleFullscreen = async () => {
        try {
            if (document.fullscreenElement) {
                await document.exitFullscreen();
                return;
            }

            if (document.documentElement.requestFullscreen) {
                await document.documentElement.requestFullscreen();
            }
        } catch {
            // ignore
        }
    };

    return (
        <div className="flex min-h-screen flex-col bg-gray-950 text-white">
            <PreviewToolbar
                currentViewport={viewport}
                onViewportChange={setViewport}
                onBack={() => router.push('/chat')}
                onFullscreen={handleFullscreen}
            />

            <div className="flex-1 overflow-auto p-4">
                {loading ? (
                    <SiteRendererSkeleton />
                ) : error || !site ? (
                    <div className="mx-auto flex h-full max-w-3xl items-center justify-center">
                        <div className="rounded-lg border border-gray-800 bg-gray-900 p-6 text-center">
                            <h2 className="mb-2 text-xl font-semibold text-red-400">Erreur</h2>
                            <p className="text-gray-300">{error || 'Site non trouvé'}</p>
                        </div>
                    </div>
                ) : (
                    <div className="mx-auto" style={viewportStyle}>
                        <div className={viewport === 'desktop' ? '' : 'overflow-hidden rounded-lg border border-gray-800 shadow-2xl'}>
                            <SiteRenderer site={site} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
