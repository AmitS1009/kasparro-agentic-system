from typing import List
from .agent import BaseAgent
from .models import Context

class Pipeline:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, initial_context: Context) -> Context:
        context = initial_context
        for agent in self.agents:
            print(f"[*] Running Agent: {agent.name}...")
            try:
                context = agent.process(context)
            except Exception as e:
                print(f"[!] Error in {agent.name}: {e}")
                raise e
        return context
