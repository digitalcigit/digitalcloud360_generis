import { GallerySectionContent, GalleryImage } from '@/types/blocks/gallery';

interface GalleryBlockProps extends GallerySectionContent { }

export default function GalleryBlock({
    title,
    subtitle,
    images,
    layout = 'grid',
    columns = 3
}: GalleryBlockProps) {
    const gridCols = {
        2: 'grid-cols-1 sm:grid-cols-2',
        3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
        4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
    };

    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                {(title || subtitle) && (
                    <div className="text-center mb-12">
                        {title && (
                            <h2 className="text-3xl sm:text-4xl font-bold text-[var(--color-text)] font-[family-name:var(--font-heading)]">
                                {title}
                            </h2>
                        )}
                        {subtitle && (
                            <p className="mt-4 text-xl text-gray-600">
                                {subtitle}
                            </p>
                        )}
                    </div>
                )}

                <div className={`grid ${gridCols[columns]} gap-4`}>
                    {images.map((image) => (
                        <GalleryItem key={image.id} image={image} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function GalleryItem({ image }: { image: GalleryImage }) {
    const content = (
        <div className="relative group overflow-hidden rounded-lg h-64">
            <img
                src={image.src}
                alt={image.alt}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            {image.caption && (
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-end">
                    <p className="text-white p-4 w-full text-center">{image.caption}</p>
                </div>
            )}
        </div>
    );

    if (image.href) {
        return (
            <a href={image.href} className="block">
                {content}
            </a>
        );
    }

    return content;
}
