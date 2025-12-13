import Image from 'next/image';
import { HeroSectionContent } from '@/types/blocks/hero';

type HeroBlockProps = HeroSectionContent;

export default function HeroBlock({
    title,
    subtitle,
    description,
    image,
    cta,
    alignment = 'center',
    overlay = false
}: HeroBlockProps) {
    const alignmentClasses = {
        left: 'text-left items-start',
        center: 'text-center items-center',
        right: 'text-right items-end'
    };

    return (
        <section className="relative bg-gradient-to-br from-blue-50 to-indigo-100 py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
            {/* Background Image with Overlay */}
            {image && overlay && (
                <div className="absolute inset-0 z-0">
                    <Image
                        src={image}
                        alt={title}
                        fill
                        className="object-cover"
                        sizes="100vw"
                    />
                    <div className="absolute inset-0 bg-black/60" />
                </div>
            )}

            <div className={`max-w-7xl mx-auto relative z-10 ${overlay ? 'text-white' : ''}`}>
                <div className={`grid grid-cols-1 ${(!overlay && image) ? 'lg:grid-cols-2' : ''} gap-12 items-center`}>
                    <div className={`space-y-6 flex flex-col ${alignmentClasses[alignment]}`}>
                        <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight font-[family-name:var(--font-heading)] ${overlay ? 'text-white' : 'text-[var(--color-text)]'}`}>
                            {title}
                        </h1>
                        <p className={`text-xl leading-relaxed max-w-2xl ${overlay ? 'text-gray-200' : 'text-gray-600'}`}>
                            {subtitle}
                        </p>
                        {description && (
                            <p className={`text-lg leading-relaxed max-w-2xl ${overlay ? 'text-gray-300' : 'text-gray-500'}`}>
                                {description}
                            </p>
                        )}
                        {cta && (
                            <a
                                href={cta.link}
                                className={`inline-block font-semibold px-8 py-3 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl ${cta.variant === 'outline'
                                        ? `border-2 ${overlay ? 'border-white text-white hover:bg-white hover:text-[var(--color-primary)]' : 'border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white'}`
                                        : cta.variant === 'secondary'
                                            ? 'bg-[var(--color-secondary)] hover:opacity-90 text-white'
                                            : 'bg-[var(--color-primary)] hover:opacity-90 text-white'
                                    }`}
                            >
                                {cta.text}
                            </a>
                        )}
                    </div>

                    {/* Side Image (only if not overlay) */}
                    {image && !overlay && (
                        <div className="relative h-96 rounded-2xl overflow-hidden shadow-2xl">
                            <Image
                                src={image}
                                alt={title}
                                fill
                                className="object-cover"
                                sizes="(min-width: 1024px) 50vw, 100vw"
                            />
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
