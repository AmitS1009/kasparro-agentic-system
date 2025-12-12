import json
import os
from dotenv import load_dotenv

from src.core.pipeline import Pipeline
from src.core.models import Context
from src.agents.parser import DataParserAgent
from src.agents.strategist import ContentStrategistAgent
from src.agents.writer import ContentWriterAgent

# Load environment variables (API Keys)
load_dotenv()

def main():
    # 1. Setup Input Data (The Only Input)
    raw_data = {
        "Product Name": "GlowBoost Vitamin C Serum",
        "Concentration": "10% Vitamin C",
        "Skin Type": "Oily, Combination",
        "Key Ingredients": "Vitamin C, Hyaluronic Acid",
        "Benefits": "Brightening, Fades dark spots",
        "How to Use": "Apply 2–3 drops in the morning before sunscreen",
        "Side Effects": "Mild tingling for sensitive skin",
        "Price": "₹699"
    }

    print("--- Starting Agentic Content System ---")
    
    # 2. Initialize Agents
    parser = DataParserAgent()
    strategist = ContentStrategistAgent()
    writer = ContentWriterAgent(templates_dir=os.path.abspath("src/templates"))

    # 3. Build Pipeline
    pipeline = Pipeline(agents=[parser, strategist, writer])

    # 4. Run Pipeline
    initial_context = Context(raw_data=raw_data)
    final_context = pipeline.run(initial_context)

    # 5. Output Results
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    print("\n--- Writing Outputs ---")
    for page_name, content in final_context.final_pages.items():
        file_path = os.path.join(output_dir, f"{page_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)
        print(f"[*] Generated: {file_path}")

    print("\n[SUCCESS] Content generation complete.")

if __name__ == "__main__":
    main()
