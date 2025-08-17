"""
llm_router.py
Router for handling LLM-based chat focused on Conference Call data.
Supports OpenAI and Gemini tool-calling to query the latest API endpoints.
"""

# --- Imports ---
import os
import json
from fastapi import APIRouter, Request
from openai import OpenAI
from dotenv import load_dotenv

 

from app.tools import tools
from app.services.financial_data import (
    get_companies_with_conference_calls,
    get_conference_call_details,
    get_conference_call_summary,
    conference_call_qa,
)

# --- Configuration & Setup ---
print("[llm_router] Loading environment variables...")
load_dotenv(dotenv_path="app/.env")

router = APIRouter()
openai_client = OpenAI()

# --- Config ---

# Simple in-memory store for chat history (keyed by user/session)
chat_histories = {}

def get_chat_history(session_id):
    return chat_histories.get(session_id, [])

def add_to_chat_history(session_id, message):
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append(message)

def get_function_result(fn_name, args):
    print(f"[llm_router] Calling function: {fn_name} with args: {args}")
    if fn_name == "get_companies_with_conference_calls":
        return get_companies_with_conference_calls()
    elif fn_name == "get_conference_call_details":
        return get_conference_call_details(int(args["company_id"]))
    elif fn_name == "get_conference_call_summary":
        return get_conference_call_summary(int(args["company_id"]), int(args["fiscal_year"]), int(args["fiscal_quarter"]))
    elif fn_name == "conference_call_qa":
        # Default k to 3 if not supplied
        k = int(args.get("k", 3))
        return conference_call_qa(int(args["company_id"]), int(args["fiscal_year"]), int(args["fiscal_quarter"]), str(args.get("question", "")), k)
    else:
        return {"error": f"Unknown function: {fn_name}"}

# --- Main Chat Endpoint ---
@router.post("")
@router.post("/")
async def chat(request: Request):
    try:
        print("[llm_router] Received POST request at chat endpoint.")
        body = await request.json()
        user_query = body.get("query")
        session_id = body.get("session_id", "default")  # Use a real session/user id in production
        print(f"[llm_router] Received user query: {user_query} (session: {session_id})")

        system_prompt = (
            "You are Saras, an assistant focused on Indian company Conference Calls.\n"
            "You are currently equipped with the capabilities to answer questions about conference calls for Indian companies, and nothing more.\n"
            "Users can either ask you to summarise a conference call entirely, or ask specific questions about the call, or even compare multiple conference calls.\n"
            "Use the available tools to: (1) list companies with conference calls, (2) fetch a company's available call periods, "
            "(3) get the summary of a specific call, and (4) answer questions about a specific call (top-k evidence).\n"
            "Rules: Always call tools to fetch factual data; do not invent data. If required identifiers (company_id, fiscal_year, fiscal_quarter) are missing, "
            "ask a brief clarifying question or first call a tool that helps the user choose (e.g., list companies or periods).\n"
            "Format answers in concise markdown: headings, bullet points, and include the API source when applicable."
        )
        print("[llm_router] Using OpenAI model.")
        # Retrieve chat history for this session
        history = get_chat_history(session_id)
        # Always start with system prompt
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
        #print(f"[llm_router] OpenAI messages: {messages}")

        first_response = openai_client.chat.completions.create(
            model="gpt-5-mini",
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
                # Default question to original user query if missing for QA
                if fn_name == "conference_call_qa":
                    args.setdefault("question", user_query)
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
                model="gpt-5-mini",
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