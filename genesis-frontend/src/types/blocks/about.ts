export interface AboutSectionContent {
    title: string;
    subtitle?: string;
    description: string;
    mission?: string;
    vision?: string;
    image?: string;
    stats?: AboutStat[];
}

export interface AboutStat {
    value: string;
    label: string;
}
