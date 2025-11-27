interface Feature {
    title: string;
    description: string;
    icon?: string;
}

interface FeaturesBlockProps {
    title?: string;
    features: Feature[];
}

export default function FeaturesBlock({ title, features }: FeaturesBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                {title && (
                    <h2 className="text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-12">
                        {title}
                    </h2>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            className="bg-gradient-to-br from-gray-50 to-gray-100 p-8 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300"
                        >
                            {feature.icon && (
                                <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                                    <span className="text-2xl text-white">⭐</span>
                                </div>
                            )}
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 leading-relaxed">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
