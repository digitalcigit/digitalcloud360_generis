import { SiteTheme } from '@/types/site-definition';
import { useEffect } from 'react';

interface ThemeProviderProps {
    theme: SiteTheme;
    children: React.ReactNode;
}

export default function ThemeProvider({ theme, children }: ThemeProviderProps) {
    useEffect(() => {
        const root = document.documentElement;

        // Colors
        root.style.setProperty('--color-primary', theme.colors.primary);
        root.style.setProperty('--color-secondary', theme.colors.secondary);
        root.style.setProperty('--color-background', theme.colors.background);
        root.style.setProperty('--color-text', theme.colors.text);
        if (theme.colors.accent) {
            root.style.setProperty('--color-accent', theme.colors.accent);
        }

        // Fonts (Simulation - idealement chargerait depuis Google Fonts)
        root.style.setProperty('--font-heading', theme.fonts.heading);
        root.style.setProperty('--font-body', theme.fonts.body);
        if (theme.fonts.accent) {
            root.style.setProperty('--font-accent', theme.fonts.accent);
        }

    }, [theme]);

    return <>{children}</>;
}
