
import sys
import os

# Add app to path
sys.path.append('c:\\genesis')

from app.services.sector_mappings import get_sector_config

sectors_to_test = [
    "Restaurant / Alimentation",
    "restaurant",
    "Technology",
    "default",
    None,
    ""
]

for s in sectors_to_test:
    config = get_sector_config(s)
    print(f"Sector '{s}' -> Variant: {config.get('theme_variant', 'N/A')}, Colors: {config.get('default_colors', {}).get('primary')}")
