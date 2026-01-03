import Image from 'next/image';
import { FooterSectionContent } from '@/types/blocks/footer';
import { Facebook, Twitter, Instagram, Linkedin, Youtube, MapPin, Phone, Mail, Clock, Send } from 'lucide-react';
import { LucideIcon } from 'lucide-react';

// Map of social platform to icons
const socialIconMap: Record<string, LucideIcon> = {
    facebook: Facebook,
    twitter: Twitter,
    instagram: Instagram,
    linkedin: Linkedin,
    youtube: Youtube,
};

type FooterBlockProps = FooterSectionContent;

export default function FooterBlock({
    copyright,
    links,
    logo,
    companyName,
    description,
    socialLinks,
    columns,
    variant = 'simple',
    openingHours,
    contactInfo,
    newsletter
}: FooterBlockProps) {

    // --- VARIANT: RESTAURANT ---
    if (variant === 'restaurant') {
        return (
            <footer className="bg-[#1a1a1a] text-white pt-20 pb-8 px-4 sm:px-6 lg:px-8 border-t border-[var(--color-primary)]/20">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
                        
                        {/* COL 1: Brand & Bio */}
                        <div className="space-y-6">
                            <div className="flex items-center space-x-2">
                                {logo ? (
                                    logo.includes('placehold.co') ? (
                                        <img src={logo} alt={companyName} className="h-12 w-auto brightness-0 invert" />
                                    ) : (
                                        <Image src={logo} alt={companyName || 'Logo'} width={160} height={40} className="h-12 w-auto brightness-0 invert" />
                                    )
                                ) : (
                                    <span className="text-3xl font-bold font-[family-name:var(--font-heading)]">{companyName}</span>
                                )}
                            </div>
                            {description && (
                                <p className="text-gray-400 text-sm leading-relaxed font-[family-name:var(--font-body)]">
                                    {description}
                                </p>
                            )}
                            {socialLinks && (
                                <div className="flex space-x-4">
                                    {socialLinks.map((link, idx) => {
                                        const Icon = socialIconMap[link.platform] || MapPin;
                                        return (
                                            <a key={idx} href={link.url} className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-[var(--color-primary)] hover:text-white transition-all duration-300">
                                                <Icon size={18} />
                                            </a>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        {/* COL 2: Opening Hours */}
                        <div>
                            <h3 className="text-xl font-bold mb-6 font-[family-name:var(--font-heading)] text-[var(--color-primary)]">Horaires</h3>
                            <ul className="space-y-3">
                                {openingHours?.map((slot, idx) => (
                                    <li key={idx} className="flex justify-between text-sm border-b border-gray-800 pb-2">
                                        <span className="text-gray-300">{slot.days}</span>
                                        <span className="text-[var(--color-accent)] font-medium">{slot.hours}</span>
                                    </li>
                                )) || (
                                    <li className="text-gray-400 italic">Horaires non spécifiés</li>
                                )}
                            </ul>
                        </div>

                        {/* COL 3: Contact */}
                        <div>
                            <h3 className="text-xl font-bold mb-6 font-[family-name:var(--font-heading)] text-[var(--color-primary)]">Contact</h3>
                            <ul className="space-y-4">
                                {contactInfo?.address && (
                                    <li className="flex items-start space-x-3 text-gray-400">
                                        <MapPin size={20} className="text-[var(--color-primary)] mt-1 shrink-0" />
                                        <span>{contactInfo.address}</span>
                                    </li>
                                )}
                                {contactInfo?.phone && (
                                    <li className="flex items-center space-x-3 text-gray-400">
                                        <Phone size={20} className="text-[var(--color-primary)] shrink-0" />
                                        <span>{contactInfo.phone}</span>
                                    </li>
                                )}
                                {contactInfo?.email && (
                                    <li className="flex items-center space-x-3 text-gray-400">
                                        <Mail size={20} className="text-[var(--color-primary)] shrink-0" />
                                        <span>{contactInfo.email}</span>
                                    </li>
                                )}
                            </ul>
                        </div>

                        {/* COL 4: Newsletter */}
                        <div>
                            <h3 className="text-xl font-bold mb-6 font-[family-name:var(--font-heading)] text-[var(--color-primary)]">Newsletter</h3>
                            <p className="text-gray-400 text-sm mb-4">
                                {newsletter?.description || "Inscrivez-vous pour recevoir nos dernières offres."}
                            </p>
                            <form className="relative">
                                <input 
                                    type="email" 
                                    placeholder={newsletter?.placeholder || "Votre email..."}
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg py-3 px-4 text-white focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                                />
                                <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-[var(--color-primary)] rounded-md text-white hover:bg-white hover:text-[var(--color-primary)] transition-all">
                                    <Send size={16} />
                                </button>
                            </form>
                        </div>
                    </div>

                    {/* Bottom Bar */}
                    <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
                        <p className="font-[family-name:var(--font-body)]">{copyright}</p>
                        <div className="flex space-x-6 mt-4 md:mt-0">
                            <a href="#" className="hover:text-[var(--color-primary)] transition-colors">Mentions Légales</a>
                            <a href="#" className="hover:text-[var(--color-primary)] transition-colors">Politique de Confidentialité</a>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }

    // --- VARIANT: SIMPLE (Legacy) ---
    return (
        <footer className="bg-gray-900 text-white pt-16 pb-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
                    {/* Brand Column */}
                    <div className="space-y-4">
                        {logo ? (
                            logo.includes('placehold.co') || logo.includes('placeholder') ? (
                                <img
                                    src={logo}
                                    alt={companyName ?? 'Logo de la marque'}
                                    className="h-8 w-auto brightness-0 invert"
                                />
                            ) : (
                                <Image
                                    src={logo}
                                    alt={companyName ?? 'Logo de la marque'}
                                    width={128}
                                    height={32}
                                    className="h-8 w-auto brightness-0 invert"
                                />
                            )
                        ) : (
                            <span className="text-2xl font-bold font-[family-name:var(--font-heading)]">{companyName}</span>
                        )}
                        {description && (
                            <p className="text-gray-400 text-sm leading-relaxed">
                                {description}
                            </p>
                        )}
                        {/* Social Links */}
                        {socialLinks && socialLinks.length > 0 && (
                            <div className="flex space-x-4 pt-4">
                                {socialLinks.map((link, index) => {
                                    const Icon = socialIconMap[link.platform] || MapPin;
                                    return (
                                        <a
                                            key={index}
                                            href={link.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-gray-400 hover:text-white transition-colors"
                                        >
                                            <Icon size={20} />
                                        </a>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Link Columns */}
                    {columns && columns.length > 0 ? (
                        columns.map((col, idx) => (
                            <div key={idx}>
                                <h3 className="text-lg font-semibold mb-4">{col.title}</h3>
                                <ul className="space-y-2">
                                    {col.links.map((link, lIdx) => (
                                        <li key={lIdx}>
                                            <a href={link.url} className="text-gray-400 hover:text-white transition-colors text-sm">
                                                {link.text}
                                            </a>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))
                    ) : (
                        /* Fallback simple links if no columns defined */
                        links && links.length > 0 && (
                            <div className="md:col-span-3 flex flex-wrap gap-8 md:justify-end items-start">
                                {links.map((link, index) => (
                                    <a
                                        key={index}
                                        href={link.url}
                                        className="text-gray-400 hover:text-white transition-colors"
                                    >
                                        {link.text}
                                    </a>
                                ))}
                            </div>
                        )
                    )}
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
                    <p>{copyright}</p>
                    <div className="flex space-x-6 mt-4 md:mt-0">
                        <a href="#" className="hover:text-white">Privacy Policy</a>
                        <a href="#" className="hover:text-white">Terms of Service</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
