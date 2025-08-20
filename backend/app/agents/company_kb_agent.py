from .base import Agent

class CompanyKBAgent(Agent):
    NAME = "company_kb"

    def can_handle(self, query: str) -> bool:
        print(f"[CompanyKBAgent] Checking if can handle query: {query}")
        keywords = ["company profile", "about the company", "headquarters", "sector", "industry", "founder", "employees"]
        q = query.lower()
        result = any(k in q for k in keywords)
        print(f"[CompanyKBAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[CompanyKBAgent] Handling query: {query}")
        response = "CompanyKBAgent response to: " + query
        print(f"[CompanyKBAgent] Response: {response}")
        return response
