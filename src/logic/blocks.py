from typing import Any, Dict
from src.core.models import Context

class LogicBlocks:
    @staticmethod
    def get_product_name(context: Context) -> str:
        return context.product.name

    @staticmethod
    def format_price(context: Context) -> str:
        return f"{context.product.currency} {context.product.price}"

    @staticmethod
    def get_benefits_list(context: Context) -> list:
        return context.product.benefits

    @staticmethod
    def get_key_features(context: Context) -> list:
        return context.product.key_ingredients

    @staticmethod
    def generate_faq_list(context: Context) -> list:
        # Transform Question objects to simple dicts for JSON output
        return [q.model_dump() for q in context.generated_questions]

    @staticmethod
    def comparison_table(context: Context) -> dict:
        if not context.comparison_analysis:
            return {}
        return context.comparison_analysis.model_dump()

    @staticmethod
    def get_competitor_name(context: Context) -> str:
        return context.competitor_product.name if context.competitor_product else "Generic Brand"

logic_registry = {
    "product_name": LogicBlocks.get_product_name,
    "price_formatted": LogicBlocks.format_price,
    "benefits_list": LogicBlocks.get_benefits_list,
    "ingredients": LogicBlocks.get_key_features,
    "faq_list": LogicBlocks.generate_faq_list,
    "comparison_table": LogicBlocks.comparison_table,
    "competitor_name": LogicBlocks.get_competitor_name
}
