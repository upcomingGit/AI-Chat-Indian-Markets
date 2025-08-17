tools = [
    {
        "type": "function",
        "function": {
            "name": "get_companies_with_conference_calls",
            "description": "List companies that have conference call transcripts available, with metadata.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_conference_call_details",
            "description": "Get conference call periods (fiscal year and quarter) available for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "integer", "description": "The numeric ID of the company."}
                },
                "required": ["company_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_conference_call_summary",
            "description": "Get the summary of a specific conference call for a company (by fiscal year and quarter).",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "integer", "description": "The numeric ID of the company."},
                    "fiscal_year": {"type": "integer", "description": "The fiscal year (e.g., 2025)."},
                    "fiscal_quarter": {"type": "integer", "description": "The fiscal quarter (1-4)."}
                },
                "required": ["company_id", "fiscal_year", "fiscal_quarter"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "conference_call_qa",
            "description": "Ask a question about a specific conference call and retrieve top-k relevant chunks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "integer", "description": "The numeric ID of the company."},
                    "fiscal_year": {"type": "integer", "description": "The fiscal year (e.g., 2025)."},
                    "fiscal_quarter": {"type": "integer", "description": "The fiscal quarter (1-4)."},
                    "question": {"type": "string", "description": "The user question about the conference call."},
                    "k": {"type": "integer", "description": "Number of top results to return (default 3)."}
                },
                "required": ["company_id", "fiscal_year", "fiscal_quarter", "question"]
            }
        }
    }
]
