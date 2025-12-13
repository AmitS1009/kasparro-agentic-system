import unittest
from unittest.mock import MagicMock, patch
import os
from src.core.graph import create_graph
from src.core.models import Question, ProductModel, ComparisonModel, ComparisonPoint

class TestContentPipeline(unittest.TestCase):

    def setUp(self):
        self.raw_data = {
            "Product Name": "TestProduct",
            "Price": "100",
            "Concentration": "10%",
            "Skin Type": "All",
            "Key Ingredients": "Water",
            "Benefits": "Hydration",
            "How to Use": "Apply daily",
            "Side Effects": "None"
        }

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    @patch('src.agents.strategist.ChatOpenAI')
    @patch("src.agents.writer._load_templates")
    def test_pipeline_success(self, mock_load_templates, mock_chat_openai):
        # Mock LLM Responses
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Mock structured output
        mock_structured_llm = MagicMock()
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        
        # Mock Questions Response
        questions_resp = MagicMock()
        questions_resp.questions = [
            Question(category="Cat", question=f"Q{i}", answer=f"A{i}") for i in range(15)
        ]
        
        # Mock Competitor Response
        comp_resp = MagicMock()
        comp_resp.competitor = ProductModel(name="CompB", price=200)
        comp_resp.comparison_points = [ComparisonPoint(feature="Price", product_a_value="100", product_b_value="200", winner="A")]
        
        # Configure side properties for the chain invoke
        # The chain invoke calls llm.invoke
        # but with_structured_output validation happens inside langchain.
        # We need to mock the invoke result of the structured LLM.
        mock_structured_llm.invoke.side_effect = [questions_resp, comp_resp]

        # Mock Templates
        mock_load_templates.return_value = {
            "faq": "FAQ Template",
            "product_page": "Product Page Template",
            "comparison": "Comparison Template"
        }

        app = create_graph()
        result = app.invoke({"raw_data": self.raw_data})

        self.assertIn("product", result)
        self.assertEqual(len(result["generated_questions"]), 15)
        self.assertIn("final_pages", result)
        self.assertIn("faq", result["final_pages"])

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_keys_failure(self):
        app = create_graph()
        with self.assertRaises(ValueError) as context:
            app.invoke({"raw_data": self.raw_data})
        self.assertIn("No API keys found", str(context.exception))

if __name__ == '__main__':
    unittest.main()
