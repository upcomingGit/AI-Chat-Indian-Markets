"""
llm_router.py
Router for handling LLM-based chat for Indian financial markets with OpenAI and Gemini support.
"""

# --- Imports ---
import os
import json
from fastapi import APIRouter, Request
from openai import OpenAI
from dotenv import load_dotenv

from google import genai
from google.genai import types

from app.tools import tools
from app.services.financial_data import (
    get_company_data,
    get_company_data_from_financials,
    get_company_data_from_financial_parameter,
    get_companies_in_sector,
    get_financials_in_sector,
    get_all_company_conference_calls,
    get_company_conference_call_period,
    search_chunks
)

# --- Configuration & Setup ---
print("[llm_router] Loading environment variables...")
load_dotenv(dotenv_path="app/.env")

router = APIRouter()
openai_client = OpenAI()
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Constants & Mappings ---
SECTOR_MAP = {
    "airline": "Airline",
    "sanitary ware": "Sanitary Ware",
    "hotels": "Hotels & Resorts",
    "pharmaceuticals": "Pharmaceuticals",
    "hospital": "Hospital",
}

COMPANIES_MAP = {
    "cera": "CERA",
    "indigo": "INDIGO",
    "indian hotels": "INDHOTEL",
    "narayana hrudayalaya": "NH",
    "caplin point": "CAPLIPOINT",
}

FINANCIAL_STATEMENTS = {
    "Balance Sheet": "balance-sheet",
    "Profit & Loss": "profit-loss",
    "Cash Flow": "cash-flow",
    "Conference Call": "Conference Call",
}

USE_GEMINI = False  # Set to True to use Gemini, False to use OpenAI
LATEST_TIME_PERIOD = "Q4FY25"  # Default time period for conference calls

# Simple in-memory store for chat history (keyed by user/session)
chat_histories = {}

def get_chat_history(session_id):
    return chat_histories.get(session_id, [])

def add_to_chat_history(session_id, message):
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append(message)

# --- Helpers ---
def map_sector(user_input):
    print(f"[llm_router] Mapping sector input: {user_input}")
    return SECTOR_MAP.get(user_input.strip().lower())

def get_function_result(fn_name, args):
    print(f"[llm_router] Calling function: {fn_name} with args: {args}")
    # Remove debug return to allow actual function dispatch
    if fn_name == "get_company_data":
        return get_company_data(args["company_id"])
    elif fn_name == "get_company_data_from_financials":
        return get_company_data_from_financials(args["company_id"], args["statement_name"])
    elif fn_name == "get_company_data_from_financial_parameter":
        return get_company_data_from_financial_parameter(args["company_id"], args["statement_name"], args["parameter"])
    elif fn_name == "get_companies_in_sector":
        return get_companies_in_sector(map_sector(args["sector"]))
    elif fn_name == "get_financials_in_sector":
        return get_financials_in_sector(map_sector(args["sector"]))
    elif fn_name == "get_all_company_conference_calls":
        return get_all_company_conference_calls(args["company_id"])
    elif fn_name == "get_company_conference_call_period":
        return get_company_conference_call_period(args["company_id"], args["time_period"])
    elif fn_name == "search_chunks":
        # Provide defaults if parameters are missing
        query = args.get("query", "")
        k = int(args.get("k", 5))
        company_name = args.get("company_name", "")
        statement_type = args.get("statement_type", "")
        time_period = args.get("time_period", LATEST_TIME_PERIOD)
        print(f"[llm_router] Searching chunks with query: {query}, k: {k}, company_name: {company_name}, statement_type: {statement_type}, time_period: {time_period}")
        return {"test": "test"}  # Debug return, remove in production
        return search_chunks(query, k, company_name, statement_type, time_period)
    else:
        return {"error": f"Unknown function: {fn_name}"}

# --- Main Chat Endpoint ---
@router.post("/")
async def chat(request: Request):
    try:
        print("[llm_router] Received POST request at chat endpoint.")
        body = await request.json()
        user_query = body.get("query")
        session_id = body.get("session_id", "default")  # Use a real session/user id in production
        print(f"[llm_router] Received user query: {user_query} (session: {session_id})")

        supported_sectors = ", ".join(sorted(SECTOR_MAP.values()))
        supported_companies = ", ".join(sorted(COMPANIES_MAP.values()))
        supported_financial_statements = ", ".join(sorted(FINANCIAL_STATEMENTS.values()))

        system_prompt = (
            "You are Saras, an expert assistant for the Indian Financial Market. "
            "Your job is to provide accurate, clear, and well-structured answers to user queries about Indian companies, sectors, and financial statements. "
            "Always use the available API tools to fetch data—never make up information or speculate. "
            f"Supported sectors: {supported_sectors}\n"
            f"Supported companies: {supported_companies}\n"
            f"Supported financial statements: {supported_financial_statements}\n"
            "If a user asks about an unsupported sector, company, or financial statement, reply: "
            "'Sector or Company or Financial Statement Not Found. Please specify a supported sector or company or financial statement.' "
            "Always mention the supported sectors, companies, and financial statements in your response if the user's query is unclear or unsupported. "
            "Format all responses in markdown for readability: use bullet points, headers, bold text, and whitespace for clarity. "
            "Explain your reasoning step by step, and cite the data source (API) when presenting results."
        )

        if USE_GEMINI:
            print("[llm_router] Using Gemini model.")
            # Gemini Function Declarations
            function_decls = [
                types.FunctionDeclaration(
                    name=tool["function"]["name"],
                    description=tool["function"].get("description", ""),
                    parameters=tool["function"].get("parameters", {})
                )
                for tool in tools if tool.get("type") == "function"
            ]
            print(f"[llm_router] Gemini function declarations: {function_decls}")

            contents_gemini = [
                types.Content(
                role="user", parts=[types.Part(text="user_query")]
                )
            ]

            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents_gemini,
                config=types.GenerateContentConfig(
                    system_instruction = system_prompt, 
                    tools=[types.Tool(function_declarations=function_decls)],
                    max_output_tokens=3000,
                    )   
            )
            print(f"[llm_router] Gemini response: {response}")

            if response.candidates[0].content.parts[0].function_call:
                call = response.candidates[0].content.parts[0].function_call
                # Default 'query' to original user query if missing
                if call.name == "search_chunks":
                    call.args.setdefault("query", user_query)
                print(f"[llm_router] Gemini function call: {call}")
                fn_name = call.name
                args = call.args
                tool_result = get_function_result(fn_name, args)
                print(f"[llm_router] Gemini tool result: {tool_result}")

                function_response_part = types.Part.from_function_response(
                    name=call.name,
                    response={"result": tool_result},
                )
                
                contents_gemini.append(response.candidates[0].content) # Append the content from the model's response.
                contents_gemini.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

                final = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents_gemini,
                    config=types.GenerateContentConfig(
                        system_instruction = system_prompt, 
                        tools=[types.Tool(function_declarations=function_decls)],
                        max_output_tokens=3000,
                    )
                )
                print(f"[llm_router] Gemini final response: {final.text}")
                return {"response": final.text}
            else:
                print(f"[llm_router] Gemini no function call, response: {response.text}")
                return {"response": response.text}

        else:
            print("[llm_router] Using OpenAI model.")
            # Retrieve chat history for this session
            history = get_chat_history(session_id)
            # Always start with system prompt
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
            #print(f"[llm_router] OpenAI messages: {messages}")

            first_response = openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            print(f"[llm_router] OpenAI first response:")

            msg = first_response.choices[0].message
            #print(f"[llm_router] OpenAI message: {msg}")
            # Add user message to history
            add_to_chat_history(session_id, {"role": "user", "content": user_query})

            if msg.tool_calls:
                tool_messages = []
                for tool_call in msg.tool_calls:
                    print(f"[llm_router] OpenAI tool call: {tool_call}")
                    fn_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    # Default 'query' to original user query if missing
                    if fn_name == "search_chunks":
                        args.setdefault("query", user_query)
                    tool_result = get_function_result(fn_name, args)
                    print(f"[llm_router] OpenAI tool result")
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fn_name,
                        "content": json.dumps(tool_result)
                    })

                # For the second call, reconstruct messages so the assistant tool_call is right before the tool messages
                second_messages = (
                    [{"role": "system", "content": system_prompt}]
                    + get_chat_history(session_id)
                    + [
                        {"role": "assistant", "tool_calls": msg.tool_calls},
                        *tool_messages
                    ]
                )
                print(f"[llm_router] OpenAI second messages: {second_messages}")
                second_response = openai_client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=second_messages
                )
                print(f"[llm_router] OpenAI second response:")
                final_content = second_response.choices[0].message.content
                print(f"[llm_router] OpenAI final message content: {final_content}")
                # Add assistant final response to history
                add_to_chat_history(session_id, {"role": "assistant", "content": final_content})
                return {"response": final_content}
            else:
                #print(f"[llm_router] OpenAI no tool call, message content: {msg.content}")
                add_to_chat_history(session_id, {"role": "assistant", "content": msg.content})
                return {"response": msg.content}
    except Exception as e:
        print(f"[llm_router] Unexpected error in chat endpoint: {e}")
        return {"response": f"An error occurred: {e}"}