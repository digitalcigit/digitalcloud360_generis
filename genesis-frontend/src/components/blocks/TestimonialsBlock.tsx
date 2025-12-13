import { TestimonialsSectionContent, TestimonialItem } from '@/types/blocks/testimonials';
import Image from 'next/image';
import { Star } from 'lucide-react';

type TestimonialsBlockProps = TestimonialsSectionContent;

export default function TestimonialsBlock({
    title,
    subtitle,
    testimonials,
    layout = 'grid'
}: TestimonialsBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl font-bold text-[var(--color-text)] font-[family-name:var(--font-heading)]">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="mt-4 text-xl text-gray-600">
                            {subtitle}
                        </p>
                    )}
                </div>

                <div className={`grid gap-8 ${layout === 'grid'
                        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                        : 'grid-cols-1 max-w-2xl mx-auto'
                    }`}>
                    {testimonials.map((testimonial) => (
                        <TestimonialCard key={testimonial.id} testimonial={testimonial} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function TestimonialCard({ testimonial }: { testimonial: TestimonialItem }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-lg">
            {/* Rating */}
            {testimonial.rating && (
                <div className="flex mb-4">
                    {[...Array(5)].map((_, i) => (
                        <Star
                            key={i}
                            size={20}
                            className={i < (testimonial.rating || 5) ? 'text-yellow-400 fill-current' : 'text-gray-300'}
                        />
                    ))}
                </div>
            )}

            {/* Quote */}
            <blockquote className="text-gray-600 italic mb-6">
                &quot;{testimonial.quote}&quot;
            </blockquote>

            {/* Author */}
            <div className="flex items-center">
                {testimonial.avatar && (
                    <div className="relative w-12 h-12 mr-4">
                        <Image
                            src={testimonial.avatar}
                            alt={testimonial.author}
                            fill
                            sizes="48px"
                            className="rounded-full object-cover"
                        />
                    </div>
                )}
                <div>
                    <p className="font-semibold text-[var(--color-text)]">
                        {testimonial.author}
                    </p>
                    {(testimonial.role || testimonial.company) && (
                        <p className="text-sm text-gray-500">
                            {testimonial.role}{testimonial.role && testimonial.company && ', '}
                            {testimonial.company}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
