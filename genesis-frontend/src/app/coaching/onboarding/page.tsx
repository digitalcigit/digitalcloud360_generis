'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';
import { coachingApi } from '@/utils/coaching-api';
import LogoUploader from '@/components/LogoUploader';
import { Loader2 } from 'lucide-react';

const SECTORS = [
    { value: "restaurant", label: "Restaurant / Alimentation" },
    { value: "salon", label: "Salon de coiffure / Beauté" },
    { value: "commerce", label: "Commerce / Boutique" },
    { value: "services", label: "Services aux particuliers" },
    { value: "artisanat", label: "Artisanat" },
    { value: "transport", label: "Transport / Livraison" },
    { value: "education", label: "Éducation / Formation" },
    { value: "sante", label: "Santé / Bien-être" },
    { value: "tech", label: "Tech / Digital" },
    { value: "other", label: "Autre..." },
];

export default function CoachingOnboardingPage() {
    const router = useRouter();
    const token = useAuthStore((s) => s.token);
    const setToken = useAuthStore((s) => s.setToken);
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    const [businessName, setBusinessName] = useState('');
    const [sector, setSector] = useState('restaurant');
    const [sectorOther, setSectorOther] = useState('');
    const [logoSource, setLogoSource] = useState<'upload' | 'generate' | 'later' | undefined>();
    const [logoUrl, setLogoUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Auto-fetch dev token if not authenticated
    useEffect(() => {
        const ensureToken = async () => {
            if (!token || !isAuthenticated()) {
                try {
                    const response = await fetch('/api/auth/dev-token');
                    if (response.ok) {
                        const data = await response.json();
                        setToken(data.access_token);
                    }
                } catch (err) {
                    console.error('Failed to get dev token:', err);
                }
            }
        };
        ensureToken();
    }, [token, isAuthenticated, setToken]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token || !isAuthenticated()) {
            router.push('/login?callbackUrl=/coaching/onboarding');
            return;
        }
        setIsLoading(true);
        setError(null);
        try {
            const payload = {
                business_name: businessName || undefined,
                sector,
                sector_other: sector === 'other' ? sectorOther : undefined,
                logo_source: logoSource,
                logo_url: logoUrl,
            };
            const res = await coachingApi.onboarding(token, payload);
            // Rediriger vers coaching en passant la session_id via query param
            router.push(`/coaching?session_id=${res.session_id}`);
        } catch (err: any) {
            setError(err.message || 'Erreur lors de la sauvegarde.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogoChange = (source: 'upload' | 'generate' | 'later', url?: string | null) => {
        setLogoSource(source);
        setLogoUrl(url ?? null);
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white flex items-center justify-center px-4 py-12">
            <div className="relative w-full max-w-4xl overflow-hidden rounded-3xl border border-gray-800 bg-gray-900/70 shadow-2xl">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.12),_transparent_45%),_radial-gradient(circle_at_bottom,_rgba(59,130,246,0.12),_transparent_45%)] pointer-events-none" />
                <div className="relative p-8 md:p-12 space-y-8">
                    <div className="space-y-3 text-center">
                        <span className="inline-block rounded-full border border-purple-500/40 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-100 uppercase tracking-wide">
                            Étape 0 — Onboarding
                        </span>
                        <h1 className="text-3xl md:text-4xl font-bold">Bienvenue sur Genesis AI</h1>
                        <p className="text-gray-300">Quelques informations rapides pour personnaliser votre coaching.</p>
                    </div>

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-200">Nom du projet</label>
                            <input
                                type="text"
                                className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                                placeholder="Mon Super Business"
                                value={businessName}
                                onChange={(e) => setBusinessName(e.target.value)}
                            />
                            <div className="text-xs text-gray-400">Laissez vide si vous n'avez pas encore de nom.</div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-200">Secteur d'activité</label>
                            <select
                                className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-white focus:border-purple-500 focus:outline-none"
                                value={sector}
                                onChange={(e) => setSector(e.target.value)}
                            >
                                {SECTORS.map((s) => (
                                    <option key={s.value} value={s.value}>{s.label}</option>
                                ))}
                            </select>
                            {sector === 'other' && (
                                <input
                                    type="text"
                                    className="mt-2 w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                                    placeholder="Précisez votre secteur"
                                    value={sectorOther}
                                    onChange={(e) => setSectorOther(e.target.value)}
                                    required
                                />
                            )}
                        </div>

                        <LogoUploader value={logoSource} onChange={handleLogoChange} />

                        {error && (
                            <div className="rounded-xl border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 px-4 py-3 text-lg font-bold text-white shadow-lg transition-transform hover:scale-[1.01] disabled:opacity-70"
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Sauvegarde...
                                </span>
                            ) : (
                                'Commencer le coaching →'
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </main>
    );
}
