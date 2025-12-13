import Image from 'next/image';
import { FooterSectionContent } from '@/types/blocks/footer';
import { Facebook, Twitter, Instagram, Linkedin, Youtube, MapPin } from 'lucide-react';
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
    columns
}: FooterBlockProps) {
    return (
        <footer className="bg-gray-900 text-white pt-16 pb-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
                    {/* Brand Column */}
                    <div className="space-y-4">
                        {logo ? (
                            <Image
                                src={logo}
                                alt={companyName ?? 'Logo de la marque'}
                                width={128}
                                height={32}
                                className="h-8 w-auto brightness-0 invert"
                            />
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
