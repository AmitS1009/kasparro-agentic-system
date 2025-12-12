from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ProductModel(BaseModel):
    name: str
    price: float
    currency: str = "INR"
    description: Optional[str] = None
    concentration: Optional[str] = None
    skin_type: List[str] = Field(default_factory=list)
    key_ingredients: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    how_to_use: Optional[str] = None
    side_effects: Optional[str] = None

class Question(BaseModel):
    category: str
    question: str
    answer: Optional[str] = None

class ComparisonPoint(BaseModel):
    feature: str
    product_a_value: str
    product_b_value: str
    winner: Optional[str] = None # "A", "B", or "Tie"

class ComparisonModel(BaseModel):
    competitor_name: str
    points: List[ComparisonPoint]

class Context(BaseModel):
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    product: Optional[ProductModel] = None
    generated_questions: List[Question] = Field(default_factory=list)
    competitor_product: Optional[ProductModel] = None
    comparison_analysis: Optional[ComparisonModel] = None
    final_pages: Dict[str, Any] = Field(default_factory=dict)
