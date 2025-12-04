export interface HeaderSectionContent {
    logo?: string;
    companyName: string;
    navigation: NavItem[];
    ctaButton?: HeaderCTA;
    sticky?: boolean;
}

export interface NavItem {
    label: string;
    href: string;
    children?: NavItem[];
}

export interface HeaderCTA {
    text: string;
    href: string;
    variant?: 'primary' | 'secondary' | 'outline';
}
