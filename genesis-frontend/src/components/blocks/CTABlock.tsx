import { CTASectionContent } from '@/types/blocks/cta';

interface CTABlockProps extends CTASectionContent { }

export default function CTABlock({
    headline,
    description,
    primaryButton,
    secondaryButton,
    backgroundColor,
    backgroundImage
}: CTABlockProps) {
    return (
        <section
            className="py-20 px-4 sm:px-6 lg:px-8 relative"
            style={{
                backgroundColor: backgroundColor || 'var(--color-primary)',
                backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
            }}
        >
            {backgroundImage && (
                <div className="absolute inset-0 bg-black/50" />
            )}

            <div className="max-w-4xl mx-auto text-center relative z-10">
                <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-[family-name:var(--font-heading)]">
                    {headline}
                </h2>
                {description && (
                    <p className="text-xl text-white/90 mb-8">
                        {description}
                    </p>
                )}

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <a
                        href={primaryButton.href}
                        className={`px-8 py-3 rounded-lg font-semibold transition-colors ${primaryButton.variant === 'outline'
                                ? 'border-2 border-white text-white hover:bg-white hover:text-[var(--color-primary)]'
                                : 'bg-white text-[var(--color-primary)] hover:bg-gray-100'
                            }`}
                    >
                        {primaryButton.text}
                    </a>

                    {secondaryButton && (
                        <a
                            href={secondaryButton.href}
                            className="px-8 py-3 rounded-lg font-semibold border-2 border-white text-white hover:bg-white/10 transition-colors"
                        >
                            {secondaryButton.text}
                        </a>
                    )}
                </div>
            </div>
        </section>
    );
}
