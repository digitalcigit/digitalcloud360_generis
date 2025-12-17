'use client';

export default function SiteRendererSkeleton() {
    return (
        <div className="min-h-screen bg-gray-950">
            <div className="mx-auto w-full max-w-5xl px-4 py-6">
                <div className="space-y-6">
                    <div className="h-10 w-2/3 animate-pulse rounded bg-gray-800" />
                    <div className="h-5 w-1/2 animate-pulse rounded bg-gray-800" />

                    <div className="h-64 w-full animate-pulse rounded-lg bg-gray-800" />

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                        <div className="h-28 animate-pulse rounded-lg bg-gray-800" />
                        <div className="h-28 animate-pulse rounded-lg bg-gray-800" />
                        <div className="h-28 animate-pulse rounded-lg bg-gray-800" />
                    </div>

                    <div className="h-48 w-full animate-pulse rounded-lg bg-gray-800" />
                    <div className="h-48 w-full animate-pulse rounded-lg bg-gray-800" />
                </div>
            </div>
        </div>
    );
}
