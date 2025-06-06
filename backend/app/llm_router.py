"""
llm_router.py
Router for handling LLM-based chat for Indian financial markets.
"""

# --- Imports ---
import os
import json
from fastapi import APIRouter, Request
from openai import OpenAI
from google import genai
from google.genai import types
from google.genai.types import FunctionDeclaration
from dotenv import load_dotenv

from app.tools import tools
from app.services.financial_data import (
    get_sector_performance,
    get_company_performance,
    get_companies_in_sector,
    get_company_statement_trends
)

# --- Configuration & Setup ---
load_dotenv(dotenv_path="app/.env")

router = APIRouter()
client = OpenAI()
client_google = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))

# --- Constants & Mappings ---
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

USE_GEMINI = False  # Set to True to use Gemini, False for OpenAI

# --- Helper Functions ---
def convert_openai_tools_to_gemini(tools_openai):
    """
    Convert OpenAI-style tool definitions to Gemini FunctionDeclaration objects.
    """
    gemini_tools = []
    for tool in tools_openai:
        if tool.get("type") == "function":
            fn = tool["function"]
            gemini_tools.append(
                FunctionDeclaration(
                    name=fn["name"],
                    description=fn.get("description", ""),
                    parameters=fn.get("parameters", {})
                )
            )
    print(f"gemini_tools converted: {gemini_tools}")
    return gemini_tools

def map_sector(user_input):
    """Normalize and map user input to sector name."""
    key = user_input.strip().lower()
    return SECTOR_MAP.get(key)

# --- Main Chat Endpoint ---
@router.post("/")
async def chat(request: Request):
    """
    Main chat endpoint for handling user queries with LLM and tool integration.
    """
    body = await request.json()
    user_query = body.get("query")
    print(f"Received user query: {user_query}")

    supported_sectors = ", ".join(sorted(SECTOR_MAP.values()))
    supported_companies = ", ".join(sorted(COMPANIES_MAP.values()))
    supported_financial_statements = ", ".join(sorted(FINANCIAL_STATEMENTS.values()))
    system_prompt = (
        f"You are a helpful assistant for Indian financial markets. "
        f"The supported sectors are: {supported_sectors}. "
        f"The supported companies are: {supported_companies}. "
        f"The supported financial statements are: {supported_financial_statements}. "
        f"If the user query matches a supported function, use the appropriate tool/function call."
        f"If the user asks for a sector or company or financial statement not in this list, respond appropriately with 'Sector or Company or Financial Statement Not Found. Please specify a supported sector or company or financial statement'. "
        f"Mention the supported sectors, companies, and financial statements in your response to the user query. "
        f"Respond in markdown format for better readability. Use bullet points, headers, newline, tabs and bold text where appropriate. Provide spacing and formatting to enhance readability. "
    )

    if USE_GEMINI:
        config_google = types.GenerateContentConfig(
            system_instruction=system_prompt,
            maxOutputTokens=3000,
            tools=convert_openai_tools_to_gemini(tools)
        )
        first_response = client_google.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            config=config_google,
            contents=user_query
        )
        msg = first_response.candidates[0].content.parts[0].text
        print(f"Gemini response: {msg}")

        tools_to_use = first_response.candidates[0].content.parts[0].function_call
        if tools_to_use:
            print(f"Tool calls detected: {tools_to_use.name}")
            tool_call = tools_to_use
            fn_name = tool_call.name
            args = json.loads(tool_call.args)

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
            # Step 3: Send result back to Gemini for final answer
            second_response = client_google.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                config=config_google,
                contents=[user_query, json.dumps(result)]
            )
            print(f"Final response after tool call: {second_response.candidates[0].content.parts[0].text}")
            return {"response": second_response.candidates[0].content.parts[0].text}
        else:
            print("No tool calls detected in the response.")
            return {"response": msg}
    else:
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
        else:
            print("No tool calls detected in the response.")
            return {"response": msg.content}
