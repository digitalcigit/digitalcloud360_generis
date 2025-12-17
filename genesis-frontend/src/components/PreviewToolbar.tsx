'use client';

import { ArrowLeft, Maximize2, Monitor, Smartphone, Tablet } from 'lucide-react';
import type { ReactNode } from 'react';

export type ViewportSize = 'mobile' | 'tablet' | 'desktop';

interface PreviewToolbarProps {
    currentViewport: ViewportSize;
    onViewportChange: (size: ViewportSize) => void;
    onBack?: () => void;
    onFullscreen?: () => void;
    title?: string;
}

export default function PreviewToolbar({
    currentViewport,
    onViewportChange,
    onBack,
    onFullscreen,
    title = 'Genesis Preview',
}: PreviewToolbarProps) {
    return (
        <div className="sticky top-0 z-50 flex items-center justify-between border-b border-gray-700 bg-gray-900 px-4 py-3 text-white">
            <div className="flex items-center gap-2">
                <button
                    type="button"
                    onClick={onBack}
                    className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
                    disabled={!onBack}
                    aria-label="Retour au chat"
                >
                    <ArrowLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">Chat</span>
                </button>

                <div className="hidden md:block px-2 text-sm font-semibold text-gray-200">
                    {title}
                </div>
            </div>

            <div className="flex items-center gap-1">
                <ViewportButton
                    isActive={currentViewport === 'mobile'}
                    onClick={() => onViewportChange('mobile')}
                    ariaLabel="Viewport mobile"
                >
                    <Smartphone className="h-4 w-4" />
                </ViewportButton>

                <ViewportButton
                    isActive={currentViewport === 'tablet'}
                    onClick={() => onViewportChange('tablet')}
                    ariaLabel="Viewport tablette"
                >
                    <Tablet className="h-4 w-4" />
                </ViewportButton>

                <ViewportButton
                    isActive={currentViewport === 'desktop'}
                    onClick={() => onViewportChange('desktop')}
                    ariaLabel="Viewport desktop"
                >
                    <Monitor className="h-4 w-4" />
                </ViewportButton>
            </div>

            <div>
                <button
                    type="button"
                    onClick={onFullscreen}
                    className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
                    disabled={!onFullscreen}
                    aria-label="Plein écran"
                >
                    <Maximize2 className="h-4 w-4" />
                    <span className="hidden sm:inline">Plein écran</span>
                </button>
            </div>
        </div>
    );
}

interface ViewportButtonProps {
    isActive: boolean;
    onClick: () => void;
    ariaLabel: string;
    children: ReactNode;
}

function ViewportButton({ isActive, onClick, ariaLabel, children }: ViewportButtonProps) {
    return (
        <button
            type="button"
            onClick={onClick}
            aria-label={ariaLabel}
            className={`inline-flex items-center justify-center rounded-md px-2 py-1 text-gray-200 hover:bg-gray-800 ${
                isActive ? 'bg-gray-800' : ''
            }`}
        >
            {children}
        </button>
    );
}
