'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { dashboardApi } from '@/utils/dashboard-api';
import { BriefResponse, BriefUpdateRequest } from '@/types/dashboard';
import SiteDetailHeader from '@/components/dashboard/SiteDetailHeader';
import SitePreviewEmbed from '@/components/dashboard/SitePreviewEmbed';
import BusinessBriefViewer from '@/components/dashboard/BusinessBriefViewer';
import BusinessBriefEditor from '@/components/dashboard/BusinessBriefEditor';
import ConversationHistoryModal from '@/components/dashboard/ConversationHistoryModal';
import { Loader2 } from 'lucide-react';

export default function SiteDetailPage() {
    const params = useParams();
    const siteId = params.siteId as string;

    const [brief, setBrief] = useState<BriefResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showHistory, setShowHistory] = useState(false);

    const [isEditing, setIsEditing] = useState(false);
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    useEffect(() => {
        const fetchBrief = async () => {
            try {
                const token = getAuthToken();
                if (!token) {
                    setError("Session expirée.");
                    setLoading(false);
                    return;
                }

                const data = await dashboardApi.getSiteBrief(siteId, token);
                setBrief(data);
            } catch (err) {
                console.error("Error fetching brief:", err);
                setError("Impossible de charger les détails du site.");
            } finally {
                setLoading(false);
            }
        };

        if (siteId) {
            fetchBrief();
        }
    }, [siteId]);

    const getAuthToken = () => {
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1];
    };

    const handleUpdateBrief = async (updates: BriefUpdateRequest) => {
        try {
            const token = getAuthToken();
            if (!token) throw new Error("No token");

            await dashboardApi.updateSiteBrief(siteId, updates, token);

            // Refresh local state
            setBrief(prev => prev ? { ...prev, ...updates } : null);
            setIsEditing(false);

            // Note: On pourrait ajouter un toast ici si une librairie comme sonner est dispo
            console.log("Brief mis à jour avec succès");
        } catch (err) {
            console.error("Failed to update brief:", err);
            alert("Erreur lors de la mise à jour du brief.");
        }
    };

    const handleRegenerate = async () => {
        if (!confirm("Voulez-vous vraiment regénérer le site ? Cela mettra à jour l'aperçu avec vos dernières modifications.")) {
            return;
        }

        setIsRegenerating(true);
        try {
            const token = getAuthToken();
            if (!token) throw new Error("No token");

            await dashboardApi.regenerateSite(siteId, token);

            // Bump trigger to force iframe reload
            setRefreshTrigger(prev => prev + 1);

            console.log("Site regénéré avec succès");
        } catch (err) {
            console.error("Failed to regenerate site:", err);
            alert("Erreur lors de la régénération du site.");
        } finally {
            setIsRegenerating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <Loader2 className="animate-spin text-[#2B4C7E]" size={32} />
            </div>
        );
    }

    if (error || !brief) {
        return (
            <div className="text-center py-12">
                <p className="text-red-500">{error || "Site introuvable"}</p>
            </div>
        );
    }

    const previewUrl = `/preview/${siteId}`;

    return (
        <div className="max-w-6xl mx-auto pb-12">
            <SiteDetailHeader
                businessName={brief.business_name}
                previewUrl={previewUrl}
                onShowConversation={() => setShowHistory(true)}
                onRegenerate={handleRegenerate}
                isRegenerating={isRegenerating}
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Column: Preview */}
                <div className="lg:col-span-2 space-y-6">
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-lg font-semibold text-gray-900">Aperçu du Site</h2>
                            {isRegenerating && (
                                <span className="text-xs text-blue-600 animate-pulse flex items-center gap-1 font-medium">
                                    <Loader2 size={12} className="animate-spin" />
                                    Mise à jour en cours...
                                </span>
                            )}
                        </div>
                        <SitePreviewEmbed
                            previewUrl={previewUrl}
                            refreshTrigger={refreshTrigger}
                        />
                    </section>
                </div>

                {/* Sidebar Column: Brief */}
                <div className="space-y-6">
                    {isEditing ? (
                        <BusinessBriefEditor
                            brief={brief}
                            onSave={handleUpdateBrief}
                            onCancel={() => setIsEditing(false)}
                        />
                    ) : (
                        <BusinessBriefViewer
                            brief={brief}
                            onEdit={() => setIsEditing(true)}
                        />
                    )}
                </div>
            </div>

            <ConversationHistoryModal
                sessionId={siteId}
                isOpen={showHistory}
                onClose={() => setShowHistory(false)}
            />
        </div>
    );
}
