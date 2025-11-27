'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const setToken = useAuthStore((state) => state.setToken);

    useEffect(() => {
        const token = searchParams.get('token');
        if (token) {
            setToken(token);
            router.push('/dashboard');
        } else {
            router.push('/');
        }
    }, [searchParams, setToken, router]);

    return (
        <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
                <h2 className="text-2xl font-bold">Authentification en cours...</h2>
                <p>Veuillez patienter pendant que nous vous connectons.</p>
            </div>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={<div>Chargement...</div>}>
            <CallbackContent />
        </Suspense>
    );
}
