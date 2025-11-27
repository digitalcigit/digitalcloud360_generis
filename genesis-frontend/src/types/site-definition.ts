export interface SiteDefinition {
  metadata: {
    title: string;
    description: string;
    favicon?: string;
  };
  theme: {
    colors: {
      primary: string;
      secondary: string;
      background: string;
      text: string;
    };
    fonts: {
      heading: string;
      body: string;
    };
  };
  pages: SitePage[];
}

export interface SitePage {
  id: string;
  slug: string;
  title: string;
  sections: SiteSection[];
}

export interface SiteSection {
  id: string;
  type: string;
  content: Record<string, any>;
  styles?: Record<string, any>;
}
