export interface GallerySectionContent {
    title?: string;
    subtitle?: string;
    images: GalleryImage[];
    layout?: 'grid' | 'masonry' | 'carousel';
    columns?: 2 | 3 | 4;
}

export interface GalleryImage {
    id: string;
    src: string;
    alt: string;
    caption?: string;
    href?: string;
}
