"""
Content Sub-Agent - Génération Contenu Multilingue

Spécialisé pour l'Afrique francophone avec:
- Génération contenu site web complet
- Adaptation culturelle contexte local
- Support multilingue (français + langues locales)
- Optimisation mobile-first
- Ton chaleureux valeurs africaines
"""

import asyncio
import json
import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.providers.factory import ProviderFactory
from app.core.providers.base import BaseLLMProvider
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)


class ContentSubAgent:
    """
    Sous-agent génération contenu multilingue adapté culture africaine.
    
    Utilise l'architecture multi-provider pour:
    - Génération contenu (Deepseek primary, OpenAI fallback)
    - Traduction/adaptation langues locales
    """
    
    def __init__(self):
        """Initialise le sub-agent avec providers configurés"""
        self.provider_factory = ProviderFactory()
        
        # Provider LLM primary (Deepseek pour contenu)
        self.llm_provider: BaseLLMProvider = self.provider_factory.get_llm_provider(
            provider_name="deepseek",
            fallback=True
        )
        
        # Langues locales supportées
        self.supported_languages = {
            'fr': 'français',
            'wo': 'wolof',
            'bm': 'bambara',
            'ha': 'hausa',
            'sw': 'swahili',
            'lg': 'lingala',
            'ff': 'fulfulde'
        }
        
        # Templates de contenu par section
        self.content_templates = {
            'homepage': 'Hero section + proposition valeur',
            'about': 'Histoire + mission + valeurs',
            'services': 'Services/produits détaillés',
            'contact': 'Coordonnées + formulaire contact'
        }
        
        logger.info("ContentSubAgent initialized with multi-provider architecture")
    
    async def generate_website_content(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération contenu site web complet adapté culture locale.
        
        Args:
            business_brief: Brief business contenant:
                - business_name: Nom entreprise
                - industry_sector: Secteur activité
                - vision: Vision entreprise
                - mission: Mission entreprise
                - target_market: Marché cible
                - services: Liste services
                - competitive_advantage: Avantage concurrentiel
                - location: {country, city, region}
                - differentiation: Différenciation (optionnel)
                - value_proposition: Proposition valeur (optionnel)
                
        Returns:
            Dict contenant:
                - homepage: Contenu page accueil
                - about: Contenu page à propos
                - services: Contenu page services
                - contact: Contenu page contact
                - seo_metadata: Métadonnées SEO
                - languages_generated: Langues générées
                - content_strategy: Stratégie contenu
        """
        
        logger.info(
            "Generating website content",
            business=business_brief.get('business_name'),
            sector=business_brief.get('industry_sector'),
            location=business_brief.get('location')
        )
        
        try:
            # Détermination langues cibles selon localisation
            target_languages = self._determine_target_languages(business_brief)
            
            # Génération parallèle tous contenus (français primary)
            content_tasks = [
                self._generate_homepage_content(business_brief, target_languages),
                self._generate_about_content(business_brief, target_languages),
                self._generate_services_content(business_brief, target_languages),
                self._generate_contact_content(business_brief, target_languages),
                self._generate_seo_metadata(business_brief, target_languages)
            ]
            
            content_results = await asyncio.gather(*content_tasks, return_exceptions=True)
            
            # Filtrer erreurs
            valid_results = []
            errors = []
            for i, result in enumerate(content_results):
                if isinstance(result, Exception):
                    logger.warning(f"Content generation task {i} failed", error=str(result))
                    errors.append({'task_index': i, 'error': str(result)})
                    valid_results.append({})  # Placeholder vide
                else:
                    valid_results.append(result)
            
            logger.info(
                "Website content generated successfully",
                languages=target_languages,
                errors_count=len(errors)
            )
            
            return {
                'homepage': valid_results[0] if len(valid_results) > 0 else {},
                'about': valid_results[1] if len(valid_results) > 1 else {},
                'services': valid_results[2] if len(valid_results) > 2 else {},
                'contact': valid_results[3] if len(valid_results) > 3 else {},
                'seo_metadata': valid_results[4] if len(valid_results) > 4 else {},
                'languages_generated': target_languages,
                'content_strategy': await self._generate_content_strategy(business_brief),
                'generation_metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'sections_generated': len([r for r in valid_results if r]),
                    'errors': errors if errors else None
                }
            }
            
        except Exception as e:
            logger.error("Website content generation failed", error=str(e), exc_info=True)
            # Fallback gracieux
            return await self._fallback_content(business_brief)
    
    def _determine_target_languages(self, business_brief: Dict[str, Any]) -> List[str]:
        """
        Détermination langues cibles selon localisation business.
        
        Args:
            business_brief: Brief business
            
        Returns:
            Liste codes langues ISO 639-1
        """
        location = business_brief.get('location', {})
        country = location.get('country', '').lower()
        
        # Mapping pays -> langues locales prioritaires
        country_languages = {
            'sénégal': ['fr', 'wo'],
            'mali': ['fr', 'bm'],
            'burkina faso': ['fr', 'bm'],
            'niger': ['fr', 'ha'],
            'côte d\'ivoire': ['fr'],
            'côte d'ivoire': ['fr'],
            'bénin': ['fr'],
            'togo': ['fr'],
            'cameroun': ['fr'],
            'gabon': ['fr'],
            'congo': ['fr', 'lg'],
            'rdc': ['fr', 'lg', 'sw'],
            'kenya': ['fr', 'sw'],
            'tanzanie': ['fr', 'sw'],
            'guinée': ['fr', 'ff']
        }
        
        languages = country_languages.get(country, ['fr'])
        
        logger.info(f"Target languages for {country}: {languages}")
        
        return languages
    
    async def _generate_homepage_content(
        self, 
        brief: Dict[str, Any], 
        languages: List[str]
    ) -> Dict[str, Any]:
        """
        Génération page d'accueil avec approche culturelle adaptée.
        
        Args:
            brief: Brief business
            languages: Langues cibles
            
        Returns:
            Dict avec contenu homepage structuré
        """
        location = brief.get('location', {})
        
        generation_prompt = f"""
GÉNÉRATION PAGE D'ACCUEIL PROFESSIONNELLE - CONTEXTE AFRICAIN

BUSINESS BRIEF:
- Nom: {brief.get('business_name', 'Mon Business')}
- Secteur: {brief.get('industry_sector', 'Services')}
- Vision: {brief.get('vision', 'Vision à définir')}
- Mission: {brief.get('mission', 'Mission à définir')}
- Marché cible: {brief.get('target_market', 'Clientèle générale')}
- Avantage concurrentiel: {brief.get('competitive_advantage', 'Service qualité')}
- Services: {', '.join(brief.get('services', ['Service 1', 'Service 2']))}
- Localisation: {location.get('city', '')}, {location.get('country', '')}

DIRECTIVES STYLE ET TON:
1. Ton CHALEUREUX et PROCHE (valeurs africaines: communauté, famille, ubuntu)
2. Références culturelles SUBTILES et pertinentes au contexte local
3. Call-to-action MOBILE-FIRST (90% trafic mobile Afrique)
4. Crédibilité et CONFIANCE (crucial marchés émergents)
5. Accessibilité PRIX si pertinent (sensibilité prix élevée)
6. Éviter jargon technique complexe
7. Emphase sur RELATIONS HUMAINES et SERVICE PERSONNALISÉ

FORMAT JSON STRICT ATTENDU:
{{
    "hero_section": {{
        "title": "Titre accrocheur max 60 caractères captant attention immédiate",
        "subtitle": "Sous-titre explicatif max 120 caractères détaillant bénéfice principal",
        "hero_paragraph": "Paragraphe émotionnel 2-3 phrases créant connexion",
        "primary_cta": "Appel action principal (ex: Contactez-nous, Commencez maintenant)",
        "secondary_cta": "Appel action secondaire (ex: En savoir plus, Découvrir nos services)"
    }},
    "value_proposition": {{
        "main_value": "Proposition valeur principale unique 1 phrase",
        "benefits": [
            "Bénéfice client concret 1",
            "Bénéfice client concret 2",
            "Bénéfice client concret 3"
        ],
        "why_choose_us": "Raison choisir notre entreprise 2-3 phrases"
    }},
    "trust_elements": {{
        "social_proof": "Élément preuve sociale (ex: +500 clients satisfaits)",
        "credentials": "Crédibilité/certifications/expérience",
        "guarantee": "Garantie ou engagement client clair"
    }},
    "services_teaser": {{
        "intro": "Introduction services 1 phrase",
        "highlights": [
            "Service phare 1 avec bénéfice",
            "Service phare 2 avec bénéfice",
            "Service phare 3 avec bénéfice"
        ]
    }},
    "cultural_adaptation": {{
        "local_references": "Références culturelles subtiles intégrées",
        "community_focus": "Accent communauté/valeurs locales",
        "language_tone": "Description ton utilisé et pourquoi adapté"
    }}
}}

GÉNÉRER CONTENU MAINTENANT (RÉPONDRE UNIQUEMENT JSON):
"""
        
        system_message = """Tu es un expert copywriter spécialisé dans le marketing digital africain francophone avec 12 ans d'expérience. Tu maîtrises parfaitement l'adaptation culturelle, les codes locaux, et crées du contenu qui résonne émotionnellement avec les audiences africaines. Tu produis un contenu authentique, chaleureux, et orienté résultats. RÉPONDS TOUJOURS EN JSON VALIDE."""
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=generation_prompt,
                system_message=system_message,
                response_schema={
                    "hero_section": "object",
                    "value_proposition": "object",
                    "trust_elements": "object",
                    "services_teaser": "object",
                    "cultural_adaptation": "object"
                },
                temperature=0.7,  # Créativité modérée
                max_tokens=1500
            )
            
            # Ajout metadata
            response['section_type'] = 'homepage'
            response['generated_at'] = datetime.utcnow().isoformat()
            
            return response
            
        except Exception as e:
            logger.error("Homepage content generation failed", error=str(e))
            return await self._fallback_homepage(brief)
    
    async def _generate_about_content(
        self, 
        brief: Dict[str, Any], 
        languages: List[str]
    ) -> Dict[str, Any]:
        """Génération page À propos avec storytelling"""
        
        generation_prompt = f"""
GÉNÉRATION PAGE À PROPOS - STORYTELLING AUTHENTIQUE AFRICAIN

CONTEXTE:
- Entreprise: {brief.get('business_name')}
- Secteur: {brief.get('industry_sector')}
- Vision: {brief.get('vision')}
- Mission: {brief.get('mission')}
- Différenciation: {brief.get('differentiation', brief.get('competitive_advantage', ''))}

DIRECTIVES:
1. Raconter HISTOIRE authentique et inspirante
2. Mettre en avant VALEURS humaines
3. Créer CONNEXION émotionnelle
4. Montrer IMPACT communauté locale
5. Ton personnel et accessible

FORMAT JSON:
{{
    "story": {{
        "opening": "Paragraphe ouverture captivant",
        "journey": "Histoire parcours entreprise 2-3 paragraphes",
        "mission_statement": "Énoncé mission clair"
    }},
    "values": [
        {{"value": "Valeur 1", "description": "Explication"}},
        {{"value": "Valeur 2", "description": "Explication"}},
        {{"value": "Valeur 3", "description": "Explication"}}
    ],
    "team_intro": "Introduction équipe si applicable",
    "community_impact": "Impact communauté locale",
    "call_to_action": "Invitation rejoindre aventure"
}}
"""
        
        system_message = "Expert storytelling africain créant récits authentiques et inspirants. RÉPONDS EN JSON."
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=generation_prompt,
                system_message=system_message,
                response_schema={
                    "story": "object",
                    "values": "array",
                    "community_impact": "string",
                    "call_to_action": "string"
                },
                temperature=0.75,
                max_tokens=1200
            )
            
            response['section_type'] = 'about'
            return response
            
        except Exception as e:
            logger.error("About content generation failed", error=str(e))
            return await self._fallback_about(brief)
    
    async def _generate_services_content(
        self, 
        brief: Dict[str, Any], 
        languages: List[str]
    ) -> Dict[str, Any]:
        """Génération page Services détaillée"""
        
        services_list = brief.get('services', [])
        
        generation_prompt = f"""
GÉNÉRATION PAGE SERVICES - DÉTAIL ET CLARTÉ

SERVICES À PRÉSENTER:
{json.dumps(services_list, ensure_ascii=False, indent=2)}

CONTEXTE BUSINESS:
- Entreprise: {brief.get('business_name')}
- Secteur: {brief.get('industry_sector')}
- Avantage: {brief.get('competitive_advantage')}

DIRECTIVES:
1. Décrire CHAQUE service clairement
2. Mettre en avant BÉNÉFICES clients concrets
3. Inclure cas d'usage si pertinent
4. Prix ou fourchette si approprié
5. Call-to-action par service

FORMAT JSON:
{{
    "services": [
        {{
            "name": "Nom service",
            "description": "Description détaillée 2-3 phrases",
            "benefits": ["Bénéfice 1", "Bénéfice 2"],
            "use_cases": ["Cas usage 1", "Cas usage 2"],
            "pricing_info": "Info tarifaire ou 'Sur devis'",
            "cta": "Appel action spécifique"
        }}
    ],
    "service_approach": "Approche globale services",
    "guarantees": "Garanties ou engagements qualité"
}}
"""
        
        system_message = "Expert description services B2C/B2B Afrique. Clarté et persuasion. RÉPONDS JSON."
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=generation_prompt,
                system_message=system_message,
                response_schema={
                    "services": "array",
                    "service_approach": "string",
                    "guarantees": "string"
                },
                temperature=0.6,
                max_tokens=1500
            )
            
            response['section_type'] = 'services'
            return response
            
        except Exception as e:
            logger.error("Services content generation failed", error=str(e))
            return await self._fallback_services(brief)
    
    async def _generate_contact_content(
        self, 
        brief: Dict[str, Any], 
        languages: List[str]
    ) -> Dict[str, Any]:
        """Génération page Contact avec éléments locaux"""
        
        location = brief.get('location', {})
        
        contact_data = {
            "section_title": "Contactez-nous",
            "intro_message": f"Nous sommes à {location.get('city', 'votre service')} pour vous accompagner.",
            "contact_methods": [
                {
                    "type": "Téléphone",
                    "value": "À compléter",
                    "icon": "phone",
                    "preferred": True
                },
                {
                    "type": "Email",
                    "value": "contact@" + brief.get('business_name', 'entreprise').lower().replace(' ', '') + ".com",
                    "icon": "email",
                    "preferred": False
                },
                {
                    "type": "WhatsApp",
                    "value": "À compléter",
                    "icon": "whatsapp",
                    "preferred": True  # Important Afrique
                }
            ],
            "location_info": {
                "city": location.get('city', ''),
                "country": location.get('country', ''),
                "region": location.get('region', ''),
                "address": "À compléter"
            },
            "business_hours": "À définir selon secteur",
            "form_fields": [
                "Nom complet",
                "Téléphone (préféré)",
                "Email",
                "Message"
            ],
            "cta_submit": "Envoyer le message",
            "response_promise": "Nous vous répondons sous 24h",
            "section_type": "contact"
        }
        
        return contact_data
    
    async def _generate_seo_metadata(
        self, 
        brief: Dict[str, Any], 
        languages: List[str]
    ) -> Dict[str, Any]:
        """Génération métadonnées SEO optimisées local"""
        
        location = brief.get('location', {})
        business_name = brief.get('business_name', 'Entreprise')
        sector = brief.get('industry_sector', 'Services')
        city = location.get('city', '')
        country = location.get('country', '')
        
        seo_metadata = {
            "meta_title": f"{business_name} - {sector} {city} | {country}",
            "meta_description": f"Découvrez {business_name}, votre partenaire {sector} à {city}. {brief.get('value_proposition', brief.get('mission', 'Service de qualité'))}",
            "keywords": [
                sector.lower(),
                f"{sector} {city}".lower(),
                f"{sector} {country}".lower(),
                business_name.lower(),
                brief.get('target_market', '').lower()
            ],
            "og_title": f"{business_name} | {sector} {city}",
            "og_description": brief.get('vision', f"{business_name} - {sector} à {city}"),
            "og_type": "website",
            "twitter_card": "summary_large_image",
            "canonical_url": f"https://{business_name.lower().replace(' ', '')}.com",
            "section_type": "seo_metadata"
        }
        
        return seo_metadata
    
    async def _generate_content_strategy(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Génération stratégie contenu globale"""
        
        return {
            "tone_of_voice": "Chaleureux, proche, professionnel accessible",
            "key_themes": [
                "Confiance et proximité",
                "Expertise locale",
                "Service personnalisé",
                "Impact communautaire"
            ],
            "content_pillars": [
                "Expertise sectorielle",
                "Témoignages clients",
                "Actualités secteur",
                "Conseils pratiques"
            ],
            "engagement_tactics": [
                "Call-to-action WhatsApp (canal préféré Afrique)",
                "Formulaires mobiles simplifiés",
                "Preuves sociales locales",
                "Garanties rassurantes"
            ],
            "cultural_considerations": [
                "Valeurs communautaires",
                "Relations humaines avant technologie",
                "Accessibilité financière",
                "Confiance par recommandation"
            ]
        }
    
    async def _fallback_content(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Contenu fallback si génération échoue"""
        
        logger.warning("Using fallback content generation")
        
        business_name = brief.get('business_name', 'Notre Entreprise')
        sector = brief.get('industry_sector', 'Services')
        
        return {
            'homepage': await self._fallback_homepage(brief),
            'about': await self._fallback_about(brief),
            'services': await self._fallback_services(brief),
            'contact': await self._generate_contact_content(brief, ['fr']),
            'seo_metadata': await self._generate_seo_metadata(brief, ['fr']),
            'languages_generated': ['fr'],
            'content_strategy': await self._generate_content_strategy(brief),
            'fallback_mode': True
        }
    
    async def _fallback_homepage(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Homepage fallback"""
        
        business_name = brief.get('business_name', 'Notre Entreprise')
        vision = brief.get('vision', f"Votre partenaire {brief.get('industry_sector', 'de confiance')}")
        
        return {
            "hero_section": {
                "title": f"Bienvenue chez {business_name}",
                "subtitle": vision,
                "hero_paragraph": f"{business_name} vous accompagne avec professionnalisme et proximité.",
                "primary_cta": "Contactez-nous",
                "secondary_cta": "En savoir plus"
            },
            "value_proposition": {
                "main_value": brief.get('competitive_advantage', 'Service de qualité personnalisé'),
                "benefits": [
                    "Expertise locale reconnue",
                    "Service client réactif",
                    "Solutions adaptées à vos besoins"
                ]
            },
            "trust_elements": {
                "social_proof": "Des clients satisfaits",
                "credentials": "Expérience et professionnalisme",
                "guarantee": "Votre satisfaction, notre priorité"
            },
            "fallback_mode": True
        }
    
    async def _fallback_about(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """About fallback"""
        
        return {
            "story": {
                "opening": f"{brief.get('business_name')} est né de la volonté de répondre aux besoins du marché local.",
                "mission_statement": brief.get('mission', 'Servir nos clients avec excellence')
            },
            "values": [
                {"value": "Excellence", "description": "Qualité dans tout ce que nous faisons"},
                {"value": "Proximité", "description": "À l'écoute de nos clients"},
                {"value": "Intégrité", "description": "Confiance et transparence"}
            ],
            "community_impact": "Nous contribuons au développement de notre communauté",
            "fallback_mode": True
        }
    
    async def _fallback_services(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Services fallback"""
        
        services = brief.get('services', ['Service 1', 'Service 2', 'Service 3'])
        
        return {
            "services": [
                {
                    "name": service,
                    "description": f"Service professionnel de qualité",
                    "benefits": ["Qualité garantie", "Prix compétitif"],
                    "cta": "Demander un devis"
                }
                for service in services[:5]
            ],
            "service_approach": "Approche personnalisée selon vos besoins",
            "fallback_mode": True
        }
