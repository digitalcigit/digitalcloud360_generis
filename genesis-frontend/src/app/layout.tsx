import type { Metadata } from 'next';
import { Inter, Playfair_Display, Lato, Great_Vibes } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

const inter = Inter({ 
    subsets: ['latin'],
    variable: '--font-inter'
});

const playfair = Playfair_Display({ 
    subsets: ['latin'],
    variable: '--font-playfair'
});

const lato = Lato({ 
    weight: ['100', '300', '400', '700', '900'],
    subsets: ['latin'],
    variable: '--font-lato'
});

const greatVibes = Great_Vibes({ 
    weight: '400',
    subsets: ['latin'],
    variable: '--font-great-vibes'
});

export const metadata: Metadata = {
    title: 'Genesis AI - Votre Partenaire Digital Intelligent',
    description: "Créez votre site web professionnel en quelques minutes grâce à l'IA",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="fr">
            <body className={`${inter.variable} ${playfair.variable} ${lato.variable} ${greatVibes.variable} font-sans antialiased`}>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
