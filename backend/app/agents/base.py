from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Return True if this agent can handle the query."""
        pass

    @abstractmethod
    def handle(self, query: str) -> str:
        """Process the query and return a response."""
        pass