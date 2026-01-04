'use client';

import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, LogOut, Settings, Home } from 'lucide-react';
import { usePathname } from 'next/navigation';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    const isActive = (path: string) => pathname.startsWith(path);

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 fixed h-full z-10 hidden md:block">
                <div className="p-6">
                    <Link href="/" className="flex items-center gap-2 mb-8">
                        <span className="text-2xl font-bold bg-gradient-to-r from-[#2B4C7E] to-[#5680BC] bg-clip-text text-transparent">
                            Genesis
                        </span>
                        <span className="text-xs font-medium px-2 py-0.5 bg-[#E6EEF5] text-[#2B4C7E] rounded-full">
                            Dashboard
                        </span>
                    </Link>

                    <nav className="space-y-1">
                        <Link
                            href="/dashboard/sites"
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive('/dashboard/sites')
                                    ? 'bg-[#E6EEF5] text-[#2B4C7E]'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            <LayoutDashboard size={18} />
                            Mes Sites
                        </Link>

                        <Link
                            href="/"
                            className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                        >
                            <Home size={18} />
                            Retour Accueil
                        </Link>
                    </nav>
                </div>

                <div className="absolute bottom-0 w-full p-6 border-t border-gray-100">
                    <div className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-500">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2B4C7E] to-[#5680BC] flex items-center justify-center text-white font-bold text-xs">
                            U
                        </div>
                        <div>
                            <p className="text-gray-900">Utilisateur</p>
                            <p className="text-xs">Premium Plan</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 md:ml-64 min-h-screen">
                <div className="p-8 max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
