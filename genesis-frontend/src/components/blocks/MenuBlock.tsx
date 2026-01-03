import { useState } from 'react';
import Image from 'next/image';
import { MenuSectionContent } from '@/types/blocks/menu';

type MenuBlockProps = MenuSectionContent;

export default function MenuBlock({
    title,
    subtitle,
    categories,
    currency = '€'
}: MenuBlockProps) {
    const [activeCategory, setActiveCategory] = useState(categories[0]?.id || '');

    if (!categories || categories.length === 0) return null;

    const activeItems = categories.find(c => c.id === activeCategory)?.items || [];

    return (
        <section className="py-24 px-4 sm:px-6 lg:px-8 bg-[var(--color-background)]">
            <div className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="text-center mb-16 space-y-4">
                    {subtitle && (
                        <span className="text-[var(--color-accent)] font-[family-name:var(--font-accent)] text-2xl md:text-3xl">
                            {subtitle}
                        </span>
                    )}
                    <h2 className="text-4xl md:text-5xl font-bold font-[family-name:var(--font-heading)] text-[var(--color-text)]">
                        {title}
                    </h2>
                    <div className="w-24 h-1 bg-[var(--color-primary)] mx-auto mt-6"></div>
                </div>

                {/* Category Tabs */}
                <div className="flex flex-wrap justify-center gap-4 mb-12">
                    {categories.map((category) => (
                        <button
                            key={category.id}
                            onClick={() => setActiveCategory(category.id)}
                            className={`px-6 py-2 rounded-full text-lg font-medium transition-all duration-300 font-[family-name:var(--font-heading)] tracking-wide ${
                                activeCategory === category.id
                                    ? 'bg-[var(--color-primary)] text-white shadow-lg scale-105'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                        >
                            {category.title}
                        </button>
                    ))}
                </div>

                {/* Menu Items Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-12 gap-y-8 animate-fade-in-up">
                    {activeItems.map((item, index) => (
                        <div key={index} className={`group flex justify-between items-start border-b border-gray-100 pb-4 hover:border-gray-200 transition-colors relative ${item.isHighlight ? 'border-l-4 border-l-[var(--color-primary)] pl-4 bg-[var(--color-primary)]/5 rounded-r-lg' : ''}`}>
                            {item.isHighlight && (
                                <span className="absolute -top-3 right-0 bg-[var(--color-primary)] text-white text-[10px] px-2 py-0.5 uppercase font-bold rounded">
                                    Signature
                                </span>
                            )}
                            <div className="flex-1 pr-4">
                                <div className="flex justify-between items-baseline">
                                    <h3 className="text-xl font-bold font-[family-name:var(--font-heading)] text-[var(--color-text)] group-hover:text-[var(--color-primary)] transition-colors">
                                        {item.title}
                                    </h3>
                                    <span className="text-lg font-bold text-[var(--color-primary)] whitespace-nowrap ml-4 italic">
                                        {item.price}{currency}
                                    </span>
                                </div>
                                {item.description && (
                                    <p className="text-gray-500 italic mt-1 font-[family-name:var(--font-body)]">
                                        {item.description}
                                    </p>
                                )}
                                {item.dietary && item.dietary.length > 0 && (
                                    <div className="flex gap-2 mt-2">
                                        {item.dietary.map((tag, i) => (
                                            <span key={i} className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded-full border border-green-100">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
