export interface CTASectionContent {
    headline: string;
    description?: string;
    primaryButton: CTAButton;
    secondaryButton?: CTAButton;
    backgroundColor?: string;
    backgroundImage?: string;
}

export interface CTAButton {
    text: string;
    href: string;
    variant?: 'primary' | 'secondary' | 'outline';
}
