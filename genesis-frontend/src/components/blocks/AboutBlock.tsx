import { AboutSectionContent } from '@/types/blocks/about';

interface AboutBlockProps extends AboutSectionContent { }

export default function AboutBlock({
    title,
    subtitle,
    description,
    mission,
    vision,
    image,
    stats
}: AboutBlockProps) {
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
                            <img
                                src={image}
                                alt={title}
                                className="w-full h-full object-cover"
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
