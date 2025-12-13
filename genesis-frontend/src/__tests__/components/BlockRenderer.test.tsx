import { render } from '@testing-library/react';
import BlockRenderer from '@/components/BlockRenderer';
import { SiteSection } from '@/types/site-definition';

// Mock data for each block type
const mockSections: Record<string, SiteSection> = {
    header: {
        id: 'header-1',
        type: 'header',
        content: {
            companyName: 'Test Co',
            navigation: [{ label: 'Home', href: '/' }],
            ctaButton: { text: 'Get Started', href: '#' }
        }
    },
    hero: {
        id: 'hero-1',
        type: 'hero',
        content: {
            title: 'Hero Title',
            subtitle: 'Hero Subtitle',
            cta: { text: 'Click Me', link: '#' }
        }
    },
    about: {
        id: 'about-1',
        type: 'about',
        content: {
            title: 'About Us',
            description: 'We are great.',
            stats: [{ value: '100+', label: 'Clients' }]
        }
    },
    services: {
        id: 'services-1',
        type: 'services',
        content: {
            title: 'Our Services',
            services: [
                { id: 's1', title: 'Service 1', description: 'Desc 1', icon: 'star' }
            ]
        }
    },
    features: {
        id: 'features-1',
        type: 'features',
        content: {
            title: 'Features',
            features: [
                { id: 'f1', title: 'Feature 1', description: 'Desc 1', icon: 'zap' }
            ]
        }
    },
    testimonials: {
        id: 'testimonials-1',
        type: 'testimonials',
        content: {
            title: 'Testimonials',
            testimonials: [
                { id: 't1', quote: 'Great!', author: 'John Doe', rating: 5 }
            ]
        }
    },
    contact: {
        id: 'contact-1',
        type: 'contact',
        content: {
            title: 'Contact Us',
            email: 'test@example.com',
            showForm: true
        }
    },
    gallery: {
        id: 'gallery-1',
        type: 'gallery',
        content: {
            title: 'Gallery',
            images: [
                { id: 'g1', src: 'https://via.placeholder.com/150', alt: 'Image 1' }
            ]
        }
    },
    cta: {
        id: 'cta-1',
        type: 'cta',
        content: {
            headline: 'Ready?',
            primaryButton: { text: 'Yes', href: '#' }
        }
    },
    footer: {
        id: 'footer-1',
        type: 'footer',
        content: {
            copyright: '© 2024 Test Co',
            companyName: 'Test Co',
            links: [{ text: 'Privacy', url: '#' }]
        }
    }
};

describe('BlockRenderer Smoke Tests', () => {
    // Test each block type renders without crashing
    Object.entries(mockSections).forEach(([type, section]) => {
        it(`renders ${type} block without crashing`, () => {
            expect(() => render(<BlockRenderer section={section} />)).not.toThrow();
        });
    });

    // Test unknown block type
    it('handles unknown block types gracefully', () => {
        const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => { });
        const unknownSection = {
            id: 'unknown-1',
            type: 'unknown-type',
            content: {}
        };

        const { container } = render(<BlockRenderer section={unknownSection} />);
        expect(container).toBeEmptyDOMElement();
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Unknown section type'));
        consoleSpy.mockRestore();
    });
});
