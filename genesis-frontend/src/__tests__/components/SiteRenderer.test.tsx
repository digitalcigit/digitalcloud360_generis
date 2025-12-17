import { afterEach, describe, expect, it, jest } from '@jest/globals';
import { render, waitFor } from '@testing-library/react';
import SiteRenderer from '@/components/SiteRenderer';

jest.mock('@/components/PageRenderer', () => ({
    __esModule: true,
    default: function MockPageRenderer(props) {
        const React = require('react');
        return React.createElement('div', { 'data-testid': 'page-slug' }, props.page.slug);
    },
}));

describe('SiteRenderer', () => {
    afterEach(() => {
        document.documentElement.removeAttribute('style');
    });

    it('renders Page not found when there are no pages', () => {
        const site = {
            metadata: { title: 'T', description: 'D' },
            theme: {
                colors: { primary: '#111', secondary: '#222', background: '#fff', text: '#000' },
                fonts: { heading: 'Arial', body: 'Arial' },
            },
            pages: [],
        };

        const { getByText } = render(<SiteRenderer site={site} />);
        expect(getByText('Page not found')).toBeTruthy();
    });

    it('selects the page matching currentPageSlug', () => {
        const site = {
            metadata: { title: 'T', description: 'D' },
            theme: {
                colors: { primary: '#111', secondary: '#222', background: '#fff', text: '#000' },
                fonts: { heading: 'Arial', body: 'Arial' },
            },
            pages: [
                { id: 'p1', slug: '/', title: 'Home', sections: [] },
                { id: 'p2', slug: '/about', title: 'About', sections: [] },
            ],
        };

        const { getByTestId } = render(<SiteRenderer site={site} currentPageSlug="/about" />);
        expect(getByTestId('page-slug').textContent).toBe('/about');
    });

    it('defaults to the first page when currentPageSlug is not found', () => {
        const site = {
            metadata: { title: 'T', description: 'D' },
            theme: {
                colors: { primary: '#111', secondary: '#222', background: '#fff', text: '#000' },
                fonts: { heading: 'Arial', body: 'Arial' },
            },
            pages: [
                { id: 'p1', slug: '/', title: 'Home', sections: [] },
                { id: 'p2', slug: '/about', title: 'About', sections: [] },
            ],
        };

        const { getByTestId } = render(<SiteRenderer site={site} currentPageSlug="/missing" />);
        expect(getByTestId('page-slug').textContent).toBe('/');
    });

    it('applies theme colors to CSS variables', async () => {
        const site = {
            metadata: { title: 'T', description: 'D' },
            theme: {
                colors: {
                    primary: '#123456',
                    secondary: '#654321',
                    accent: '#ff00ff',
                    background: '#fafafa',
                    text: '#101010',
                },
                fonts: { heading: 'Inter', body: 'Roboto' },
            },
            pages: [{ id: 'p1', slug: '/', title: 'Home', sections: [] }],
        };

        render(<SiteRenderer site={site} />);

        await waitFor(() => {
            expect(document.documentElement.style.getPropertyValue('--color-primary').trim()).toBe('#123456');
        });

        expect(document.documentElement.style.getPropertyValue('--color-secondary').trim()).toBe('#654321');
        expect(document.documentElement.style.getPropertyValue('--color-accent').trim()).toBe('#ff00ff');
        expect(document.documentElement.style.getPropertyValue('--color-background').trim()).toBe('#fafafa');
        expect(document.documentElement.style.getPropertyValue('--color-text').trim()).toBe('#101010');
        expect(document.documentElement.style.getPropertyValue('--font-heading').trim()).toBe('Inter');
        expect(document.documentElement.style.getPropertyValue('--font-body').trim()).toBe('Roboto');
    });
});
