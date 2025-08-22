"""
llm_router.py
Router for handling LLM-based chat focused on Conference Call data.
Supports OpenAI and Gemini tool-calling to query the latest API endpoints.

Situations to cater to:
-> Multiple agents being called in one query
"""

# --- Imports ---
import os
import json
from fastapi import APIRouter, Request
from openai import OpenAI
import threading
from dotenv import load_dotenv
from tools import tools

from agents.conference_call_agent import ConferenceCallAgent
from agents.financial_statements_agent import FinancialStatementsAgent
from agents.news_agent import NewsAgent
from agents.market_data_agent import MarketDataAgent
from agents.company_kb_agent import CompanyKBAgent
from agents.company_disclosures_agent import CompanyDisclosuresAgent
from agents.registry import registry


# --- Configuration & Setup ---
print("[llm_router] Loading environment variables...")
load_dotenv(dotenv_path=".env")

router = APIRouter()
openai_client = OpenAI()

# Register all agents here
print("[llm_router] Registering agents...")
registry.register("conference_call", ConferenceCallAgent())
registry.register("financial_statements", FinancialStatementsAgent())
registry.register("news", NewsAgent())
registry.register("market_data", MarketDataAgent())
registry.register("company_kb", CompanyKBAgent())
registry.register("company_disclosures", CompanyDisclosuresAgent())
print("[llm_router] Agents registered.")


# --- In-memory per-session chat histories ---
# Keeps the most recent N messages (user + assistant) per session in memory only.
chat_histories = {}
chat_histories_lock = threading.Lock()
HISTORY_LIMIT = 20


def get_chat_history(session_id: str):
    """Return a copy of the chat history list for the given session id.

    Each message is a dict: {"role": "user"|"assistant", "content": str}
    """
    with chat_histories_lock:
        return list(chat_histories.get(session_id, []))


def add_to_chat_history(session_id: str, message: dict):
    """Append a message to the session history and trim to the most recent HISTORY_LIMIT messages."""
    if not isinstance(message, dict) or "role" not in message or "content" not in message:
        return
    with chat_histories_lock:
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append(message)
        # Trim to last HISTORY_LIMIT messages
        if len(chat_histories[session_id]) > HISTORY_LIMIT:
            chat_histories[session_id] = chat_histories[session_id][-HISTORY_LIMIT:]


@router.post("/reset")
@router.post("/session/reset")
async def reset_session(request: Request):
    """Clear the in-memory history for a given session_id.

    Body: {"session_id": "..."}
    Returns: {"status": "ok", "cleared": bool}
    """
    try:
        body = await request.json()
        session_id = str(body.get("session_id", "default"))
        with chat_histories_lock:
            existed = session_id in chat_histories
            if existed:
                del chat_histories[session_id]
        print(f"[llm_router] Cleared session history for {session_id}: existed={existed}")
        return {"status": "ok", "cleared": existed}
    except Exception as e:
        print(f"[llm_router] Error clearing session: {e}")
        return {"status": "error", "error": str(e)}


def choose_agent_via_llm(user_query: str, session_id: str = None):
    """Ask the LLM to pick an agent from the registry for the given user_query.

    Returns a dict: {"agent": "registry_name", "reason": "..."}
    If selection fails, returns None.
    """
    try:
        agents_map = registry.list_agents()
        print(f"[llm_router] Available agents for selection: {agents_map}")

        # Load routing knowledge base if available
        kb_text = ""
        kb_path = os.path.join(os.path.dirname(__file__), "agent_routing_knowledge.md")
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_text = f.read()
                print("[llm_router] Loaded agent routing knowledge base for prompt.")
        except Exception:
            print("[llm_router] No agent routing knowledge base found; proceeding without it.")

        system_prompt = (
            "You are an assistant that selects the best specialised agent to handle a user's query."
            " Respond only with valid JSON in the format: {\"agent\": \"registry_name\", \"reason\": \"why\"}."
            " If you are unsure, return agent as null.\n\n"
            + (kb_text or "")
        )

        agent_list_text = "\n".join([f"- {name}: {clsname}" for name, clsname in agents_map.items()])
        user_prompt = (
            f"Available agents:\n{agent_list_text}\n\n"
            f"User query: \"{user_query}\"\n\n"
            "Choose the single most appropriate agent and return the JSON object as described."
        )

        # Build messages: system prompt, optional recent session history, then the user prompt
        messages = [{"role": "system", "content": system_prompt}]
        if session_id:
            history_msgs = get_chat_history(session_id)
            if history_msgs:
                print(f"[llm_router] Including {len(history_msgs)} history messages from session {session_id} in agent selection prompt")
                # history_msgs are already in {role, content} format
                messages.extend(history_msgs)

        messages.append({"role": "user", "content": user_prompt})

        resp = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        choice_msg = resp.choices[0].message.content
        print(f"[llm_router] Agent selection raw response: {choice_msg}")

        # Parse JSON from the model output; be permissive
        try:
            parsed = json.loads(choice_msg)
            return parsed
        except Exception:
            # try to extract first JSON substring
            start = choice_msg.find('{')
            end = choice_msg.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(choice_msg[start:end+1])
                    return parsed
                except Exception as e:
                    print(f"[llm_router] Failed parsing JSON substring: {e}")
        return None
    except Exception as e:
        print(f"[llm_router] Error when asking LLM to choose agent: {e}")
        return None

# --- Main Chat Endpoint ---

@router.post("")
@router.post("/")
async def chat_endpoint(request: Request):
    try:
        print("[llm_router] Received POST request at chat endpoint.")
        body = await request.json()
        user_query = body.get("query")
        session_id = str(body.get("session_id", "default"))  # Use a real session/user id in production
        print(f"[llm_router] Received user query: {user_query} (session: {session_id})")

        # Record user message into session history (will be trimmed to HISTORY_LIMIT)
        add_to_chat_history(session_id, {"role": "user", "content": user_query})

        # Ask LLM to choose an agent (include session history)
        selection = choose_agent_via_llm(user_query, session_id)
        print(f"[llm_router] Agent selection result: {selection}")

        response = None
        if selection and isinstance(selection, dict):
            agent_name = selection.get("agent")
            reason = selection.get("reason")
            print(f"[llm_router] LLM selected agent: {agent_name} (reason: {reason})")

            # If LLM explicitly returned null/None for agent, treat 'reason' as a clarifying question
            if agent_name is None:
                if reason:
                    print(f"[llm_router] LLM requested clarification: {reason}")
                    # Save assistant clarifying question and return
                    add_to_chat_history(session_id, {"role": "assistant", "content": reason})
                    return {"response": reason}
                else:
                    print("[llm_router] LLM returned null agent without reason; falling back to default routing")

            if agent_name and registry.get(agent_name):
                agent = registry.get(agent_name)
                print(f"[llm_router] Routing to agent '{agent_name}' -> {agent.__class__.__name__}")
                try:
                    response = agent.handle(user_query)
                except TypeError:
                    # fallback to just passing the query
                    response = agent.handle(user_query)
            else:
                print(f"[llm_router] Selected agent '{agent_name}' not found in registry; falling back to default routing")

        if response is None:
            # fallback: let registry find a matching agent by can_handle
            print("[llm_router] Falling back to registry.route_query")
            response = registry.route_query(user_query)

        # Save assistant response into session history
        add_to_chat_history(session_id, {"role": "assistant", "content": response})

        print(f"[llm_router] Response from agent: {response}")
        return {"response": response}

    except Exception as e:
        print(f"[llm_router] Unexpected error in chat endpoint: {e}")
        return {"response": f"An error occurred: {e}"}

'''
from core.financial_data import (
    get_companies_with_conference_calls,
    get_conference_call_details,
    get_conference_call_summary,
    conference_call_qa,
)

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
    # Retrieve chat history for this session and include it so assistant gets multi-turn context
    history = get_chat_history(session_id)
    # Always start with system prompt; history already contains role/content entries
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
'''