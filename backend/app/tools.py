tools = [
    {
        "type": "function",
        "function": {
            "name": "get_sector_performance",
            "description": "Get performance of all companies in a specific sector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {"type": "string", "description": "The sector name."}
                },
                "required": ["sector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_performance",
            "description": "Get performance of a specific company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "The company name or ID."}
                },
                "required": ["company"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_companies_in_sector",
            "description": "Get all the companies in a sector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {"type": "string", "description": "The sector name."}
                },
                "required": ["sector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_statement_trends",
            "description": "Get trends of a specific financial statement for a specific company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "The company name or ID."},
                    "statement": {"type": "string", "description": "The financial statement name (e.g., balance-sheet, profit-loss, cash-flow)."}
                },
                "required": ["company", "statement"]
            }
        }
    }
]
