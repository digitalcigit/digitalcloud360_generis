import {
  HeaderSectionContent,
  HeroSectionContent,
  AboutSectionContent,
  ServicesSectionContent,
  FeaturesSectionContent,
  TestimonialsSectionContent,
  ContactSectionContent,
  GallerySectionContent,
  CTASectionContent,
  FooterSectionContent,
  MenuSectionContent
} from './blocks';

// ===== BLOCK TYPES =====
export type BlockType =
  | 'header'
  | 'hero'
  | 'about'
  | 'services'
  | 'features'
  | 'testimonials'
  | 'contact'
  | 'gallery'
  | 'cta'
  | 'footer'
  | 'menu';

// ===== BLOCK CONTENT MAP =====
export interface BlockContentMap {
  header: HeaderSectionContent;
  hero: HeroSectionContent;
  about: AboutSectionContent;
  services: ServicesSectionContent;
  features: FeaturesSectionContent;
  testimonials: TestimonialsSectionContent;
  contact: ContactSectionContent;
  gallery: GallerySectionContent;
  cta: CTASectionContent;
  footer: FooterSectionContent;
  menu: MenuSectionContent;
}

// ===== SECTION GÉNÉRIQUE TYPÉE =====
export interface SiteSectionGeneric<T extends BlockType> {
  id: string;
  type: T;
  content: BlockContentMap[T];
  styles?: SectionStyles;
}

// ===== SITE SECTION UNION (Discriminated Union) =====
export type SiteSection =
  | SiteSectionGeneric<'header'>
  | SiteSectionGeneric<'hero'>
  | SiteSectionGeneric<'about'>
  | SiteSectionGeneric<'services'>
  | SiteSectionGeneric<'features'>
  | SiteSectionGeneric<'testimonials'>
  | SiteSectionGeneric<'contact'>
  | SiteSectionGeneric<'gallery'>
  | SiteSectionGeneric<'cta'>
  | SiteSectionGeneric<'footer'>
  | SiteSectionGeneric<'menu'>;

// ===== STYLES =====
export interface SectionStyles {
  backgroundColor?: string;
  padding?: string;
  margin?: string;
  className?: string;
}

// ===== SITE DEFINITION =====
export interface SiteDefinition {
  metadata: SiteMetadata;
  theme: SiteTheme;
  pages: SitePage[];
}

export interface SiteMetadata {
  title: string;
  description: string;
  favicon?: string;
  ogImage?: string;
}

export interface SiteTheme {
  colors: ThemeColors;
  fonts: ThemeFonts;
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent?: string;
  background: string;
  text: string;
}

export interface ThemeFonts {
  heading: string;
  body: string;
  accent?: string;
}

export interface SitePage {
  id: string;
  slug: string;
  title: string;
  sections: SiteSection[];
}

// ===== IMPORTS DES BLOCK CONTENTS =====
export * from './blocks';
