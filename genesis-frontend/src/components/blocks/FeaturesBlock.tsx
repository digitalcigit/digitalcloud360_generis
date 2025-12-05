import { FeaturesSectionContent, FeatureItem } from '@/types/blocks/features';
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

interface FeaturesBlockProps extends FeaturesSectionContent { }

export default function FeaturesBlock({ title, subtitle, features, layout = 'grid' }: FeaturesBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    {title && (
                        <h2 className="text-3xl sm:text-4xl font-bold text-[var(--color-text)] mb-4 font-[family-name:var(--font-heading)]">
                            {title}
                        </h2>
                    )}
                    {subtitle && (
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            {subtitle}
                        </p>
                    )}
                </div>

                <div className={`grid gap-8 ${layout === 'grid'
                    ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                    : 'grid-cols-1'
                    }`}>
                    {features.map((feature, index) => (
                        <FeatureCard key={feature.id || index} feature={feature} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function FeatureCard({ feature }: { feature: FeatureItem }) {
    const IconComponent = feature.icon ? (iconMap[feature.icon.toLowerCase()] || Star) : Star;

    return (
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-8 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300">
            {feature.icon && (
                <div className="w-12 h-12 bg-[var(--color-primary)] rounded-lg flex items-center justify-center mb-4 text-white">
                    <IconComponent size={24} />
                </div>
            )}
            {feature.image && (
                <img
                    src={feature.image}
                    alt={feature.title}
                    className="w-full h-48 object-cover rounded-lg mb-4"
                />
            )}
            <h3 className="text-xl font-semibold text-[var(--color-text)] mb-3">
                {feature.title}
            </h3>
            <p className="text-gray-600 leading-relaxed">
                {feature.description}
            </p>
        </div>
    );
}
