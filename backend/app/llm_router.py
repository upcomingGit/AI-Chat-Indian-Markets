from fastapi import APIRouter, Request
from openai import OpenAI
from app.tools import tools
from app.services.financial_data import (
    get_sector_performance,
    get_company_performance,
    get_companies_in_sector,
    get_company_statement_trends
)
import json
from dotenv import load_dotenv
import os

print("Loading environment variables from app/.env...")
load_dotenv(dotenv_path="app/.env")
print("Environment variables loaded.")

router = APIRouter()
print("APIRouter initialized.")

client = OpenAI()
print("OpenAI client initialized.")
load_dotenv(dotenv_path="app/.env")
router = APIRouter()
client = OpenAI()

# Example sector mapping (expand as needed)
SECTOR_MAP = {
    "airlines": "Air Transport Services",
    "ceramics": "Ceramic Products",
    "hotels": "Hotels & Restaurants",
    "pharmaceuticals": "Pharmaceuticals",
    "healthcare": "Healthcare",
    # Add more mappings as needed
}
COMPANIES_MAP = {
    "cera": "CERA",
    "indigo": "INDIGO",
    "indian hotels": "INDHOTEL",
    "narayana hrudayalaya": "NH",
    "caplin point": "CAPLIPOINT",
    # Add more mappings as needed
}

FINANCIAL_STATEMENTS = {
    "Balance Sheet": "balance-sheet",
    "Profit & Loss": "profit-loss",
    "Cash Flow": "cash-flow"
    # Add more mappings as needed
}

def map_sector(user_input):
    # Normalize input for matching
    key = user_input.strip().lower()
    return SECTOR_MAP.get(key)  # returns None if not found

@router.post("/")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("query")
    print(f"Received user query: {user_query}")
    # Step 1: Send user query to GPT-4o with tools
    supported_sectors = ", ".join(sorted(SECTOR_MAP.values()))
    supported_companies = ", ".join(sorted(COMPANIES_MAP.values()))
    supported_financial_statements = ", ".join(sorted(FINANCIAL_STATEMENTS.values()))
    system_prompt = (
        f"You are a helpful assistant for Indian financial markets. "
        f"The supported sectors are: {supported_sectors}. "
        f"The supported companies are: {supported_companies}. "
        f"The supported financial statements are: {supported_financial_statements}. "
        f"If the user asks for a sector or company or financial statement not in this list, respond appropriately with 'Sector or Company or Financial Statement Not Found. Please specify a supported sector or company or financial statement'."
        f"Mention the supported sectors, companies, and financial statements in your response to the user query."
        f"Respond in markdown format for better readability. Use bullet points, headers, newline, tabs and bold text where appropriate. Provide spacing and formatting to enhance readability. "
    )
    first_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        tools=tools,
        tool_choice="auto"
    )

    msg = first_response.choices[0].message
    print(f"GPT-4o response: {msg.content}")
    # Step 2: If tool is requested, call it
    if msg.tool_calls:
        print(f"Tool calls detected: {msg.tool_calls}")
        tool_call = msg.tool_calls[0]
        fn_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if fn_name == "get_sector_performance":
            sector = map_sector(args["sector"])
            result = get_sector_performance(sector)
        elif fn_name == "get_company_performance":
            result = get_company_performance(args["company"])
        elif fn_name == "get_companies_in_sector":
            sector = map_sector(args["sector"])
            result = get_companies_in_sector(sector)
        elif fn_name == "get_company_statement_trends":
            result = get_company_statement_trends(args["company"], args["statement"])
        else:
            result = {"error": f"Unknown tool function: {fn_name}"}
        print(f"Tool result: {result}")
        # Step 3: Send result back to GPT-4o for final answer
        second_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": user_query},
                {"role": "assistant", "tool_calls": msg.tool_calls},
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(result)
                }
            ]
        )
        print(f"Final response after tool call: {second_response.choices[0].message.content}")
        return {"response": second_response.choices[0].message.content}

    # Else: No tool used, just return first LLM output
    return {"response": msg.content}
