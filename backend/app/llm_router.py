from fastapi import APIRouter, Request
from openai import OpenAI
from app.tools import tools
from app.services.financial_data import get_historical_financials
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

@router.post("/")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("query")
    print(f"Received user query: {user_query}")
    # Step 1: Send user query to GPT-4o with tools
    first_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_query}],
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

        if fn_name == "get_historical_financials":
            result = get_historical_financials(args["sector"], args["years"])
            print(f"Tool result: {result}")
            # Step 3: Send result back to GPT-4o for final answer
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
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
