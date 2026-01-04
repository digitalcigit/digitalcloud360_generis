'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

interface SitePreviewEmbedProps {
    previewUrl: string;
    refreshTrigger?: number; // To force iframe reload
}

export default function SitePreviewEmbed({ previewUrl, refreshTrigger = 0 }: SitePreviewEmbedProps) {
    const [isLoading, setIsLoading] = React.useState(true);

    // Refresh iframe when trigger changes
    const urlWithTrigger = `${previewUrl}?t=${refreshTrigger}`;

    return (
        <div className="w-full bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center gap-2">
                <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>
                <div className="mx-auto text-xs text-gray-400 font-mono bg-white px-3 py-1 rounded border border-gray-200 w-1/2 text-center truncate">
                    {previewUrl}
                </div>
            </div>

            <div className="relative aspect-[16/9] w-full bg-gray-100">
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                        <Loader2 className="animate-spin" size={32} />
                    </div>
                )}
                <iframe
                    src={urlWithTrigger}
                    className="w-full h-full border-0"
                    onLoad={() => setIsLoading(false)}
                    title="Site Preview"
                />
            </div>
        </div>
    );
}
