interface FooterLink {
    text: string;
    url: string;
}

interface FooterBlockProps {
    copyright: string;
    links?: FooterLink[];
}

export default function FooterBlock({ copyright, links }: FooterBlockProps) {
    return (
        <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
                    <p className="text-gray-400">{copyright}</p>
                    {links && links.length > 0 && (
                        <nav className="flex space-x-6">
                            {links.map((link, index) => (
                                <a
                                    key={index}
                                    href={link.url}
                                    className="text-gray-400 hover:text-white transition-colors duration-200"
                                >
                                    {link.text}
                                </a>
                            ))}
                        </nav>
                    )}
                </div>
            </div>
        </footer>
    );
}
