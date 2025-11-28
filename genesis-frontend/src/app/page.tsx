import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

export default async function HomePage() {
    const user = await getCurrentUser();
    
    // Si authentifié, rediriger vers le chat
    if (user) {
        redirect('/chat');
    }
    
    // Sinon, afficher la page de connexion/redirection
    return (
        <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
            <div className="container mx-auto px-4 py-16 flex flex-col items-center justify-center min-h-screen">
                {/* Logo */}
                <div className="mb-8">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        Genesis AI
                    </h1>
                    <p className="text-gray-400 text-center mt-2">
                        Votre Partenaire Digital Intelligent
                    </p>
                </div>
                
                {/* Message */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md text-center">
                    <h2 className="text-2xl font-semibold mb-4">
                        Bienvenue sur Genesis
                    </h2>
                    <p className="text-gray-300 mb-6">
                        Pour accéder à votre espace de création, veuillez vous connecter via DigitalCloud360.
                    </p>
                    <a 
                        href={process.env.NEXT_PUBLIC_DC360_URL || 'http://localhost:3000'}
                        className="inline-block bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                    >
                        Se connecter via DC360
                    </a>
                </div>
                
                {/* Features */}
                <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
                    <FeatureCard 
                        icon="💬" 
                        title="Chat IA" 
                        description="Décrivez votre business, Genesis crée votre site"
                    />
                    <FeatureCard 
                        icon="🎨" 
                        title="Design Automatique" 
                        description="Templates professionnels adaptés à votre secteur"
                    />
                    <FeatureCard 
                        icon="🚀" 
                        title="Publication Instantanée" 
                        description="Votre site en ligne en quelques minutes"
                    />
                </div>
            </div>
        </main>
    );
}

function FeatureCard({ icon, title, description }: { 
    icon: string; 
    title: string; 
    description: string 
}) {
    return (
        <div className="bg-white/5 backdrop-blur rounded-xl p-6 text-center">
            <div className="text-4xl mb-4">{icon}</div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">{description}</p>
        </div>
    );
}
