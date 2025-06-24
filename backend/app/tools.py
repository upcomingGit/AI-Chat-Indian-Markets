tools = [
    {
        "type": "function",
        "function": {
            "name": "get_company_data",
            "description": "Get all historical financial data for a company across all financial statements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "string", "description": "The ID of the company."}
                },
                "required": ["company_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_data_from_financials",
            "description": "Get all historical financial data for a company based on selected financial statement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "string", "description": "The ID of the company."},
                    "statement_name": {"type": "string", "description": "The financial statement name from which data is needed."}
                },
                "required": ["company_id", "statement_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_data_from_financial_parameter",
            "description": "Get all historical financial data for a company based on selected financial statement and specific parameter in that financial statement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "string", "description": "The ID of the company."},
                    "statement_name": {"type": "string", "description": "The financial statement name from which data is needed."},
                    "parameter": {"type": "string", "description": "The financial parameter to retrieve."}
                },
                "required": ["company_id", "statement_name", "parameter"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_companies_in_sector",
            "description": "Get all companies in a sector.",
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
            "name": "get_financials_in_sector",
            "description": "Get the financials for all the companies in a specific sector.",
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
            "name": "get_all_company_conference_calls",
            "description": "Get all conference call transcripts for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "string", "description": "The ID of the company."}
                },
                "required": ["company_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_conference_call_period",
            "description": "Get conference call transcripts for a company for a specific time period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "string", "description": "The ID of the company."},
                    "time_period": {"type": "string", "description": "The time period of the conference call."}
                },
                "required": ["company_id", "time_period"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_chunks",
            "description": "Search for top-k similar text chunks based on a user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query by the user."},
                    "k": {"type": "integer", "description": "The number of top results to return."},
                    "company_name": {"type": "string", "description": "The company name."},
                    "statement_type": {"type": "string", "description": "The statement type."},
                    "time_period": {"type": "string", "description": "The time period."}
                },
                "required": ["query", "k", "company_name", "statement_type", "time_period"]
            }
        }
    }
]
