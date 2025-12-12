import re
from typing import List
from src.core.agent import BaseAgent
from src.core.models import Context, ProductModel

class DataParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataParserAgent")

    def process(self, context: Context) -> Context:
        raw = context.raw_data
        
        # Helper to clean price
        price_raw = raw.get("Price", "0")
        price_val = float(re.sub(r"[^\d.]", "", str(price_raw))) if price_raw else 0.0

        # Helper to split lists (comma or newline separated)
        def parse_list(val):
            if isinstance(val, list): return val
            if not val: return []
            return [x.strip() for x in re.split(r",|\n", str(val)) if x.strip()]

        product = ProductModel(
            name=raw.get("Product Name", "Unknown Product"),
            price=price_val,
            currency="INR" if "₹" in str(raw.get("Price", "")) else "USD",
            description=f"A {raw.get('Concentration', '')} formula for {raw.get('Skin Type', 'all skin types')}.", # Synthetic desc logic
            concentration=raw.get("Concentration"),
            skin_type=parse_list(raw.get("Skin Type")),
            key_ingredients=parse_list(raw.get("Key Ingredients")),
            benefits=parse_list(raw.get("Benefits")),
            how_to_use=raw.get("How to Use"),
            side_effects=raw.get("Side Effects")
        )

        context.product = product
        return context
