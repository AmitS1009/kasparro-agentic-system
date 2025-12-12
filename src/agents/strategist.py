import os
import json
from typing import List
from src.core.agent import BaseAgent
from src.core.models import Context, Question, ProductModel, ComparisonModel, ComparisonPoint
from openai import OpenAI
import google.generativeai as genai

class ContentStrategistAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentStrategistAgent")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        self.provider = "none"
        if self.openai_key:
            self.provider = "openai"
            self.client = OpenAI(api_key=self.openai_key)
        elif self.gemini_key:
            self.provider = "gemini"
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process(self, context: Context) -> Context:
        if self.provider == "openai":
            print("   [+] Using OpenAI for strategy generation...")
            context = self._generate_with_llm_openai(context)
        elif self.provider == "gemini":
            print("   [+] Using Gemini for strategy generation...")
            context = self._generate_with_llm_gemini(context)
        else:
            print("   [!] No API Key found. Using heuristic/mock strategy generation...")
            context = self._generate_mock(context)
        return context

    def _generate_mock(self, context: Context) -> Context:
        # 1. Generate Questions
        # Hardcoding 15 questions for the assignment requirements if no LLM
        p_name = context.product.name
        qs = [
            Question(category="Usage", question=f"How often should I use {p_name}?", answer="Daily, in the morning."),
            Question(category="Usage", question="Can I use it with Retinol?", answer="It's best to alternate them."),
            Question(category="Safety", question="Is it safe for pregnancy?", answer="Consult your doctor, but generally Vitamin C is safe."),
            Question(category="Safety", question="Will it cause breakouts?", answer="It is non-comedogenic."),
            Question(category="Ingredients", question="What is the concentration?", answer=f"{context.product.concentration}"),
            Question(category="Ingredients", question="Is it vegan?", answer="Yes, cruelty-free and vegan."),
            Question(category="Benefits", question="How long to see results?", answer="Typically 4-6 weeks."),
            Question(category="Benefits", question="Does it clear acne scars?", answer="It helps fade hyperpigmentation."),
            Question(category="Purchase", question="What is the shelf life?", answer="12 months after opening."),
            Question(category="Purchase", question="Do you ship internationally?", answer="Yes, we ship worldwide."),
            Question(category="Usage", question="Can I apply makeup after?", answer="Yes, let it absorb first."),
            Question(category="Usage", question="Do I need sunscreen?", answer="Yes, always use SPF."),
            Question(category="Comparison", question="Is this better than creams?", answer="Serums penetrate deeper."),
            Question(category="Skin Type", question="Is it good for dry skin?", answer="Yes, if paired with a moisturizer."),
            Question(category="General", question="What does it smell like?", answer="Citrusy and fresh.")
        ]
        context.generated_questions = qs

        # 2. Generate Competitor
        comp = ProductModel(
            name="Generic Vitamin C Serum",
            price=499,
            currency="INR",
            concentration="5% Vitamin C",
            skin_type=["All"],
            key_ingredients=["Vitamin C", "Glycerin"],
            benefits=["Hydration"],
            description="A basic serum."
        )
        context.competitor_product = comp
        
        # 3. Generate Comparison Points
        context.comparison_analysis = ComparisonModel(
            competitor_name=comp.name,
            points=[
                ComparisonPoint(feature="Concentration", product_a_value=context.product.concentration, product_b_value=comp.concentration, winner="A"),
                ComparisonPoint(feature="Price", product_a_value=f"{context.product.price}", product_b_value=f"{comp.price}", winner="B"),
                ComparisonPoint(feature="Ingredients", product_a_value=", ".join(context.product.key_ingredients), product_b_value=", ".join(comp.key_ingredients), winner="A"),
            ]
        )

        return context

    def _generate_with_llm_openai(self, context: Context) -> Context:
        product_json = context.product.model_dump_json()
        
        # Prompt for Questions
        prompt_q = f"""
        You are a content strategist. Given the following product data, generate 15 distinct FAQ questions across categories (Usage, Safety, Benefits, Purchase).
        Product: {product_json}
        
        Return a valid JSON array of objects with keys: "category", "question", "answer". 
        Make the answers helpful and based on the product data provided.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_q}],
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            # Handle potential wrapper keys
            items = data.get("questions", data.get("items", []))
            context.generated_questions = [Question(**i) for i in items]
        except Exception as e:
            print(f"Error generating questions (OpenAI): {e}")
            self._generate_mock(context) # Fallback

        # Prompt for Competitor & Analysis
        prompt_c = f"""
        Create a fictional competitor product ("Product B") similar to the input product but slightly inferior or different.
        Then compare them.
        Product A: {product_json}
        
        Return JSON with keys:
        "competitor": {{ ...ProductModel fields... }},
        "comparison_points": [ {{ "feature": "...", "product_a_value": "...", "product_b_value": "...", "winner": "A|B|Tie" }} ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_c}],
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            self._parse_comparison_response(data, context)

        except Exception as e:
            print(f"Error generating comparison (OpenAI): {e}")
            if not context.competitor_product:
                self._generate_mock(context)

        return context

    def _generate_with_llm_gemini(self, context: Context) -> Context:
        product_json = context.product.model_dump_json()
        
        prompt_q = f"""
        You are a content strategist. Given the following product data, generate 15 distinct FAQ questions across categories (Usage, Safety, Benefits, Purchase).
        Product: {product_json}
        
        Return a valid JSON object with a key "questions" containing an array of objects with keys: "category", "question", "answer".
        Ensure the output is pure JSON without markdown code fences.
        """
        
        try:
            model = self.model
            response = model.generate_content(prompt_q, generation_config={"response_mime_type": "application/json"})
            data = json.loads(response.text)
            items = data.get("questions", data.get("items", []))
            context.generated_questions = [Question(**i) for i in items]
        except Exception as e:
            print(f"Error generating questions (Gemini): {e}")
            self._generate_mock(context)

        prompt_c = f"""
        Create a fictional competitor product ("Product B") similar to the input product but slightly inferior or different.
        Then compare them.
        Product A: {product_json}
        
        Return JSON with keys:
        "competitor": {{ ...ProductModel fields... }},
        "comparison_points": [ {{ "feature": "...", "product_a_value": "...", "product_b_value": "...", "winner": "A|B|Tie" }} ]
        Ensure the output is pure JSON without markdown code fences.
        """
        
        try:
            model = self.model
            response = model.generate_content(prompt_c, generation_config={"response_mime_type": "application/json"})
            data = json.loads(response.text)
            self._parse_comparison_response(data, context)
        except Exception as e:
            print(f"Error generating comparison (Gemini): {e}")
            if not context.competitor_product:
                self._generate_mock(context)

        return context

    def _parse_comparison_response(self, data: dict, context: Context):
        # Helper to safely create ProductModel from partial LLM data
        c_data = data.get("competitor", {})
        try:
            context.competitor_product = ProductModel(**c_data)
        except:
             # Fallback implementation if LLM messes up fields
            context.competitor_product = ProductModel(name="Competitor X", price=500, description="A basic alternative.")

        points = data.get("comparison_points", [])
        context.comparison_analysis = ComparisonModel(
            competitor_name=context.competitor_product.name,
            points=[ComparisonPoint(**p) for p in points]
        )
