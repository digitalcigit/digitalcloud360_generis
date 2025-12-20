import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';
import CoachingInterface from '@/components/coaching/CoachingInterface';

export const metadata = {
    title: 'Coach Genesis AI - DigitalCloud360',
    description: 'Votre partenaire intelligent pour construire votre business.',
};

export default async function CoachingPage() {
    const user = await getCurrentUser();
    
    // Pour le développement/test si SSO n'est pas encore parfait, on peut commenter cette ligne
    // Mais pour la prod, c'est requis.
    if (!user) {
        // Redirection vers login DC360 ou page d'accueil
        redirect('/login?callbackUrl=/coaching');
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white relative overflow-hidden">
            {/* Background Decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-900/20 rounded-full blur-[100px]" />
            </div>

            <div className="container mx-auto px-4 py-8 max-w-5xl relative z-10">
                <header className="text-center mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className="inline-block mb-3 px-3 py-1 rounded-full bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold tracking-wider uppercase">
                        Mode Maïeutique Argent
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-white via-purple-100 to-blue-200 bg-clip-text text-transparent mb-4">
                        Coach Genesis AI
                    </h1>
                    <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
                        Construisons ensemble les fondations solides de votre futur succès.
                        <br className="hidden md:block" />
                        Je suis là pour vous guider étape par étape.
                    </p>
                </header>
                
                <div className="bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-3xl p-4 md:p-8 shadow-2xl">
                    <CoachingInterface />
                </div>

                <footer className="text-center mt-12 text-sm text-gray-600">
                    <p>© 2025 DigitalCloud360 - Propulsé par Genesis AI Deep Agents</p>
                </footer>
            </div>
        </main>
    );
}
