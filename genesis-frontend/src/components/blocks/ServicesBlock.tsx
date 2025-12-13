import { ServicesSectionContent, ServiceItem } from '@/types/blocks/services';
import Image from 'next/image';
import { Star, Zap, Shield, Heart, Users, Settings, Globe, Mail, Phone } from 'lucide-react';
import { LucideIcon } from 'lucide-react';

// Map of common icon names to components
const iconMap: Record<string, LucideIcon> = {
    star: Star,
    zap: Zap,
    shield: Shield,
    heart: Heart,
    users: Users,
    settings: Settings,
    globe: Globe,
    mail: Mail,
    phone: Phone,
};

type ServicesBlockProps = ServicesSectionContent;

export default function ServicesBlock({
    title,
    subtitle,
    services,
    layout = 'grid'
}: ServicesBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
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

                {/* Services Grid */}
                <div className={`grid gap-8 ${layout === 'grid'
                        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                        : 'grid-cols-1'
                    }`}>
                    {services.map((service) => (
                        <ServiceCard key={service.id} service={service} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function ServiceCard({ service }: { service: ServiceItem }) {
    const IconComponent = service.icon ? (iconMap[service.icon.toLowerCase()] || Star) : Star;

    return (
        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            {service.icon && (
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 text-[var(--color-primary)]">
                    <IconComponent size={24} />
                </div>
            )}
            {service.image && (
                <div className="w-full h-48 relative rounded-lg mb-4 overflow-hidden">
                    <Image
                        src={service.image}
                        alt={service.title}
                        fill
                        sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
                        className="object-cover"
                        priority={false}
                    />
                </div>
            )}
            <h3 className="text-xl font-semibold text-[var(--color-text)] mb-2">
                {service.title}
            </h3>
            <p className="text-gray-600 mb-4">
                {service.description}
            </p>
            {service.price && (
                <p className="text-[var(--color-primary)] font-semibold">
                    {service.price}
                </p>
            )}
            {service.href && (
                <a
                    href={service.href}
                    className="inline-block mt-4 text-[var(--color-primary)] hover:text-[var(--color-secondary)] font-medium"
                >
                    En savoir plus →
                </a>
            )}
        </div>
    );
}
