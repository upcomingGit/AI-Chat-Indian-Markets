from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Allow frontend access (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(req: ChatRequest):
    query = req.query.lower()
    print(f"Received query: {query}")
    # Placeholder: replace this with OpenAI + SQL logic later
    if "revenue" in query:
        return {"answer": "The company's revenue for FY2023 was ₹12,345 crore."}
    elif "profit" in query:
        return {"answer": "The net profit for FY2023 was ₹2,300 crore."}
    else:
        return {"answer": "I'm still learning how to fetch that. Try asking about revenue or profit!"}
