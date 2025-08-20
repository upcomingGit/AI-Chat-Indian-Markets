from .base import Agent

class CompanyDisclosuresAgent(Agent):
    NAME = "company_disclosures"

    def can_handle(self, query: str) -> bool:
        print(f"[CompanyDisclosuresAgent] Checking if can handle query: {query}")
        keywords = ["disclosure", "filing", "sec", "regulatory", "prospectus", "company disclosure"]
        q = query.lower()
        result = any(k in q for k in keywords)
        print(f"[CompanyDisclosuresAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[CompanyDisclosuresAgent] Handling query: {query}")
        response = "CompanyDisclosuresAgent response to: " + query
        print(f"[CompanyDisclosuresAgent] Response: {response}")
        return response
