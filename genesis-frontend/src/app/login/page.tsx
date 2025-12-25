'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';

export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const callbackUrl = searchParams.get('callbackUrl') || '/coaching';
    const setToken = useAuthStore((state) => state.setToken);

    useEffect(() => {
        // E2E Test Mode Simulation
        // For local E2E/Dev without DC360 running locally on port 3000/8000
        const simulateLogin = async () => {
            console.log('🔐 Simulating Login for E2E/Dev...');
            
            try {
                // Fetch a valid token from the backend
                const response = await fetch('/api/auth/dev-token', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (!response.ok) {
                    throw new Error('Failed to get dev token');
                }
                
                const data = await response.json();
                const fakeToken = data.access_token;
                
                // Set in Zustand Store (persisted to localStorage)
                setToken(fakeToken);
                
                // Set in Cookie for Server Actions / Middleware
                document.cookie = `access_token=${fakeToken}; path=/; max-age=86400`;
                document.cookie = `my-app-auth=${fakeToken}; path=/; max-age=86400`;
                
                console.log('✅ Token injected, redirecting to:', callbackUrl);
                router.push(callbackUrl);
            } catch (error) {
                console.error('❌ Failed to get dev token:', error);
                // Fallback to hardcoded token if API fails
                const fallbackToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY2MzM0ODAzfQ.Bi4YzlWTXPNkAnbRGQK25fWtzNRgAGu4Lp_xAwSQPNM";
                setToken(fallbackToken);
                router.push(callbackUrl);
            }
        };

        // Small delay to show UI
        const timer = setTimeout(() => {
            simulateLogin();
        }, 1000);

        return () => clearTimeout(timer);
    }, [router, setToken, callbackUrl]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 text-black">
            <div className="p-8 bg-white rounded-lg shadow-md max-w-md w-full text-center">
                <h1 className="text-2xl font-bold mb-4">Genesis AI Dev Login</h1>
                <p className="text-gray-600 mb-6">Simulation de l'authentification DC360...</p>
                <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent"></div>
                </div>
                <p className="text-xs text-gray-400 mt-8">Mode E2E / Développement Local</p>
            </div>
        </div>
    );
}
