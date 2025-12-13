import { HeaderSectionContent } from '@/types/blocks/header';
import Image from 'next/image';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';

type HeaderBlockProps = HeaderSectionContent;

export default function HeaderBlock({
    logo,
    companyName,
    navigation,
    ctaButton,
    sticky = true
}: HeaderBlockProps) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <header className={`bg-white shadow-sm z-50 ${sticky ? 'sticky top-0' : 'relative'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex-shrink-0 flex items-center">
                        {logo ? (
                            <Image
                                src={logo}
                                alt={companyName}
                                width={128}
                                height={32}
                                className="h-8 w-auto"
                                priority
                            />
                        ) : (
                            <span className="text-2xl font-bold text-[var(--color-primary)] font-[family-name:var(--font-heading)]">
                                {companyName}
                            </span>
                        )}
                    </div>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex space-x-8">
                        {navigation.map((item) => (
                            <a
                                key={item.label}
                                href={item.href}
                                className="text-gray-500 hover:text-[var(--color-primary)] px-3 py-2 rounded-md text-sm font-medium transition-colors"
                            >
                                {item.label}
                            </a>
                        ))}
                    </nav>

                    {/* CTA Button */}
                    <div className="hidden md:flex items-center">
                        {ctaButton && (
                            <a
                                href={ctaButton.href}
                                className="ml-8 inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[var(--color-primary)] hover:opacity-90 transition-opacity"
                            >
                                {ctaButton.text}
                            </a>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="flex items-center md:hidden">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[var(--color-primary)]"
                        >
                            <span className="sr-only">Open main menu</span>
                            {isMobileMenuOpen ? (
                                <X className="block h-6 w-6" aria-hidden="true" />
                            ) : (
                                <Menu className="block h-6 w-6" aria-hidden="true" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                        {navigation.map((item) => (
                            <a
                                key={item.label}
                                href={item.href}
                                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-[var(--color-primary)] hover:bg-gray-50"
                            >
                                {item.label}
                            </a>
                        ))}
                        {ctaButton && (
                            <a
                                href={ctaButton.href}
                                className="block w-full text-center mt-4 px-4 py-3 rounded-md shadow-sm text-base font-medium text-white bg-[var(--color-primary)] hover:opacity-90"
                            >
                                {ctaButton.text}
                            </a>
                        )}
                    </div>
                </div>
            )}
        </header>
    );
}
