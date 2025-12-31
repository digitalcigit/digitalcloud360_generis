'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';
import { themesApi } from '@/utils/themes-api';
import { ThemeRecommendation } from '@/types/theme';
import { Loader2, Check, Sparkles, Wand2, ArrowRight } from 'lucide-react';

export default function ThemeSelectionPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const briefId = searchParams.get('brief_id');
    const token = useAuthStore((state) => state.token);
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

    const [recommendations, setRecommendations] = useState<ThemeRecommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const [selectedThemeId, setSelectedThemeId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!isAuthenticated()) {
            router.push('/login?callbackUrl=/genesis/themes');
            return;
        }

        if (token && briefId) {
            loadRecommendations();
        } else if (!briefId) {
            setError("Identifiant de brief manquant.");
            setIsLoading(false);
        }
    }, [token, briefId]);

    const loadRecommendations = async () => {
        setIsLoading(true);
        try {
            const data = await themesApi.getRecommendations(token!, parseInt(briefId!));
            setRecommendations(data.recommendations);
            // Select the best match by default
            if (data.recommendations.length > 0) {
                setSelectedThemeId(data.recommendations[0].theme.id);
            }
        } catch (err: any) {
            console.error('Failed to load themes:', err);
            setError(err.message || "Erreur lors du chargement des thèmes.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectTheme = async () => {
        if (!selectedThemeId || !briefId || !token) return;

        setIsGenerating(true);
        try {
            const result = await themesApi.selectTheme(token, parseInt(briefId), selectedThemeId);
            // result contains { status: 'GENERATION_COMPLETED', session_id: '...', site_data: {...} }
            router.push(`/preview/${result.session_id}`);
        } catch (err: any) {
            console.error('Generation failed:', err);
            setError(err.message || "La génération a échoué. Veuillez réessayer.");
            setIsGenerating(false);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#030712] flex flex-col items-center justify-center text-white p-6">
                <div className="relative">
                    <div className="absolute inset-0 bg-purple-500 rounded-full blur-[80px] opacity-20 animate-pulse"></div>
                    <Loader2 className="w-16 h-16 text-purple-500 animate-spin relative z-10" />
                </div>
                <p className="mt-8 text-xl font-light text-purple-200 tracking-wide animate-pulse">
                    Analyse de votre business brief en cours...
                </p>
                <p className="text-gray-500 mt-2">Nous trouvons les designs parfaits pour vous.</p>
            </div>
        );
    }

    if (isGenerating) {
        return (
            <div className="min-h-screen bg-[#030712] flex flex-col items-center justify-center text-white p-6 overflow-hidden">
                <div className="max-w-md w-full text-center space-y-12">
                    <div className="relative mx-auto w-32 h-32">
                        <div className="absolute inset-0 bg-blue-500 rounded-full blur-[60px] opacity-30 animate-pulse"></div>
                        <div className="w-full h-full border-4 border-t-white border-white/10 rounded-full animate-spin"></div>
                        <Wand2 className="absolute inset-0 m-auto w-10 h-10 text-white animate-bounce" />
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent">
                            Génération de votre Univers
                        </h2>
                        <div className="flex flex-col gap-2">
                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 w-[70%] animate-[progress_8s_ease-in-out_infinite]"></div>
                            </div>
                            <div className="flex justify-between text-[10px] uppercase tracking-widest text-gray-500">
                                <span>Copywriting IA</span>
                                <span>Design System</span>
                                <span>Déploiement</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-3 text-left">
                        {[
                            "Rédaction de contenu stratégique...",
                            "Optimisation SEO sémantique...",
                            "Configuration des composants visuels...",
                            "Préparation de la prévisualisation..."
                        ].map((text, i) => (
                            <div key={i} className="flex items-center gap-3 text-sm text-gray-400 animate-in fade-in slide-in-from-left-4 fill-mode-both" style={{ animationDelay: `${i * 1.5}s` }}>
                                <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                                {text}
                            </div>
                        ))}
                    </div>

                    <p className="text-xs text-gray-600 italic">
                        Cela prend généralement entre 15 et 30 secondes.
                    </p>
                </div>

                <style jsx>{`
                    @keyframes progress {
                        0% { width: 0%; }
                        50% { width: 85%; }
                        100% { width: 95%; }
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#030712] text-white p-4 md:p-10 selection:bg-purple-500/30">
            {/* Ambient Background */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-purple-900/20 rounded-full blur-[120px]"></div>
                <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]"></div>
            </div>

            <div className="max-w-7xl mx-auto relative z-10">
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-16 animate-in fade-in slide-in-from-top-6 duration-700">
                    <div className="space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Phase Finale : Identité Visuelle</span>
                        </div>
                        <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-none">
                            Choisissez votre <br />
                            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">Design Maître</span>
                        </h1>
                        <p className="text-gray-400 text-lg max-w-xl">
                            Nos algorithmes ont analysé votre brief. Voici les thèmes qui maximiseront votre impact.
                        </p>
                    </div>

                    <button
                        onClick={handleSelectTheme}
                        disabled={!selectedThemeId}
                        className="group relative px-8 py-4 bg-white text-black font-bold rounded-2xl overflow-hidden transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 group-hover:opacity-10 transition-opacity"></div>
                        <span className="relative flex items-center gap-2">
                            Lancer la Création <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </span>
                    </button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {recommendations.map((rec, index) => (
                        <div
                            key={rec.theme.id}
                            onClick={() => setSelectedThemeId(rec.theme.id)}
                            className={`group relative cursor-pointer transition-all duration-500 ${selectedThemeId === rec.theme.id
                                    ? 'scale-[1.02] ring-2 ring-purple-500 shadow-[0_0_40px_rgba(168,85,247,0.2)]'
                                    : 'hover:scale-[1.01] hover:bg-white/5'
                                } bg-white/[0.02] border border-white/10 rounded-[2.5rem] overflow-hidden backdrop-blur-sm animate-in fade-in slide-in-from-bottom-8 fill-mode-both`}
                            style={{ animationDelay: `${index * 150}ms` }}
                        >
                            {/* Score Badge */}
                            <div className="absolute top-6 right-6 z-20 px-3 py-1 rounded-full bg-black/60 backdrop-blur-xl border border-white/10 flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                <span className="text-xs font-bold text-white">{Math.round(rec.match_score)}% Match</span>
                            </div>

                            {/* Thumbnail */}
                            <div className="relative h-64 overflow-hidden">
                                <img
                                    src={rec.theme.thumbnail_url || `https://placehold.co/600x400/111827/FFFFFF?text=${rec.theme.name}`}
                                    alt={rec.theme.name}
                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-transparent to-transparent"></div>

                                {selectedThemeId === rec.theme.id && (
                                    <div className="absolute inset-0 bg-purple-600/20 flex items-center justify-center backdrop-blur-[2px]">
                                        <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-black shadow-xl animate-in zoom-in duration-300">
                                            <Check className="w-6 h-6 stroke-[3]" />
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Content */}
                            <div className="p-8 space-y-4">
                                <div>
                                    <h3 className="text-2xl font-bold group-hover:text-purple-400 transition-colors">{rec.theme.name}</h3>
                                    <p className="text-xs font-bold uppercase tracking-widest text-gray-500 mt-1">{rec.theme.category}</p>
                                </div>

                                <p className="text-gray-400 text-sm leading-relaxed line-clamp-2 italic">
                                    "{rec.reasoning}"
                                </p>

                                <div className="pt-4 flex flex-wrap gap-2">
                                    {rec.theme.compatibility_tags.slice(0, 3).map(tag => (
                                        <span key={tag} className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[10px] text-gray-400 font-medium">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Border Highlight Effect */}
                            <div className={`absolute inset-0 border-2 transition-opacity duration-500 rounded-[2.5rem] ${selectedThemeId === rec.theme.id ? 'opacity-100' : 'opacity-0'
                                } pointer-events-none ring-offset-4 ring-offset-black ring-2 ring-purple-500/50`}></div>
                        </div>
                    ))}
                </div>

                {error && (
                    <div className="mt-12 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-center animate-in fade-in">
                        {error}
                        <button onClick={loadRecommendations} className="ml-4 underline font-bold">Réessayer</button>
                    </div>
                )}
            </div>
        </div>
    );
}
