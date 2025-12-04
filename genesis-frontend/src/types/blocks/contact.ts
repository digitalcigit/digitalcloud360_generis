export interface ContactSectionContent {
    title: string;
    subtitle?: string;
    description?: string;
    email?: string;
    phone?: string;
    address?: ContactAddress;
    socialLinks?: SocialLink[];
    showForm?: boolean;
    formFields?: ContactFormField[];
    mapEmbed?: string;
}

export interface ContactAddress {
    street: string;
    city: string;
    country: string;
    postalCode?: string;
}

export interface SocialLink {
    platform: 'facebook' | 'twitter' | 'instagram' | 'linkedin' | 'youtube' | 'tiktok';
    url: string;
}

export interface ContactFormField {
    name: string;
    type: 'text' | 'email' | 'tel' | 'textarea';
    label: string;
    required?: boolean;
    placeholder?: string;
}
