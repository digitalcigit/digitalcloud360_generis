import { SiteDefinition } from '@/types/site-definition';
import PageRenderer from '@/components/PageRenderer';
import ThemeProvider from '@/components/ThemeProvider';

interface SiteRendererProps {
    site: SiteDefinition;
    currentPageSlug?: string;
}

export default function SiteRenderer({ site, currentPageSlug = '/' }: SiteRendererProps) {
    const currentPage = site.pages.find(p => p.slug === currentPageSlug) || site.pages[0];

    if (!currentPage) {
        return <div>Page not found</div>;
    }

    return (
        <ThemeProvider theme={site.theme}>
            <PageRenderer page={currentPage} />
        </ThemeProvider>
    );
}
