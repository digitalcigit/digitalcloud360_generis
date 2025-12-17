require('@testing-library/jest-dom');

jest.mock('next/image', () => ({
    __esModule: true,
    default: ({ src, alt, ...props }) => {
        const resolvedSrc = typeof src === 'string' ? src : '';
        return require('react').createElement('img', { src: resolvedSrc, alt, ...props });
    },
}));

jest.mock('next/dynamic', () => ({
    __esModule: true,
    default: () => () => null,
}));
