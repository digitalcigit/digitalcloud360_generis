"""Tests unitaires pour SiteDefinition schema"""

import pytest
from app.schemas.site_definition import (
    SiteDefinition,
    SiteSection,
    SitePage,
    BlockType,
    HeroSectionContent,
    FooterSectionContent,
    TestimonialItem,
)


class TestSiteDefinitionSchema:
    """Tests pour SiteDefinition"""
    
    def test_site_definition_valid(self):
        """Test création SiteDefinition valide"""
        data = {
            "metadata": {
                "title": "Test Site",
                "description": "Test description"
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
        site = SiteDefinition(**data)
        assert site.metadata.title == "Test Site"
        assert len(site.pages) == 1

    def test_hero_section_content(self):
        """Test HeroSectionContent avec props alignées sur HeroBlock.tsx"""
        hero = HeroSectionContent(
            title="Bienvenue",
            subtitle="Description courte",
            image="https://example.com/hero.jpg",
            cta={"text": "En savoir plus", "link": "/about"}
        )
        assert hero.title == "Bienvenue"
        assert hero.cta.link == "/about"

    def test_footer_section_content(self):
        """Test FooterSectionContent avec props alignées sur FooterBlock.tsx"""
        footer = FooterSectionContent(
            copyright="© 2025 Company",
            links=[{"text": "Privacy", "url": "/privacy"}]
        )
        assert footer.copyright == "© 2025 Company"
        assert footer.links[0].url == "/privacy"

    def test_testimonial_rating_validation(self):
        """Test que rating doit être entre 1 et 5"""
        # Valid
        valid = TestimonialItem(id="1", quote="Great!", author="John", rating=5)
        assert valid.rating == 5
        
        # Invalid - should raise
        with pytest.raises(ValueError):
            TestimonialItem(id="2", quote="Bad", author="Jane", rating=6)
        
        with pytest.raises(ValueError):
            TestimonialItem(id="3", quote="Bad", author="Jane", rating=0)

    def test_page_with_empty_sections(self):
        """Test qu'une page sans sections est valide"""
        page = SitePage(id="empty", slug="/empty", title="Empty", sections=[])
        assert len(page.sections) == 0
