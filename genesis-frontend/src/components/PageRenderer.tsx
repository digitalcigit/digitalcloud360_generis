import { SitePage } from '@/types/site-definition';
import BlockRenderer from './BlockRenderer';

interface PageRendererProps {
    page: SitePage;
}

export default function PageRenderer({ page }: PageRendererProps) {
    return (
        <main className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)] font-[family-name:var(--font-body)]">
            {page.sections.map((section) => (
                <BlockRenderer key={section.id} section={section} />
            ))}
        </main>
    );
}
