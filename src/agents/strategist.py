import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.core.state import AgentState
from src.core.models import Context, Question, ProductModel, ComparisonModel, ComparisonPoint

# --- Output Schemas for LLM ---
class FAQOutput(BaseModel):
    questions: List[Question] = Field(..., description="List of at least 15 FAQ questions.")

class ComparisonOutput(BaseModel):
    competitor: ProductModel
    comparison_points: List[ComparisonPoint]

# --- Node Function ---
def node_strategize_content(state: AgentState) -> dict:
    # 1. Select Provider
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    llm = None
    if openai_key:
        print("   [+] Using OpenAI for strategy generation...")
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
    elif gemini_key:
        print("   [+] Using Gemini for strategy generation...")
        # Fallback to 'gemini-flash-latest' to avoid 404s on strict versions and reduce 429s (hopefully)
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=gemini_key)
    else:
        # STRICT RULE: NO MOCKS. Fail if no keys.
        raise ValueError("CRITICAL FAIURE: No API keys found (OPENAI_API_KEY or GEMINI_API_KEY). Cannot proceed with content generation.")

    product = state["product"]
    if not product:
         raise ValueError("Product data missing in state.")

    # 2. Generate Questions (with validation)
    print("   [+] Generating FAQs (Strict: >= 15 questions)...")
    
    faq_llm = llm.with_structured_output(FAQOutput)
    
    prompt_q = ChatPromptTemplate.from_messages([
        ("system", "You are a content strategist. You MUST generate at least 15 distinct FAQ questions."),
        ("human", "Product Data: {product_json}\nGenerate 15+ FAQs across Usage, Safety, Benefits, Purchase.")
    ])
    
    # Retry loop for length validation
    generated_qs = []
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chain_q = prompt_q | faq_llm
            result_q = chain_q.invoke({"product_json": product.model_dump_json()})
            
            if len(result_q.questions) >= 15:
                generated_qs = result_q.questions
                break
            else:
                print(f"   [!] Validation Failed: Generated {len(result_q.questions)} questions. Retrying ({attempt+1}/{max_retries})...")
        except Exception as e:
             print(f"   [!] LLM Call Failed: {e}")
             if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                 print("   [!] Quota exceeded. Sleeping for 30s...")
                 time.sleep(30) # Backoff for free tier limits
    
    if len(generated_qs) < 15:
        # Final Strict Check
        raise ValueError(f"FAILED: Could not generate 15 valid questions after {max_retries} attempts. Got {len(generated_qs)}.")

    # 3. Generate Competitor & Analysis
    print("   [+] Generating Competitor Analysis...")
    comp_llm = llm.with_structured_output(ComparisonOutput)
    
    prompt_c = ChatPromptTemplate.from_messages([
        ("system", "You are a market analyst. Create a realistic competitor and compare."),
        ("human", "Product: {product_json}\nCreate a competitor 'Product B' and comparison points.")
    ])
    
    chain_c = prompt_c | comp_llm
    result_c = chain_c.invoke({"product_json": product.model_dump_json()})

    # Construct ComparisonModel
    comp_analysis = ComparisonModel(
        competitor_name=result_c.competitor.name,
        points=result_c.comparison_points
    )

    return {
        "generated_questions": generated_qs,
        "competitor_product": result_c.competitor,
        "comparison_analysis": comp_analysis
    }

