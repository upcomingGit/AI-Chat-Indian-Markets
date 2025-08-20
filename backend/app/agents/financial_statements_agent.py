from .base import Agent

class FinancialStatementsAgent(Agent):
    NAME = "financial_statements"

    def can_handle(self, query: str) -> bool:
        print(f"[FinancialStatementsAgent] Checking if can handle query: {query}")
        keywords = ["financial statement", "balance sheet", "income statement", "profit", "loss", "cash flow"]
        q = query.lower()
        result = any(k in q for k in keywords)
        print(f"[FinancialStatementsAgent] can_handle result: {result}")
        return result

    def handle(self, query: str) -> str:
        print(f"[FinancialStatementsAgent] Handling query: {query}")
        response = "FinancialStatementsAgent response to: " + query
        print(f"[FinancialStatementsAgent] Response: {response}")
        return response
