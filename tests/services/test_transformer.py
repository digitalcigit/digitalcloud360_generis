"""Tests unitaires pour BriefToSiteTransformer

Ces tests valident la transformation BusinessBrief → SiteDefinition
conformément aux spécifications GEN-7 et au schema GEN-8.
"""

import pytest
from unittest.mock import MagicMock
from app.services.transformer import BriefToSiteTransformer
from app.schemas.site_definition import SiteDefinition, BlockType


class TestBriefToSiteTransformer:
    """Tests pour le Transformer Brief → SiteDefinition"""
    
    @pytest.fixture
    def transformer(self):
        """Instance du transformer"""
        return BriefToSiteTransformer()
    
    @pytest.fixture
    def sample_brief(self):
        """Brief de test minimal"""
        brief = MagicMock()
        brief.business_name = "TechStartup Dakar"
        brief.sector = "technology"
        brief.mission = "Digitaliser les PME africaines avec des solutions innovantes"
        brief.vision = "Leader de la transformation digitale en Afrique de l'Ouest"
        brief.value_proposition = "Solutions tech sur mesure pour PME"
        brief.target_audience = "PME africaines"
        brief.differentiation = "Expertise locale. Prix compétitifs. Support 24/7."
        brief.services = ["Développement Web", "Applications Mobile", "Conseil IT"]
        brief.content_generation = {
            "hero_image": "https://example.com/hero.jpg",
            "theme_colors": {"primary": "#2563eb"},
            "features": [
                {"title": "Innovation", "description": "Technologies de pointe", "icon": "lightbulb"},
                {"title": "Expertise", "description": "15 ans d'expérience", "icon": "award"}
            ]
        }
        brief.logo_creation = {"logo_url": "https://example.com/logo.png"}
        brief.seo_optimization = {"keywords": ["tech", "digital", "afrique"]}
        brief.template_selection = {"template_id": "tech-startup-v2"}
        brief.research_results = {}
        return brief
    
    @pytest.fixture
    def minimal_brief(self):
        """Brief avec données minimales"""
        brief = MagicMock()
        brief.business_name = "Simple Business"
        brief.sector = None
        brief.mission = "Notre mission simple"
        brief.vision = None
        brief.value_proposition = None
        brief.target_audience = None
        brief.differentiation = None
        brief.services = None
        brief.content_generation = None
        brief.logo_creation = None
        brief.seo_optimization = None
        brief.template_selection = None
        brief.research_results = None
        return brief

    # ===== TESTS STRUCTURE =====
    
    def test_transform_returns_valid_structure(self, transformer, sample_brief):
        """Test que transform() retourne une structure avec metadata, theme, pages"""
        result = transformer.transform(sample_brief)
        
        assert "metadata" in result
        assert "theme" in result
        assert "pages" in result
        assert len(result["pages"]) >= 1
    
    def test_transform_with_minimal_brief(self, transformer, minimal_brief):
        """Test transformation avec données minimales"""
        result = transformer.transform(minimal_brief)
        
        assert result["metadata"]["title"] == "Simple Business"
        assert len(result["pages"]) >= 1

    # ===== TESTS METADATA =====
    
    def test_metadata_extraction(self, transformer, sample_brief):
        """Test extraction des métadonnées depuis le brief"""
        result = transformer.transform(sample_brief)
        
        assert result["metadata"]["title"] == "TechStartup Dakar"
        assert "Digitaliser" in result["metadata"]["description"]
        assert result["metadata"]["favicon"] == "https://example.com/logo.png"
        assert result["metadata"]["ogImage"] == "https://example.com/hero.jpg"
    
    def test_metadata_truncates_description(self, transformer, sample_brief):
        """Test que la description est tronquée à 160 caractères"""
        sample_brief.mission = "A" * 200
        result = transformer.transform(sample_brief)
        
        assert len(result["metadata"]["description"]) <= 160

    # ===== TESTS THEME =====
    
    def test_theme_colors_from_brief(self, transformer, sample_brief):
        """Test extraction des couleurs personnalisées depuis content_generation"""
        result = transformer.transform(sample_brief)
        
        assert result["theme"]["colors"]["primary"] == "#2563eb"
    
    def test_theme_colors_sector_defaults(self, transformer, minimal_brief):
        """Test couleurs par défaut quand pas de content_generation"""
        minimal_brief.sector = "restaurant"
        result = transformer.transform(minimal_brief)
        
        # Restaurant sector default is red
        assert result["theme"]["colors"]["primary"] == "#EF4444"
    
    def test_theme_fonts_default(self, transformer, sample_brief):
        """Test polices par défaut"""
        result = transformer.transform(sample_brief)
        
        assert result["theme"]["fonts"]["heading"] == "Inter"
        assert result["theme"]["fonts"]["body"] == "Inter"

    # ===== TESTS SECTIONS =====
    
    def test_home_page_has_required_sections(self, transformer, sample_brief):
        """Test que la homepage contient hero et footer minimum"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        
        section_types = [s["type"] for s in home_page["sections"]]
        assert "hero" in section_types
        assert "footer" in section_types
    
    def test_home_page_has_all_sections(self, transformer, sample_brief):
        """Test que la homepage contient toutes les sections prévues"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        
        section_types = [s["type"] for s in home_page["sections"]]
        assert "hero" in section_types
        assert "about" in section_types
        assert "services" in section_types
        assert "features" in section_types
        assert "contact" in section_types
        assert "footer" in section_types

    # ===== TESTS HERO SECTION =====
    
    def test_hero_section_content(self, transformer, sample_brief):
        """Test contenu de la section Hero"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        hero = next(s for s in home_page["sections"] if s["type"] == "hero")
        
        assert hero["content"]["title"] == sample_brief.value_proposition
        assert hero["content"]["subtitle"] == sample_brief.mission
        assert hero["content"]["image"] == "https://example.com/hero.jpg"
    
    def test_hero_cta_has_link(self, transformer, sample_brief):
        """Test que le CTA hero utilise 'link' (pas 'href') pour alignement GEN-8"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        hero = next(s for s in home_page["sections"] if s["type"] == "hero")
        
        assert "link" in hero["content"]["cta"]
        assert hero["content"]["cta"]["link"] == "#contact"
        # Vérifier qu'on n'utilise pas href
        assert "href" not in hero["content"]["cta"]

    # ===== TESTS ABOUT SECTION =====
    
    def test_about_section_content(self, transformer, sample_brief):
        """Test contenu de la section About"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        about = next(s for s in home_page["sections"] if s["type"] == "about")
        
        assert about["content"]["subtitle"] == "TechStartup Dakar"
        assert about["content"]["mission"] == sample_brief.mission
        assert about["content"]["vision"] == sample_brief.vision

    # ===== TESTS SERVICES SECTION =====
    
    def test_services_section_with_list(self, transformer, sample_brief):
        """Test section services avec liste de strings"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        services = next(s for s in home_page["sections"] if s["type"] == "services")
        
        assert len(services["content"]["services"]) == 3
        assert services["content"]["services"][0]["id"] == "service-1"
        assert services["content"]["services"][0]["title"] == "Développement Web"
    
    def test_services_items_have_id(self, transformer, sample_brief):
        """Test que chaque service a un id unique"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        services = next(s for s in home_page["sections"] if s["type"] == "services")
        
        ids = [s["id"] for s in services["content"]["services"]]
        assert len(ids) == len(set(ids))  # Tous uniques

    # ===== TESTS FEATURES SECTION =====
    
    def test_features_section_from_content_generation(self, transformer, sample_brief):
        """Test features depuis content_generation"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        features = next(s for s in home_page["sections"] if s["type"] == "features")
        
        assert len(features["content"]["features"]) == 2
        assert features["content"]["features"][0]["title"] == "Innovation"
        assert features["content"]["features"][0]["id"] == "feature-1"
    
    def test_features_fallback_from_differentiation(self, transformer, minimal_brief):
        """Test features générées depuis differentiation"""
        minimal_brief.differentiation = "Point 1. Point 2. Point 3."
        result = transformer.transform(minimal_brief)
        home_page = result["pages"][0]
        features = next((s for s in home_page["sections"] if s["type"] == "features"), None)
        
        assert features is not None
        assert len(features["content"]["features"]) == 3

    # ===== TESTS CONTACT SECTION =====
    
    def test_contact_section_has_form_fields(self, transformer, sample_brief):
        """Test que contact a des champs de formulaire"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        contact = next(s for s in home_page["sections"] if s["type"] == "contact")
        
        assert contact["content"]["showForm"] is True
        assert len(contact["content"]["formFields"]) >= 3
        
        field_names = [f["name"] for f in contact["content"]["formFields"]]
        assert "name" in field_names
        assert "email" in field_names
        assert "message" in field_names

    # ===== TESTS FOOTER SECTION =====
    
    def test_footer_section_content(self, transformer, sample_brief):
        """Test contenu de la section Footer"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        footer = next(s for s in home_page["sections"] if s["type"] == "footer")
        
        assert footer["content"]["companyName"] == "TechStartup Dakar"
        assert "TechStartup Dakar" in footer["content"]["copyright"]
        assert footer["content"]["logo"] == "https://example.com/logo.png"
    
    def test_footer_links_use_url(self, transformer, sample_brief):
        """Test que footer links utilisent 'url' (pas 'href') pour alignement GEN-8"""
        result = transformer.transform(sample_brief)
        home_page = result["pages"][0]
        footer = next(s for s in home_page["sections"] if s["type"] == "footer")
        
        for link in footer["content"]["links"]:
            assert "url" in link
            assert "href" not in link

    # ===== TESTS VALIDATION PYDANTIC =====
    
    def test_validates_against_pydantic_schema(self, transformer, sample_brief):
        """Test que l'output est valide selon le schema Pydantic SiteDefinition"""
        result = transformer.transform(sample_brief)
        
        # Doit passer sans erreur de validation
        site = SiteDefinition(**result)
        assert site.metadata.title == "TechStartup Dakar"
        assert len(site.pages) >= 1
    
    def test_validates_minimal_brief(self, transformer, minimal_brief):
        """Test validation Pydantic avec brief minimal"""
        result = transformer.transform(minimal_brief)
        
        # Doit passer sans erreur
        site = SiteDefinition(**result)
        assert site.metadata.title == "Simple Business"

    # ===== TESTS SECTOR MAPPING =====
    
    def test_technology_sector_config(self, transformer, sample_brief):
        """Test configuration secteur technology"""
        sample_brief.sector = "technology"
        sample_brief.content_generation = None  # Force sector defaults
        result = transformer.transform(sample_brief)
        
        # Tech sector uses blue
        assert result["theme"]["colors"]["primary"] == "#3B82F6"
    
    def test_restaurant_sector_config(self, transformer, sample_brief):
        """Test configuration secteur restaurant"""
        sample_brief.sector = "restaurant"
        sample_brief.content_generation = None
        result = transformer.transform(sample_brief)
        
        # Restaurant sector uses red
        assert result["theme"]["colors"]["primary"] == "#EF4444"
    
    def test_health_sector_config(self, transformer, sample_brief):
        """Test configuration secteur health"""
        sample_brief.sector = "health"
        sample_brief.content_generation = None
        result = transformer.transform(sample_brief)
        
        # Health sector uses emerald
        assert result["theme"]["colors"]["primary"] == "#10B981"
