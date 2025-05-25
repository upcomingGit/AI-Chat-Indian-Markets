tools = [
    {
        "type": "function",
        "function": {
            "name": "get_historical_financials",
            "description": "Get past financial data for a given sector",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {"type": "string"},
                    "years": {"type": "integer"}
                },
                "required": ["sector", "years"]
            }
        }
    }
]
