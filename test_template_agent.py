"""Test script for TemplateAgent Phase 2 Premium"""
import asyncio
from app.core.agents.template import TemplateAgent

async def test():
    agent = TemplateAgent()
    result = await agent.run(
        business_name="Chez Maman Afrique",
        industry_sector="restaurant",
        brand_personality="elegant",
        target_audience="familles africaines"
    )
    print("=== THEME GENERE ===")
    print(f"Template: {result.get('template_name')}")
    theme = result.get("theme", {})
    colors = theme.get("colors", {})
    print(f"Couleurs: primary={colors.get('primary')}, secondary={colors.get('secondary')}, accent={colors.get('accent')}")
    fonts = theme.get("fonts", {})
    print(f"Fonts: heading={fonts.get('heading')}, body={fonts.get('body')}")
    style = theme.get("style", {})
    print(f"Style: {style.get('visual_style')}, radius={style.get('border_radius')}, shadows={style.get('shadows')}")
    rationale = theme.get("design_rationale", "")
    print(f"Rationale: {rationale[:100]}..." if len(rationale) > 100 else f"Rationale: {rationale}")
    print(f"AI Generated: {result.get('metadata', {}).get('ai_generated', False)}")

if __name__ == "__main__":
    asyncio.run(test())
