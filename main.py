import json
import os
import sys
from dotenv import load_dotenv

from src.core.graph import create_graph

# Load environment variables (API Keys)
load_dotenv()

def main():
    # 1. Setup Input Data
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

    print("--- Starting Agentic Content System (LangGraph) ---")
    
    # 2. Build Graph
    app = create_graph()

    # 3. Process Input
    initial_state = {"raw_data": raw_data}
    
    try:
        final_state = app.invoke(initial_state)

        # 4. Output Results
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        print("\n--- Writing Outputs ---")
        pages = final_state.get("final_pages", {})
        for page_name, content in pages.items():
            file_path = os.path.join(output_dir, f"{page_name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
            print(f"[*] Generated: {file_path}")

        print("\n[SUCCESS] Content generation complete.")

    except Exception as e:
        print(f"\n[ERROR] Pipeline Failed: {e}")
        # Explicitly exit with error code for CI/CD checks
        sys.exit(1)

if __name__ == "__main__":
    main()
