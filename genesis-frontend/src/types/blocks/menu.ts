export interface MenuSectionContent {
    title: string;
    subtitle?: string;
    categories: MenuCategory[];
    currency?: string;
}

export interface MenuCategory {
    id: string;
    title: string;
    items: MenuItem[];
}

export interface MenuItem {
    title: string;
    description?: string;
    price: string | number;
    image?: string;
    isHighlight?: boolean; // For "Chef's Choice" etc.
    dietary?: string[]; // e.g. ['vegan', 'gluten-free']
}
