from .base import Agent

class ConferenceCallAgent(Agent):
    def can_handle(self, query: str) -> bool:
        print(f"[ConferenceCallAgent] Checking if can handle query: {query}")
        result = "conference call" in query.lower()
        print(f"[ConferenceCallAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[ConferenceCallAgent] Handling query: {query}")
        # Your conference call logic here
        response = "ConferenceCallAgent response to: " + query
        print(f"[ConferenceCallAgent] Response: {response}")
        return response