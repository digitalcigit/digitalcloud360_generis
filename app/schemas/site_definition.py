"""SiteDefinition Pydantic schemas - Miroir des types TypeScript frontend"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union
from enum import Enum


# ===== BLOCK TYPES =====
class BlockType(str, Enum):
    HEADER = "header"
    HERO = "hero"
    ABOUT = "about"
    SERVICES = "services"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    CONTACT = "contact"
    GALLERY = "gallery"
    CTA = "cta"
    FOOTER = "footer"


# ===== HEADER =====
class NavItem(BaseModel):
    label: str
    href: str
    children: Optional[List["NavItem"]] = None


class HeaderCTA(BaseModel):
    text: str
    href: str
    variant: Optional[Literal["primary", "secondary", "outline"]] = "primary"


class HeaderSectionContent(BaseModel):
    logo: Optional[str] = None
    companyName: str = Field(..., description="Nom de l'entreprise")
    navigation: List[NavItem]
    ctaButton: Optional[HeaderCTA] = None
    sticky: Optional[bool] = False


# ===== HERO =====
# ⚠️ IMPORTANT: Aligné sur HeroBlock.tsx existant
class HeroCTA(BaseModel):
    text: str
    link: str  # Aligné sur HeroBlock.tsx (pas href)
    variant: Optional[Literal["primary", "secondary", "outline"]] = "primary"


class HeroSectionContent(BaseModel):
    title: str = Field(..., description="Titre principal du hero")  # Aligné sur HeroBlock.tsx
    subtitle: Optional[str] = None  # Aligné sur HeroBlock.tsx
    description: Optional[str] = None
    image: Optional[str] = None  # Aligné sur HeroBlock.tsx (pas backgroundImage)
    backgroundVideo: Optional[str] = None
    cta: Optional[HeroCTA] = None  # Single object, aligné sur HeroBlock.tsx
    alignment: Optional[Literal["left", "center", "right"]] = "center"
    overlay: Optional[bool] = False


# ===== ABOUT =====
class AboutStat(BaseModel):
    value: str
    label: str


class AboutSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section À propos")
    subtitle: Optional[str] = None
    description: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    image: Optional[str] = None
    stats: Optional[List[AboutStat]] = None


# ===== SERVICES =====
class ServiceItem(BaseModel):
    id: str
    title: str
    description: str
    icon: Optional[str] = None
    image: Optional[str] = None
    price: Optional[str] = None
    href: Optional[str] = None


class ServicesSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Services")
    subtitle: Optional[str] = None
    services: List[ServiceItem]
    layout: Optional[Literal["grid", "list", "cards"]] = "grid"


# ===== FEATURES =====
class FeatureItem(BaseModel):
    id: str
    title: str
    description: str
    icon: Optional[str] = None
    image: Optional[str] = None


class FeaturesSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Features")
    subtitle: Optional[str] = None
    features: List[FeatureItem]
    layout: Optional[Literal["grid", "alternating", "centered"]] = "grid"


# ===== TESTIMONIALS =====
class TestimonialItem(BaseModel):
    id: str
    quote: str
    author: str
    role: Optional[str] = None
    company: Optional[str] = None
    avatar: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class TestimonialsSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Testimonials")
    subtitle: Optional[str] = None
    testimonials: List[TestimonialItem]
    layout: Optional[Literal["carousel", "grid", "masonry"]] = "grid"


# ===== CONTACT =====
class ContactAddress(BaseModel):
    street: str
    city: str
    country: str
    postalCode: Optional[str] = None


class SocialLink(BaseModel):
    platform: Literal["facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok"]
    url: str


class ContactFormField(BaseModel):
    name: str
    type: Literal["text", "email", "tel", "textarea"]
    label: str
    required: Optional[bool] = False
    placeholder: Optional[str] = None


class ContactSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Contact")
    subtitle: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[ContactAddress] = None
    socialLinks: Optional[List[SocialLink]] = None
    showForm: Optional[bool] = True
    formFields: Optional[List[ContactFormField]] = None
    mapEmbed: Optional[str] = None


# ===== GALLERY =====
class GalleryImage(BaseModel):
    id: str
    src: str
    alt: str
    caption: Optional[str] = None
    href: Optional[str] = None


class GallerySectionContent(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    images: List[GalleryImage]
    layout: Optional[Literal["grid", "masonry", "carousel"]] = "grid"
    columns: Optional[Literal[2, 3, 4]] = 3


# ===== CTA =====
class CTAButton(BaseModel):
    text: str
    href: str
    variant: Optional[Literal["primary", "secondary", "outline"]] = "primary"


class CTASectionContent(BaseModel):
    headline: str = Field(..., description="Titre du CTA")
    description: Optional[str] = None
    primaryButton: CTAButton
    secondaryButton: Optional[CTAButton] = None
    backgroundColor: Optional[str] = None
    backgroundImage: Optional[str] = None


# ===== FOOTER =====
# ⚠️ IMPORTANT: Aligné sur FooterBlock.tsx existant
class FooterLink(BaseModel):
    text: str
    url: str  # Aligné sur FooterBlock.tsx (pas href)


class FooterColumn(BaseModel):
    title: str
    links: List[FooterLink]


class FooterSectionContent(BaseModel):
    logo: Optional[str] = None
    companyName: Optional[str] = None  # Optional pour compatibilité
    description: Optional[str] = None
    columns: Optional[List[FooterColumn]] = None
    copyright: str = Field(..., description="Copyright text")  # Required, aligné sur FooterBlock.tsx
    socialLinks: Optional[List[SocialLink]] = None
    links: Optional[List[FooterLink]] = None  # Aligné sur FooterBlock.tsx (pas legalLinks)


# ===== SECTION CONTENT UNION =====
SectionContent = Union[
    HeaderSectionContent,
    HeroSectionContent,
    AboutSectionContent,
    ServicesSectionContent,
    FeaturesSectionContent,
    TestimonialsSectionContent,
    ContactSectionContent,
    GallerySectionContent,
    CTASectionContent,
    FooterSectionContent
]


# ===== SITE SECTION =====
class SectionStyles(BaseModel):
    backgroundColor: Optional[str] = None
    padding: Optional[str] = None
    margin: Optional[str] = None
    className: Optional[str] = None


class SiteSection(BaseModel):
    id: str
    type: BlockType
    content: SectionContent
    styles: Optional[SectionStyles] = None


# ===== SITE STRUCTURE =====
class SiteMetadata(BaseModel):
    title: str = Field(..., description="Titre du site")
    description: str = Field(..., description="Meta description")
    favicon: Optional[str] = None
    ogImage: Optional[str] = None


class ThemeColors(BaseModel):
    primary: str = Field(..., description="Couleur primaire (hex)")
    secondary: str = Field(..., description="Couleur secondaire (hex)")
    accent: Optional[str] = None
    background: str = "#ffffff"
    text: str = "#1a1a1a"


class ThemeFonts(BaseModel):
    heading: str = "Inter"
    body: str = "Inter"


class SiteTheme(BaseModel):
    colors: ThemeColors
    fonts: ThemeFonts


class SitePage(BaseModel):
    id: str
    slug: str = Field(..., description="URL slug de la page (ex: / pour homepage)")
    title: str
    sections: List[SiteSection]


class SiteDefinition(BaseModel):
    """Schema complet d'un site généré par Genesis AI"""
    metadata: SiteMetadata
    theme: SiteTheme
    pages: List[SitePage]
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "title": "TechStartup Dakar",
                    "description": "Solutions tech pour PME africaines"
                },
                "theme": {
                    "colors": {
                        "primary": "#2563eb",
                        "secondary": "#7c3aed",
                        "background": "#ffffff",
                        "text": "#1a1a1a"
                    },
                    "fonts": {"heading": "Inter", "body": "Inter"}
                },
                "pages": [{
                    "id": "home",
                    "slug": "/",
                    "title": "Accueil",
                    "sections": []
                }]
            }
        }
