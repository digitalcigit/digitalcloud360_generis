import Image from 'next/image';
import { AboutSectionContent } from '@/types/blocks/about';

type AboutBlockProps = AboutSectionContent;

export default function AboutBlock({
    title,
    subtitle,
    description,
    mission,
    vision,
    image,
    stats,
    variant = 'simple'
}: AboutBlockProps) {

    // --- VARIANT: ENHANCED (Savor V2) ---
    if (variant === 'enhanced') {
        return (
            <section className="relative py-24 px-4 sm:px-6 lg:px-8 bg-[var(--color-background)] overflow-hidden">
                {/* Decorative Background Element */}
                <div className="absolute top-0 right-0 w-1/3 h-full bg-[var(--color-primary)]/5 -skew-x-12 transform origin-top translate-x-20" />

                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                        
                        {/* Image Side - Collage Effect */}
                        <div className="relative order-2 lg:order-1">
                            {image ? (
                                <div className="relative">
                                    {/* Main Image */}
                                    <div className="relative h-[500px] w-full rounded-lg overflow-hidden shadow-2xl z-10 transform -rotate-2 hover:rotate-0 transition-transform duration-500">
                                        <Image
                                            src={image}
                                            alt={title}
                                            fill
                                            className="object-cover"
                                            sizes="(min-width: 1024px) 50vw, 100vw"
                                        />
                                    </div>
                                    {/* Stats Badge Overlay (Savor V2 Style) */}
                                    {stats && stats.length > 0 && (
                                        <div className="absolute -bottom-6 -right-6 bg-[var(--color-primary)] text-white p-6 rounded-xl shadow-xl z-20 hidden md:block animate-bounce-slow">
                                            <span className="text-4xl font-bold block">{stats[0].value}</span>
                                            <span className="text-xs uppercase tracking-wider font-semibold opacity-90">{stats[0].label}</span>
                                        </div>
                                    )}
                                    {/* Decorative Frame */}
                                    <div className="absolute inset-0 border-2 border-[var(--color-primary)] rounded-lg transform translate-x-4 translate-y-4 z-0" />
                                </div>
                            ) : (
                                <div className="h-96 w-full bg-gray-200 rounded-lg flex items-center justify-center">
                                    <span className="text-gray-400">Image manquante</span>
                                </div>
                            )}
                        </div>

                        {/* Content Side */}
                        <div className="space-y-8 order-1 lg:order-2">
                            <div className="space-y-2">
                                {subtitle && (
                                    <p className="text-3xl text-[var(--color-accent)] font-[family-name:var(--font-accent)]">
                                        {subtitle}
                                    </p>
                                )}
                                <h2 className="text-4xl md:text-5xl font-bold text-[var(--color-text)] font-[family-name:var(--font-heading)] leading-tight">
                                    {title}
                                </h2>
                                <div className="w-20 h-1 bg-[var(--color-primary)] mt-4" />
                            </div>

                            <p className="text-lg text-gray-600 leading-relaxed font-[family-name:var(--font-body)]">
                                {description}
                            </p>

                            {(mission || vision) && (
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
                                    {mission && (
                                        <div className="bg-white p-6 rounded-lg shadow-md border-t-2 border-[var(--color-primary)]">
                                            <h3 className="font-bold text-[var(--color-text)] mb-2 font-[family-name:var(--font-heading)]">Mission</h3>
                                            <p className="text-sm text-gray-600">{mission}</p>
                                        </div>
                                    )}
                                    {vision && (
                                        <div className="bg-white p-6 rounded-lg shadow-md border-t-2 border-[var(--color-secondary)]">
                                            <h3 className="font-bold text-[var(--color-text)] mb-2 font-[family-name:var(--font-heading)]">Vision</h3>
                                            <p className="text-sm text-gray-600">{vision}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Stats - Elegant Row */}
                    {stats && stats.length > 0 && (
                        <div className="mt-24 border-t border-gray-200 pt-12">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                                {stats.map((stat, index) => (
                                    <div key={index} className="text-center group">
                                        <div className="text-5xl font-bold text-[var(--color-primary)] mb-2 font-[family-name:var(--font-heading)] group-hover:scale-110 transition-transform duration-300">
                                            {stat.value}
                                        </div>
                                        <div className="text-sm uppercase tracking-wider text-gray-500 font-semibold">
                                            {stat.label}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </section>
        );
    }

    // --- VARIANT: SIMPLE (Legacy) ---
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Content */}
                    <div className="space-y-6">
                        <h2 className="text-3xl sm:text-4xl font-bold text-[var(--color-text)] font-[family-name:var(--font-heading)]">
                            {title}
                        </h2>
                        {subtitle && (
                            <p className="text-xl text-[var(--color-primary)] font-semibold">
                                {subtitle}
                            </p>
                        )}
                        <p className="text-lg text-gray-600 leading-relaxed">
                            {description}
                        </p>

                        {mission && (
                            <div className="border-l-4 border-[var(--color-primary)] pl-4">
                                <h3 className="font-semibold text-[var(--color-text)]">Notre Mission</h3>
                                <p className="text-gray-600">{mission}</p>
                            </div>
                        )}

                        {vision && (
                            <div className="border-l-4 border-[var(--color-secondary)] pl-4">
                                <h3 className="font-semibold text-[var(--color-text)]">Notre Vision</h3>
                                <p className="text-gray-600">{vision}</p>
                            </div>
                        )}
                    </div>

                    {/* Image */}
                    {image && (
                        <div className="relative h-96 rounded-2xl overflow-hidden shadow-xl">
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

                {/* Stats */}
                {stats && stats.length > 0 && (
                    <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
                        {stats.map((stat, index) => (
                            <div key={index} className="text-center">
                                <div className="text-4xl font-bold text-[var(--color-primary)]">
                                    {stat.value}
                                </div>
                                <div className="text-gray-600 mt-1">
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}
