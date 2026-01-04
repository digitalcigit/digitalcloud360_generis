'use client';

import React from 'react';
import Link from 'next/link';
import { ExternalLink, Edit2, Globe, Clock, AlertCircle } from 'lucide-react';
import { SiteListItem } from '@/types/dashboard';

interface SiteCardProps {
    site: SiteListItem;
}

export default function SiteCard({ site }: SiteCardProps) {
    const isExpired = site.status === 'expired';

    // Format date readable
    const formattedDate = new Date(site.created_at).toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });

    return (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col h-full">
            {/* Thumbnail Area */}
            <div className="h-40 bg-gray-100 relative group overflow-hidden">
                {site.hero_image_url ? (
                    <img
                        src={site.hero_image_url}
                        alt={site.business_name}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#F5F7FA] to-[#E6EEF5]">
                        <Globe className="text-gray-300" size={48} />
                    </div>
                )}

                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                    <Link
                        href={site.preview_url}
                        className="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
                        title="Voir le site"
                    >
                        <ExternalLink size={20} className="text-gray-900" />
                    </Link>
                    <Link
                        href={`/dashboard/sites/${site.session_id}`}
                        className="p-2 bg-[#2B4C7E] rounded-full hover:bg-[#1A365D] transition-colors"
                        title="Détails & Configuration"
                    >
                        <Edit2 size={20} className="text-white" />
                    </Link>
                </div>

                {/* Status Badge */}
                {isExpired && (
                    <div className="absolute top-2 right-2 bg-amber-100 text-amber-800 text-xs font-semibold px-2 py-1 rounded-md flex items-center gap-1">
                        <AlertCircle size={12} />
                        Expiré (Cache)
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="p-5 flex flex-col flex-1">
                <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                        <h3 className="font-bold text-lg text-gray-900 line-clamp-1" title={site.business_name}>
                            {site.business_name}
                        </h3>
                    </div>

                    <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                        {site.sector}
                    </p>
                </div>

                <div className="border-t border-gray-100 pt-4 mt-auto flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-1" title={`Créé le ${new Date(site.created_at).toLocaleString()}`}>
                        <Clock size={14} />
                        {formattedDate}
                    </div>

                    {site.theme_slug && (
                        <span className="capitalize bg-gray-100 px-2 py-0.5 rounded text-gray-600">
                            {site.theme_slug}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
