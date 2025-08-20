from .base import Agent

class MarketDataAgent(Agent):
    NAME = "market_data"

    def can_handle(self, query: str) -> bool:
        print(f"[MarketDataAgent] Checking if can handle query: {query}")
        keywords = ["price", "market", "quote", "ticker", "volume", "market data"]
        q = query.lower()
        result = any(k in q for k in keywords)
        print(f"[MarketDataAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[MarketDataAgent] Handling query: {query}")
        response = "MarketDataAgent response to: " + query
        print(f"[MarketDataAgent] Response: {response}")
        return response
