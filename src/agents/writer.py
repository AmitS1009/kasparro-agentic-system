import json
import os
import re
from typing import Dict, Any
from src.core.state import AgentState
from src.core.models import Context
from src.logic.blocks import logic_registry

def node_write_content(state: AgentState) -> dict:
    # Shim state to Context for logic blocks
    # We can safely assume state has all fields populated by previous nodes
    context = Context(**state)
    
    # Load templates
    templates_dir = os.path.abspath("src/templates")
    templates = _load_templates(templates_dir)
    
    # Process each page type
    final_pages = {}
    final_pages['faq'] = _render(templates.get('faq'), context)
    final_pages['product_page'] = _render(templates.get('product_page'), context)
    final_pages['comparison'] = _render(templates.get('comparison'), context)
    
    return {"final_pages": final_pages}

def _load_templates(templates_dir: str) -> Dict[str, Any]:
    templates = {}
    if not os.path.exists(templates_dir):
        # Fallback or error - let's just warn or return empty.
        print(f"[!] Warning: Templates dir not found: {templates_dir}")
        return {}

    for filename in os.listdir(templates_dir):
        if filename.endswith(".json"):
            name = filename.replace(".json", "")
            with open(os.path.join(templates_dir, filename), 'r') as f:
                templates[name] = json.load(f)
    return templates

def _render(template: Any, context: Context) -> Any:
    if isinstance(template, dict):
        return {k: _render(v, context) for k, v in template.items()}
    elif isinstance(template, list):
        return [_render(i, context) for i in template]
    elif isinstance(template, str):
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
