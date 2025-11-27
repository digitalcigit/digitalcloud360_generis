interface HeroBlockProps {
    title: string;
    subtitle: string;
    image?: string;
    cta?: {
        text: string;
        link: string;
    };
}

export default function HeroBlock({ title, subtitle, image, cta }: HeroBlockProps) {
    return (
        <section className="relative bg-gradient-to-br from-blue-50 to-indigo-100 py-20 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    <div className="space-y-6">
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                            {title}
                        </h1>
                        <p className="text-xl text-gray-600 leading-relaxed">
                            {subtitle}
                        </p>
                        {cta && (
                            <a
                                href={cta.link}
                                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl"
                            >
                                {cta.text}
                            </a>
                        )}
                    </div>
                    {image && (
                        <div className="relative h-96 rounded-2xl overflow-hidden shadow-2xl">
                            <img
                                src={image}
                                alt={title}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
