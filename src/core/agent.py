from abc import ABC, abstractmethod
from typing import Any
from .models import Context

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, context: Context) -> Context:
        """
        Process the context and return the updated context.
        """
        pass
