from .base import Agent

class NewsAgent(Agent):
    NAME = "news"

    def can_handle(self, query: str) -> bool:
        print(f"[NewsAgent] Checking if can handle query: {query}")
        keywords = ["news", "press", "announcement", "reported", "article"]
        q = query.lower()
        result = any(k in q for k in keywords)
        print(f"[NewsAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[NewsAgent] Handling query: {query}")
        response = "NewsAgent response to: " + query
        print(f"[NewsAgent] Response: {response}")
        return response
