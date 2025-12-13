import { ContactSectionContent } from '@/types/blocks/contact';
import { useState } from 'react';
import { Mail, Phone, MapPin, Facebook, Twitter, Instagram, Linkedin, Youtube } from 'lucide-react';
import { LucideIcon } from 'lucide-react';

// Map of social platform to icons
const socialIconMap: Record<string, LucideIcon> = {
    facebook: Facebook,
    twitter: Twitter,
    instagram: Instagram,
    linkedin: Linkedin,
    youtube: Youtube,
};

type ContactBlockProps = ContactSectionContent;

export default function ContactBlock({
    title,
    subtitle,
    description,
    email,
    phone,
    address,
    socialLinks,
    showForm = true,
    formFields
}: ContactBlockProps) {
    const [formData, setFormData] = useState<Record<string, string>>({});

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Form submitted:', formData);
        // TODO: Implement form submission
        alert('Message envoyé ! (Simulation)');
    };

    return (
        <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Contact Info */}
                    <div className="space-y-8">
                        <div>
                            <h2 className="text-3xl sm:text-4xl font-bold text-[var(--color-text)] font-[family-name:var(--font-heading)]">
                                {title}
                            </h2>
                            {subtitle && (
                                <p className="mt-2 text-xl text-gray-600">
                                    {subtitle}
                                </p>
                            )}
                            {description && (
                                <p className="mt-4 text-gray-600">
                                    {description}
                                </p>
                            )}
                        </div>

                        <div className="space-y-4">
                            {email && (
                                <div className="flex items-center space-x-3">
                                    <Mail className="text-[var(--color-primary)]" />
                                    <a href={`mailto:${email}`} className="text-gray-600 hover:text-[var(--color-primary)]">
                                        {email}
                                    </a>
                                </div>
                            )}
                            {phone && (
                                <div className="flex items-center space-x-3">
                                    <Phone className="text-[var(--color-primary)]" />
                                    <a href={`tel:${phone}`} className="text-gray-600 hover:text-[var(--color-primary)]">
                                        {phone}
                                    </a>
                                </div>
                            )}
                            {address && (
                                <div className="flex items-start space-x-3">
                                    <MapPin className="text-[var(--color-primary)]" />
                                    <div className="text-gray-600">
                                        <p>{address.street}</p>
                                        <p>{address.city}, {address.country}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Social Links */}
                        {socialLinks && socialLinks.length > 0 && (
                            <div className="flex space-x-4">
                                {socialLinks.map((link, index) => {
                                    const Icon = socialIconMap[link.platform] || MapPin;
                                    return (
                                        <a
                                            key={index}
                                            href={link.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-blue-100 transition-colors text-[var(--color-primary)]"
                                        >
                                            <Icon size={20} />
                                        </a>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Contact Form */}
                    {showForm && (
                        <form onSubmit={handleSubmit} className="space-y-6 bg-gray-50 p-8 rounded-xl">
                            {(formFields || [
                                { name: 'name', type: 'text', label: 'Nom', required: true },
                                { name: 'email', type: 'email', label: 'Email', required: true },
                                { name: 'message', type: 'textarea', label: 'Message', required: true }
                            ]).map((field) => (
                                <div key={field.name}>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        {field.label} {field.required && '*'}
                                    </label>
                                    {field.type === 'textarea' ? (
                                        <textarea
                                            name={field.name}
                                            required={field.required}
                                            placeholder={field.placeholder}
                                            rows={4}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                                            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                                        />
                                    ) : (
                                        <input
                                            type={field.type}
                                            name={field.name}
                                            required={field.required}
                                            placeholder={field.placeholder}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                                            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                                        />
                                    )}
                                </div>
                            ))}
                            <button
                                type="submit"
                                className="w-full bg-[var(--color-primary)] text-white py-3 px-6 rounded-lg font-semibold hover:opacity-90 transition-opacity"
                            >
                                Envoyer
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </section>
    );
}
