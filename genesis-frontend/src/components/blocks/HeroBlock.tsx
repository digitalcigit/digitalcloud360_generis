import Image from 'next/image';
import { useState, useEffect } from 'react';
import { HeroSectionContent, HeroSlide } from '@/types/blocks/hero';
import { ChevronLeft, ChevronRight } from 'lucide-react';

type HeroBlockProps = HeroSectionContent;

export default function HeroBlock({
    title,
    subtitle,
    description,
    image,
    cta,
    alignment = 'center',
    overlay = false,
    variant = 'standard',
    slides = []
}: HeroBlockProps) {
    const [currentSlide, setCurrentSlide] = useState(0);

    // Auto-advance slider
    useEffect(() => {
        if (variant === 'slider' && slides.length > 1) {
            const timer = setInterval(() => {
                setCurrentSlide((prev) => (prev + 1) % slides.length);
            }, 5000);
            return () => clearInterval(timer);
        }
    }, [variant, slides.length]);

    const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);
    const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);

    // Alignment mapping
    const alignmentClasses = {
        left: 'text-left items-start',
        center: 'text-center items-center',
        right: 'text-right items-end'
    };

    // --- RENDERERS ---

    // 1. SLIDER VARIANT
    if (variant === 'slider' && slides.length > 0) {
        return (
            <section className="relative h-[80vh] min-h-[600px] w-full overflow-hidden bg-black">
                {slides.map((slide, index) => (
                    <div
                        key={index}
                        className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
                            index === currentSlide ? 'opacity-100 z-10' : 'opacity-0 z-0'
                        }`}
                    >
                        {/* Background Image */}
                        <div className="absolute inset-0">
                            <Image
                                src={slide.image}
                                alt={slide.title}
                                fill
                                className="object-cover"
                                priority={index === 0}
                            />
                            <div className="absolute inset-0 bg-black/40" />
                        </div>

                        {/* Content */}
                        <div className="relative z-20 h-full flex items-center justify-center text-center px-4">
                            <div className="max-w-4xl space-y-6 animate-fade-in-up">
                                {slide.subtitle && (
                                    <p className="text-xl md:text-2xl text-[var(--color-accent)] font-[family-name:var(--font-accent)]">
                                        {slide.subtitle}
                                    </p>
                                )}
                                <h1 className="text-5xl md:text-7xl font-bold text-white font-[family-name:var(--font-heading)] leading-tight">
                                    {slide.title}
                                </h1>
                                {slide.cta && (
                                    <a
                                        href={slide.cta.link}
                                        className="inline-block mt-8 px-8 py-4 bg-[var(--color-primary)] text-white font-semibold rounded hover:bg-white hover:text-[var(--color-primary)] transition-all duration-300"
                                    >
                                        {slide.cta.text}
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Controls */}
                <button 
                    onClick={prevSlide}
                    className="absolute left-4 top-1/2 -translate-y-1/2 z-30 p-2 text-white/70 hover:text-white transition-colors"
                >
                    <ChevronLeft size={48} />
                </button>
                <button 
                    onClick={nextSlide}
                    className="absolute right-4 top-1/2 -translate-y-1/2 z-30 p-2 text-white/70 hover:text-white transition-colors"
                >
                    <ChevronRight size={48} />
                </button>
            </section>
        );
    }

    // 2. SPLIT VARIANT (Modern Split)
    if (variant === 'split' || (!overlay && image)) {
        return (
            <section className="relative bg-[var(--color-background)] overflow-hidden">
                <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[70vh]">
                    {/* Text Side */}
                    <div className="flex items-center justify-center p-12 lg:p-24 order-2 lg:order-1">
                        <div className={`space-y-6 max-w-xl ${alignmentClasses[alignment]}`}>
                            {/* Decorative Line */}
                            <div className="w-20 h-1 bg-[var(--color-primary)] mb-6"></div>
                            
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight font-[family-name:var(--font-heading)] text-[var(--color-text)]">
                                {title}
                            </h1>
                            <p className="text-xl leading-relaxed text-gray-600 font-[family-name:var(--font-body)]">
                                {subtitle}
                            </p>
                            {description && (
                                <p className="text-lg leading-relaxed text-gray-500 font-[family-name:var(--font-body)]">
                                    {description}
                                </p>
                            )}
                            {cta && (
                                <a
                                    href={cta.link}
                                    className={`inline-block font-semibold px-8 py-4 rounded-none border-2 transition-all duration-300 ${
                                        cta.variant === 'outline'
                                            ? 'border-[var(--color-text)] text-[var(--color-text)] hover:bg-[var(--color-text)] hover:text-white'
                                            : 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white hover:bg-transparent hover:text-[var(--color-primary)]'
                                    }`}
                                >
                                    {cta.text}
                                </a>
                            )}
                        </div>
                    </div>

                    {/* Image Side */}
                    <div className="relative h-96 lg:h-auto order-1 lg:order-2">
                        {image ? (
                            image.includes('placehold.co') ? (
                                <img src={image} alt={title} className="w-full h-full object-cover" />
                            ) : (
                                <Image
                                    src={image}
                                    alt={title}
                                    fill
                                    className="object-cover"
                                    sizes="(min-width: 1024px) 50vw, 100vw"
                                />
                            )
                        ) : (
                            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                                <span className="text-gray-400">No Image</span>
                            </div>
                        )}
                    </div>
                </div>
            </section>
        );
    }

    // 3. STANDARD VARIANT (Fallback / Original Overlay)
    return (
        <section className="relative bg-gradient-to-br from-blue-50 to-indigo-100 py-32 px-4 sm:px-6 lg:px-8 overflow-hidden min-h-[60vh] flex items-center">
            {/* Background Image with Overlay */}
            {image && (
                <div className="absolute inset-0 z-0">
                    {image.includes('placehold.co') ? (
                         <img src={image} alt={title} className="w-full h-full object-cover" />
                    ) : (
                        <Image
                            src={image}
                            alt={title}
                            fill
                            className="object-cover"
                            sizes="100vw"
                        />
                    )}
                    <div className="absolute inset-0 bg-black/50" />
                </div>
            )}

            <div className="max-w-7xl mx-auto relative z-10 w-full">
                <div className={`flex flex-col ${alignmentClasses[alignment]} space-y-8`}>
                    <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight font-[family-name:var(--font-heading)] text-white drop-shadow-lg">
                        {title}
                    </h1>
                    <div className="h-1 w-24 bg-[var(--color-primary)] mx-auto rounded-full"></div>
                    <p className="text-2xl leading-relaxed max-w-3xl text-gray-100 drop-shadow-md font-[family-name:var(--font-body)]">
                        {subtitle}
                    </p>
                    {description && (
                        <p className="text-lg leading-relaxed max-w-2xl text-gray-200">
                            {description}
                        </p>
                    )}
                    {cta && (
                        <a
                            href={cta.link}
                            className="inline-block font-bold uppercase tracking-wider px-10 py-4 bg-[var(--color-primary)] text-white rounded hover:bg-white hover:text-[var(--color-primary)] transition-all duration-300 shadow-xl mt-8"
                        >
                            {cta.text}
                        </a>
                    )}
                </div>
            </div>
        </section>
    );
}
