import json
import os
from typing import Dict, Any
from src.core.agent import BaseAgent
from src.core.models import Context
from src.logic.blocks import logic_registry

class ContentWriterAgent(BaseAgent):
    def __init__(self, templates_dir: str):
        super().__init__("ContentWriterAgent")
        self.templates_dir = templates_dir

    def process(self, context: Context) -> Context:
        # Load templates
        templates = self._load_templates()
        
        # Process each page type
        context.final_pages['faq'] = self._render(templates.get('faq'), context)
        context.final_pages['product_page'] = self._render(templates.get('product_page'), context)
        context.final_pages['comparison'] = self._render(templates.get('comparison'), context)
        
        return context

    def _load_templates(self) -> Dict[str, Any]:
        templates = {}
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                name = filename.replace(".json", "")
                with open(os.path.join(self.templates_dir, filename), 'r') as f:
                    templates[name] = json.load(f)
        return templates

    def _render(self, template: Any, context: Context) -> Any:
        import re
        if isinstance(template, dict):
            return {k: self._render(v, context) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._render(i, context) for i in template]
        elif isinstance(template, str):
            # 1. Exact match (returns Any, e.g. list/dict from logic block)
            if template.startswith("{logic.") and template.endswith("}"):
                # Check if it is a single block without other text
                # We want to perform exact replacement if the type is not string
                # logic is basically: if it matches the pattern exactly, return the result
                # but we need to check if there are other characters.
                # simpler: just use regex, and if the result is not a string, return it directly?
                # No, regex replace returns a string. 
                # If we need non-string return (like a list), we must detect the exact match case.
                pass 

            # Detect pattern {logic.xxx}
            pattern = r"\{logic\.([a-zA-Z0-9_]+)\}"
            matches = re.findall(pattern, template)
            
            if not matches:
                return template
            
            # Case 1: Single block, entire string is the block -> preserve type (could be list/dict)
            if len(matches) == 1 and template == f"{{logic.{matches[0]}}}":
                func = logic_registry.get(matches[0])
                return func(context) if func else f"MISSING:{matches[0]}"

            # Case 2: String interpolation -> result is always a string
            def replace(match):
                block_name = match.group(1)
                func = logic_registry.get(block_name)
                if func:
                    val = func(context)
                    return str(val) # Force string conversion
                return f"MISSING:{block_name}"
            
            return re.sub(pattern, replace, template)
            
        else:
            return template
