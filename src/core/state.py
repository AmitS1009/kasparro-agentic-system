from typing import TypedDict, Optional, List, Dict, Any
from src.core.models import ProductModel, Question, ComparisonModel

class AgentState(TypedDict):
    raw_data: Dict[str, Any]
    product: Optional[ProductModel]
    generated_questions: List[Question]
    competitor_product: Optional[ProductModel]
    comparison_analysis: Optional[ComparisonModel]
    final_pages: Dict[str, Any]
